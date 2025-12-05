"""
Unified Sentiment Analysis Module for National Activity Indicator System.

Provides multiple sentiment analysis backends:
- VADER (fast, rule-based, no GPU required)
- Transformers (accurate, deep learning based)

Usage:
    # Quick analysis with VADER (default)
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("Great economic growth reported today!")
    
    # Deep learning analysis
    analyzer = SentimentAnalyzer(backend='transformers')
    result = analyzer.analyze("Market crash fears grow among investors")
    
    # Batch processing
    results = analyzer.analyze_batch(["Text 1", "Text 2", "Text 3"])
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import time


class SentimentLabel(str, Enum):
    """Sentiment classification labels"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class SentimentResult:
    """
    Structured sentiment analysis result.
    
    Attributes:
        score: Normalized score from -1.0 (negative) to +1.0 (positive)
        score_normalized: Score normalized to 0-100 scale
        label: Categorical sentiment label
        confidence: Model confidence (0.0 to 1.0)
        compound: Raw compound score (VADER) or model score
        positive: Positive component score
        negative: Negative component score
        neutral: Neutral component score
        processing_time_ms: Time taken for analysis
        backend: Which backend was used
    """
    score: float  # -1.0 to +1.0
    score_normalized: float  # 0 to 100
    label: SentimentLabel
    confidence: float = 1.0
    compound: float = 0.0
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 0.0
    processing_time_ms: float = 0.0
    backend: str = "vader"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "score": self.score,
            "score_normalized": self.score_normalized,
            "label": self.label.value,
            "confidence": self.confidence,
            "compound": self.compound,
            "positive": self.positive,
            "negative": self.negative,
            "neutral": self.neutral,
            "processing_time_ms": self.processing_time_ms,
            "backend": self.backend
        }


class BaseSentimentBackend(ABC):
    """Abstract base class for sentiment analysis backends"""
    
    @abstractmethod
    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text"""
        pass
    
    @abstractmethod
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze sentiment of multiple texts"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Backend name"""
        pass


class VaderBackend(BaseSentimentBackend):
    """
    NLTK VADER sentiment analyzer backend.
    
    Fast, rule-based sentiment analysis optimized for social media text.
    No GPU required.
    """
    
    def __init__(self):
        import nltk
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
        
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        self._analyzer = SentimentIntensityAnalyzer()
    
    @property
    def name(self) -> str:
        return "vader"
    
    def _score_to_label(self, compound: float) -> SentimentLabel:
        """Convert compound score to categorical label"""
        if compound >= 0.5:
            return SentimentLabel.VERY_POSITIVE
        elif compound >= 0.05:
            return SentimentLabel.POSITIVE
        elif compound <= -0.5:
            return SentimentLabel.VERY_NEGATIVE
        elif compound <= -0.05:
            return SentimentLabel.NEGATIVE
        else:
            return SentimentLabel.NEUTRAL
    
    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment using VADER"""
        start = time.time()
        
        if not text or not text.strip():
            return SentimentResult(
                score=0.0,
                score_normalized=50.0,
                label=SentimentLabel.NEUTRAL,
                confidence=0.0,
                processing_time_ms=0.0,
                backend=self.name
            )
        
        scores = self._analyzer.polarity_scores(text)
        compound = scores['compound']
        
        # Calculate confidence based on how extreme the score is
        confidence = abs(compound)
        
        processing_time = (time.time() - start) * 1000
        
        return SentimentResult(
            score=compound,
            score_normalized=((compound + 1) / 2) * 100,
            label=self._score_to_label(compound),
            confidence=confidence,
            compound=compound,
            positive=scores['pos'],
            negative=scores['neg'],
            neutral=scores['neu'],
            processing_time_ms=processing_time,
            backend=self.name
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze multiple texts (sequential for VADER)"""
        return [self.analyze(text) for text in texts]


class TransformersBackend(BaseSentimentBackend):
    """
    Hugging Face Transformers sentiment analyzer backend.
    
    Uses DistilBERT fine-tuned on SST-2 for accurate sentiment classification.
    Supports GPU acceleration.
    """
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english",
                 use_gpu: bool = True, max_length: int = 512):
        self._model_name = model_name
        self._max_length = max_length
        self._pipeline = None
        self._use_gpu = use_gpu
        self._load_model()
    
    def _load_model(self):
        """Lazy load the transformer model"""
        if self._pipeline is None:
            from transformers import pipeline
            import torch
            
            device = 0 if self._use_gpu and torch.cuda.is_available() else -1
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self._model_name,
                device=device,
                truncation=True,
                max_length=self._max_length
            )
    
    @property
    def name(self) -> str:
        return "transformers"
    
    def _result_to_score(self, result: Dict) -> float:
        """Convert pipeline result to -1 to +1 score"""
        label = result['label']
        score = result['score']
        
        if label == 'POSITIVE':
            return score
        elif label == 'NEGATIVE':
            return -score
        else:
            return 0.0
    
    def _score_to_label(self, score: float, confidence: float) -> SentimentLabel:
        """Convert score to categorical label"""
        if confidence < 0.6:
            return SentimentLabel.NEUTRAL
        
        if score >= 0.5:
            return SentimentLabel.VERY_POSITIVE
        elif score > 0:
            return SentimentLabel.POSITIVE
        elif score <= -0.5:
            return SentimentLabel.VERY_NEGATIVE
        elif score < 0:
            return SentimentLabel.NEGATIVE
        else:
            return SentimentLabel.NEUTRAL
    
    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment using Transformers"""
        start = time.time()
        
        if not text or not text.strip():
            return SentimentResult(
                score=0.0,
                score_normalized=50.0,
                label=SentimentLabel.NEUTRAL,
                confidence=0.0,
                processing_time_ms=0.0,
                backend=self.name
            )
        
        # Truncate to max length
        text = text[:self._max_length * 4]  # Rough char estimate
        
        result = self._pipeline(text)[0]
        score = self._result_to_score(result)
        confidence = result['score']
        
        processing_time = (time.time() - start) * 1000
        
        return SentimentResult(
            score=score,
            score_normalized=((score + 1) / 2) * 100,
            label=self._score_to_label(score, confidence),
            confidence=confidence,
            compound=score,
            positive=max(0, score),
            negative=abs(min(0, score)),
            neutral=1 - confidence,
            processing_time_ms=processing_time,
            backend=self.name
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze multiple texts efficiently using batching"""
        if not texts:
            return []
        
        start = time.time()
        
        # Filter empty texts
        valid_indices = [i for i, t in enumerate(texts) if t and t.strip()]
        valid_texts = [texts[i][:self._max_length * 4] for i in valid_indices]
        
        if not valid_texts:
            return [SentimentResult(
                score=0.0, score_normalized=50.0, label=SentimentLabel.NEUTRAL,
                confidence=0.0, processing_time_ms=0.0, backend=self.name
            ) for _ in texts]
        
        # Batch inference
        results = self._pipeline(valid_texts)
        
        total_time = (time.time() - start) * 1000
        per_text_time = total_time / len(valid_texts)
        
        # Build full results list
        sentiment_results = []
        result_idx = 0
        
        for i in range(len(texts)):
            if i in valid_indices:
                result = results[result_idx]
                score = self._result_to_score(result)
                confidence = result['score']
                
                sentiment_results.append(SentimentResult(
                    score=score,
                    score_normalized=((score + 1) / 2) * 100,
                    label=self._score_to_label(score, confidence),
                    confidence=confidence,
                    compound=score,
                    positive=max(0, score),
                    negative=abs(min(0, score)),
                    neutral=1 - confidence,
                    processing_time_ms=per_text_time,
                    backend=self.name
                ))
                result_idx += 1
            else:
                sentiment_results.append(SentimentResult(
                    score=0.0, score_normalized=50.0, label=SentimentLabel.NEUTRAL,
                    confidence=0.0, processing_time_ms=0.0, backend=self.name
                ))
        
        return sentiment_results


class SentimentAnalyzer:
    """
    Unified Sentiment Analyzer with multiple backend support.
    
    Args:
        backend: Which backend to use ('vader' or 'transformers')
        use_gpu: Whether to use GPU for transformers backend
        model_name: Model name for transformers backend
    
    Examples:
        >>> analyzer = SentimentAnalyzer()
        >>> result = analyzer.analyze("Great news for the economy!")
        >>> print(f"Score: {result.score:.2f}, Label: {result.label.value}")
        Score: 0.73, Label: positive
        
        >>> analyzer = SentimentAnalyzer(backend='transformers')
        >>> results = analyzer.analyze_batch(["Good news", "Bad news"])
    """
    
    _instance_cache: Dict[str, 'SentimentAnalyzer'] = {}
    
    def __init__(self, backend: str = 'vader', use_gpu: bool = True,
                 model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        self._backend_name = backend.lower()
        
        if self._backend_name == 'vader':
            self._backend = VaderBackend()
        elif self._backend_name in ('transformers', 'transformer', 'bert', 'distilbert'):
            self._backend = TransformersBackend(
                model_name=model_name,
                use_gpu=use_gpu
            )
        else:
            raise ValueError(f"Unknown backend: {backend}. Use 'vader' or 'transformers'")
    
    @classmethod
    def get_instance(cls, backend: str = 'vader', **kwargs) -> 'SentimentAnalyzer':
        """Get or create a cached instance (singleton pattern per backend)"""
        if backend not in cls._instance_cache:
            cls._instance_cache[backend] = cls(backend=backend, **kwargs)
        return cls._instance_cache[backend]
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with score, label, and details
        """
        return self._backend.analyze(text)
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze sentiment of multiple texts efficiently.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of SentimentResult objects
        """
        return self._backend.analyze_batch(texts)
    
    def analyze_article(self, article: Dict[str, Any], 
                        analyze_title: bool = True,
                        analyze_body: bool = True) -> Dict[str, SentimentResult]:
        """
        Analyze sentiment of an article's components.
        
        Args:
            article: Article dict with 'content' containing 'title' and 'body'
            analyze_title: Whether to analyze title separately
            analyze_body: Whether to analyze body
            
        Returns:
            Dict with 'title', 'body', and 'overall' sentiment results
        """
        content = article.get('content', {})
        if isinstance(content, str):
            # Handle case where content is just a string
            body = content
            title = article.get('title', '')
        else:
            title = content.get('title', article.get('title', ''))
            body = content.get('body', content.get('text', ''))
        
        results = {}
        
        if analyze_title and title:
            results['title'] = self.analyze(title)
        
        if analyze_body and body:
            results['body'] = self.analyze(body)
        
        # Calculate overall (weighted: title 30%, body 70%)
        if 'title' in results and 'body' in results:
            overall_score = 0.3 * results['title'].score + 0.7 * results['body'].score
            overall_confidence = 0.3 * results['title'].confidence + 0.7 * results['body'].confidence
        elif 'body' in results:
            overall_score = results['body'].score
            overall_confidence = results['body'].confidence
        elif 'title' in results:
            overall_score = results['title'].score
            overall_confidence = results['title'].confidence
        else:
            overall_score = 0.0
            overall_confidence = 0.0
        
        results['overall'] = SentimentResult(
            score=overall_score,
            score_normalized=((overall_score + 1) / 2) * 100,
            label=self._score_to_label(overall_score),
            confidence=overall_confidence,
            compound=overall_score,
            backend=self._backend.name
        )
        
        return results
    
    def _score_to_label(self, score: float) -> SentimentLabel:
        """Convert score to label"""
        if score >= 0.5:
            return SentimentLabel.VERY_POSITIVE
        elif score >= 0.05:
            return SentimentLabel.POSITIVE
        elif score <= -0.5:
            return SentimentLabel.VERY_NEGATIVE
        elif score <= -0.05:
            return SentimentLabel.NEGATIVE
        else:
            return SentimentLabel.NEUTRAL
    
    def get_aggregate_sentiment(self, articles: List[Dict[str, Any]],
                                 weight_by_credibility: bool = True) -> SentimentResult:
        """
        Calculate aggregate sentiment across multiple articles.
        
        Args:
            articles: List of article dicts
            weight_by_credibility: Whether to weight by source credibility
            
        Returns:
            Aggregated SentimentResult
        """
        if not articles:
            return SentimentResult(
                score=0.0,
                score_normalized=50.0,
                label=SentimentLabel.NEUTRAL,
                confidence=0.0,
                backend=self._backend.name
            )
        
        start = time.time()
        
        total_score = 0.0
        total_weight = 0.0
        all_positive = 0.0
        all_negative = 0.0
        all_neutral = 0.0
        
        for article in articles:
            result = self.analyze_article(article)['overall']
            
            if weight_by_credibility:
                metadata = article.get('metadata', {})
                weight = metadata.get('source_credibility', 0.5)
            else:
                weight = 1.0
            
            total_score += result.score * weight
            total_weight += weight
            all_positive += result.positive * weight
            all_negative += result.negative * weight
            all_neutral += result.neutral * weight
        
        if total_weight > 0:
            avg_score = total_score / total_weight
            avg_positive = all_positive / total_weight
            avg_negative = all_negative / total_weight
            avg_neutral = all_neutral / total_weight
        else:
            avg_score = 0.0
            avg_positive = 0.0
            avg_negative = 0.0
            avg_neutral = 1.0
        
        processing_time = (time.time() - start) * 1000
        
        return SentimentResult(
            score=avg_score,
            score_normalized=((avg_score + 1) / 2) * 100,
            label=self._score_to_label(avg_score),
            confidence=abs(avg_score),
            compound=avg_score,
            positive=avg_positive,
            negative=avg_negative,
            neutral=avg_neutral,
            processing_time_ms=processing_time,
            backend=self._backend.name
        )
    
    @property
    def backend_name(self) -> str:
        """Get the name of the current backend"""
        return self._backend.name


# Convenience functions for quick access
def analyze_sentiment(text: str, backend: str = 'vader') -> SentimentResult:
    """Quick sentiment analysis of a single text"""
    return SentimentAnalyzer.get_instance(backend).analyze(text)


def analyze_sentiment_batch(texts: List[str], backend: str = 'vader') -> List[SentimentResult]:
    """Quick batch sentiment analysis"""
    return SentimentAnalyzer.get_instance(backend).analyze_batch(texts)


if __name__ == '__main__':
    # Demo/test
    print("=" * 60)
    print("SENTIMENT ANALYZER DEMO")
    print("=" * 60)
    
    test_texts = [
        "Great economic growth reported today! Investors are thrilled.",
        "Market crash fears grow as inflation spirals out of control.",
        "Weather update: Sunny skies expected tomorrow.",
        "Protesters clash with police in downtown area. Situation critical.",
        "New trade agreement brings hope for export sector."
    ]
    
    print("\n📊 VADER Backend (Fast)")
    print("-" * 40)
    analyzer_vader = SentimentAnalyzer(backend='vader')
    
    for text in test_texts:
        result = analyzer_vader.analyze(text)
        print(f"Score: {result.score:+.2f} | {result.label.value:15} | {text[:50]}...")
    
    print("\n📊 Batch Processing Test")
    print("-" * 40)
    results = analyzer_vader.analyze_batch(test_texts)
    avg_score = sum(r.score for r in results) / len(results)
    print(f"Average sentiment across {len(results)} texts: {avg_score:+.2f}")
    
    print("\n✅ Sentiment Analyzer ready for integration!")
