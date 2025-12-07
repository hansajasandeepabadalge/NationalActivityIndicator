"""
Advanced Multi-Dimensional Sentiment Analysis Service

This module provides sophisticated sentiment analysis using Groq's Llama 3.1 70B.
It extends the existing SentimentAnalyzer with:
- 4 sentiment dimensions: overall, business confidence, public mood, economic outlook
- Sentiment drivers identification
- Tone and emotion analysis
- Temporal sentiment trends

Falls back to basic SentimentAnalyzer if LLM is unavailable.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

from .llm_base import GroqLLMClient, LLMConfig, CacheConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Sentiment Models
# ============================================================================

class SentimentLevel(str, Enum):
    """Sentiment level classification."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    SLIGHTLY_POSITIVE = "slightly_positive"
    NEUTRAL = "neutral"
    SLIGHTLY_NEGATIVE = "slightly_negative"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class EmotionType(str, Enum):
    """Primary emotion types detected in text."""
    JOY = "joy"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    SURPRISE = "surprise"
    FEAR = "fear"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    NEUTRAL = "neutral"


class ToneType(str, Enum):
    """Writing tone classification."""
    OBJECTIVE = "objective"
    ANALYTICAL = "analytical"
    CAUTIONARY = "cautionary"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    URGENT = "urgent"
    REASSURING = "reassuring"
    CRITICAL = "critical"


# Pydantic models for structured LLM output
class SentimentDimension(BaseModel):
    """Single sentiment dimension analysis."""
    score: float = Field(ge=-1.0, le=1.0, description="Sentiment score from -1 (very negative) to +1 (very positive)")
    level: str = Field(description="Sentiment level label")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this assessment")
    reasoning: str = Field(default="", description="Brief reasoning")


class SentimentDriver(BaseModel):
    """A factor driving sentiment in a particular direction."""
    factor: str = Field(description="The sentiment-driving factor")
    direction: str = Field(description="positive or negative")
    strength: float = Field(ge=0.0, le=1.0, description="Strength of this driver")
    quote: str = Field(default="", description="Supporting quote from text")


class LLMSentimentResult(BaseModel):
    """Complete LLM sentiment response structure."""
    overall: SentimentDimension
    business_confidence: SentimentDimension
    public_mood: SentimentDimension  
    economic_outlook: SentimentDimension
    
    primary_emotion: str = Field(default="neutral", description="Primary emotion detected")
    secondary_emotions: List[str] = Field(default_factory=list, description="Secondary emotions")
    tone: str = Field(default="objective", description="Writing tone")
    
    drivers: List[SentimentDriver] = Field(default_factory=list, description="Sentiment drivers")
    
    summary: str = Field(default="", description="Brief sentiment summary")


# ============================================================================
# Sentiment Result Dataclass
# ============================================================================

@dataclass
class AdvancedSentimentResult:
    """
    Enhanced multi-dimensional sentiment analysis result.
    
    Compatible with existing SentimentAnalyzer output but with additional dimensions.
    """
    # Overall sentiment (legacy compatible)
    overall_score: float  # -1 to +1
    overall_level: SentimentLevel
    overall_confidence: float
    
    # Dimensional sentiments
    business_confidence_score: float = 0.0
    business_confidence_level: SentimentLevel = SentimentLevel.NEUTRAL
    
    public_mood_score: float = 0.0
    public_mood_level: SentimentLevel = SentimentLevel.NEUTRAL
    
    economic_outlook_score: float = 0.0
    economic_outlook_level: SentimentLevel = SentimentLevel.NEUTRAL
    
    # Emotions and tone
    primary_emotion: EmotionType = EmotionType.NEUTRAL
    secondary_emotions: List[EmotionType] = field(default_factory=list)
    tone: ToneType = ToneType.OBJECTIVE
    
    # Sentiment drivers
    positive_drivers: List[Dict[str, Any]] = field(default_factory=list)
    negative_drivers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    summary: str = ""
    analysis_source: str = "llm"  # "llm" or "basic_fallback"
    processing_time_ms: float = 0.0
    cached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "overall": {
                "score": self.overall_score,
                "level": self.overall_level.value,
                "confidence": self.overall_confidence
            },
            "dimensions": {
                "business_confidence": {
                    "score": self.business_confidence_score,
                    "level": self.business_confidence_level.value
                },
                "public_mood": {
                    "score": self.public_mood_score,
                    "level": self.public_mood_level.value
                },
                "economic_outlook": {
                    "score": self.economic_outlook_score,
                    "level": self.economic_outlook_level.value
                }
            },
            "emotions": {
                "primary": self.primary_emotion.value,
                "secondary": [e.value for e in self.secondary_emotions]
            },
            "tone": self.tone.value,
            "drivers": {
                "positive": self.positive_drivers,
                "negative": self.negative_drivers
            },
            "summary": self.summary,
            "analysis_source": self.analysis_source,
            "processing_time_ms": self.processing_time_ms,
            "cached": self.cached
        }
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Convert to legacy SentimentAnalyzer format for backward compatibility.
        """
        return {
            "score": self.overall_score,
            "label": self.overall_level.value,
            "confidence": self.overall_confidence
        }
    
    def get_composite_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate weighted composite sentiment score.
        
        Args:
            weights: Custom weights for each dimension
        
        Returns:
            Weighted composite score from -1 to +1
        """
        default_weights = {
            "overall": 0.3,
            "business_confidence": 0.25,
            "public_mood": 0.2,
            "economic_outlook": 0.25
        }
        weights = weights or default_weights
        
        return (
            weights.get("overall", 0.3) * self.overall_score +
            weights.get("business_confidence", 0.25) * self.business_confidence_score +
            weights.get("public_mood", 0.2) * self.public_mood_score +
            weights.get("economic_outlook", 0.25) * self.economic_outlook_score
        )


# ============================================================================
# Score to Level Mapping
# ============================================================================

def score_to_level(score: float) -> SentimentLevel:
    """Convert numeric score to SentimentLevel."""
    if score >= 0.6:
        return SentimentLevel.VERY_POSITIVE
    elif score >= 0.3:
        return SentimentLevel.POSITIVE
    elif score >= 0.1:
        return SentimentLevel.SLIGHTLY_POSITIVE
    elif score >= -0.1:
        return SentimentLevel.NEUTRAL
    elif score >= -0.3:
        return SentimentLevel.SLIGHTLY_NEGATIVE
    elif score >= -0.6:
        return SentimentLevel.NEGATIVE
    else:
        return SentimentLevel.VERY_NEGATIVE


def level_to_score(level: str) -> float:
    """Convert level string to approximate score."""
    level_scores = {
        "very_positive": 0.8,
        "positive": 0.5,
        "slightly_positive": 0.2,
        "neutral": 0.0,
        "slightly_negative": -0.2,
        "negative": -0.5,
        "very_negative": -0.8
    }
    return level_scores.get(level.lower(), 0.0)


# ============================================================================
# Advanced Sentiment Analyzer Service
# ============================================================================

class AdvancedSentimentAnalyzer:
    """
    LLM-powered multi-dimensional sentiment analyzer using Groq's Llama 3.1 70B.
    
    Features:
    - 4 sentiment dimensions for comprehensive analysis
    - Emotion and tone detection
    - Sentiment driver identification with quotes
    - Fallback to basic analyzer when needed
    - Response caching for efficiency
    
    Usage:
        analyzer = AdvancedSentimentAnalyzer()
        result = await analyzer.analyze("Article text here...")
    """
    
    ANALYSIS_PROMPT = """Analyze the sentiment of this article across multiple dimensions.

ARTICLE:
{article_text}

INSTRUCTIONS:
Provide a detailed sentiment analysis covering:

1. OVERALL SENTIMENT: The general sentiment of the article
   - Score: -1.0 (very negative) to +1.0 (very positive)
   - Level: very_negative, negative, slightly_negative, neutral, slightly_positive, positive, very_positive

2. BUSINESS CONFIDENCE: How does this affect business confidence and investment climate?
   - Consider: market stability, investment opportunities, business environment

3. PUBLIC MOOD: What is the public/social sentiment reflected?
   - Consider: citizen concerns, social stability, public opinion

4. ECONOMIC OUTLOOK: What does this imply for economic prospects?
   - Consider: growth expectations, inflation concerns, employment outlook

5. EMOTIONS: Identify the primary and secondary emotions
   - Options: joy, trust, anticipation, surprise, fear, sadness, disgust, anger, neutral

6. TONE: Classify the writing tone
   - Options: objective, analytical, cautionary, optimistic, pessimistic, urgent, reassuring, critical

7. SENTIMENT DRIVERS: List key factors driving sentiment
   - For each: factor name, direction (positive/negative), strength (0-1), supporting quote

Be precise and calibrated in your scores. Neutral articles should score near 0."""

    SYSTEM_PROMPT = """You are an expert sentiment analyst specializing in economic and political news.
Your analysis should be nuanced and multi-dimensional.
Consider the implications for different stakeholders: businesses, public, economy.
Be objective and avoid over-interpreting neutral content.
Provide evidence-based assessments with supporting quotes."""

    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        cache_config: Optional[CacheConfig] = None,
        fallback_analyzer: Optional[Any] = None,
        min_text_length: int = 50,
        skip_neutral_llm: bool = True
    ):
        """
        Initialize Advanced Sentiment Analyzer.
        
        Args:
            llm_config: LLM configuration
            cache_config: Cache configuration
            fallback_analyzer: Instance of basic SentimentAnalyzer for fallback
            min_text_length: Minimum text length to process
            skip_neutral_llm: Skip LLM for clearly neutral text (optimization)
        """
        self.llm_config = llm_config or LLMConfig()
        self.cache_config = cache_config or CacheConfig(prefix="sentiment_analyzer")
        self.llm_client = GroqLLMClient(self.llm_config, self.cache_config)
        self.fallback_analyzer = fallback_analyzer
        self.min_text_length = min_text_length
        self.skip_neutral_llm = skip_neutral_llm
        
        # Statistics
        self._total_analyses = 0
        self._llm_analyses = 0
        self._fallback_analyses = 0
        self._neutral_skips = 0
        self._errors = 0
    
    async def analyze(
        self,
        text: str,
        title: str = "",
        context: str = "",
        force_llm: bool = False
    ) -> AdvancedSentimentResult:
        """
        Analyze sentiment of text across multiple dimensions.
        
        Args:
            text: Article text content
            title: Article title (optional)
            context: Additional context (optional)
            force_llm: Force LLM usage
        
        Returns:
            AdvancedSentimentResult with full sentiment analysis
        """
        import time
        start_time = time.time()
        
        self._total_analyses += 1
        
        # Combine title and text
        full_text = f"{title}\n\n{text}" if title else text
        
        # Skip very short texts
        if len(full_text) < self.min_text_length:
            return self._create_neutral_result(start_time)
        
        # Quick neutral check (optimization)
        if not force_llm and self.skip_neutral_llm:
            quick_sentiment = self._quick_sentiment_check(full_text)
            if quick_sentiment is not None and abs(quick_sentiment) < 0.1:
                self._neutral_skips += 1
                return self._create_neutral_result(start_time, source="quick_check")
        
        try:
            # Truncate very long texts
            max_length = 3500
            if len(full_text) > max_length:
                full_text = full_text[:max_length] + "..."
            
            # Build prompt
            prompt = self.ANALYSIS_PROMPT.format(article_text=full_text)
            
            # Get LLM analysis
            response = await self.llm_client.generate_structured(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                response_model=LLMSentimentResult
            )
            
            # Convert to result
            result = self._parse_llm_response(response)
            result.processing_time_ms = (time.time() - start_time) * 1000
            
            self._llm_analyses += 1
            logger.info(
                f"LLM sentiment: overall={result.overall_score:.2f}, "
                f"business={result.business_confidence_score:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LLM sentiment analysis failed: {e}")
            self._errors += 1
            return await self._fallback_analyze(full_text, start_time)
    
    async def analyze_batch(
        self,
        texts: List[Dict[str, str]],
        concurrency: int = 5
    ) -> List[AdvancedSentimentResult]:
        """
        Analyze multiple texts concurrently.
        
        Args:
            texts: List of dicts with 'text', optional 'title', 'context'
            concurrency: Max concurrent analyses
        
        Returns:
            List of AdvancedSentimentResult objects
        """
        semaphore = asyncio.Semaphore(concurrency)
        
        async def analyze_with_limit(item: Dict[str, str]) -> AdvancedSentimentResult:
            async with semaphore:
                return await self.analyze(
                    text=item.get("text", ""),
                    title=item.get("title", ""),
                    context=item.get("context", "")
                )
        
        tasks = [analyze_with_limit(item) for item in texts]
        return await asyncio.gather(*tasks)
    
    def _quick_sentiment_check(self, text: str) -> Optional[float]:
        """
        Quick keyword-based sentiment check to skip LLM for neutral content.
        
        Returns approximate sentiment score or None if uncertain.
        """
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = [
            "growth", "increase", "improve", "success", "positive", "gain",
            "rise", "boost", "advance", "progress", "optimis", "confident"
        ]
        positive_count = sum(1 for w in positive_words if w in text_lower)
        
        # Negative indicators
        negative_words = [
            "decline", "decrease", "fall", "crisis", "concern", "risk",
            "worry", "drop", "loss", "negative", "fear", "uncertain"
        ]
        negative_count = sum(1 for w in negative_words if w in text_lower)
        
        # Calculate rough score
        total = positive_count + negative_count
        if total == 0:
            return 0.0  # Neutral
        
        score = (positive_count - negative_count) / max(total, 1) * 0.5
        
        # Only return if clearly neutral
        if abs(score) < 0.15 and total < 5:
            return score
        
        return None  # Uncertain, use LLM
    
    def _parse_llm_response(self, response: LLMSentimentResult) -> AdvancedSentimentResult:
        """
        Parse LLM response into AdvancedSentimentResult.
        """
        # Parse overall sentiment
        overall_score = response.overall.score
        overall_level = score_to_level(overall_score)
        overall_confidence = response.overall.confidence
        
        # Parse business confidence
        business_score = response.business_confidence.score
        business_level = score_to_level(business_score)
        
        # Parse public mood
        public_score = response.public_mood.score
        public_level = score_to_level(public_score)
        
        # Parse economic outlook
        economic_score = response.economic_outlook.score
        economic_level = score_to_level(economic_score)
        
        # Parse emotion
        try:
            primary_emotion = EmotionType(response.primary_emotion.lower())
        except ValueError:
            primary_emotion = EmotionType.NEUTRAL
        
        secondary_emotions = []
        for emo in response.secondary_emotions[:3]:
            try:
                secondary_emotions.append(EmotionType(emo.lower()))
            except ValueError:
                pass
        
        # Parse tone
        try:
            tone = ToneType(response.tone.lower())
        except ValueError:
            tone = ToneType.OBJECTIVE
        
        # Parse drivers
        positive_drivers = []
        negative_drivers = []
        for driver in response.drivers[:10]:
            driver_dict = {
                "factor": driver.factor,
                "strength": driver.strength,
                "quote": driver.quote[:200] if driver.quote else ""
            }
            if driver.direction.lower() == "positive":
                positive_drivers.append(driver_dict)
            else:
                negative_drivers.append(driver_dict)
        
        return AdvancedSentimentResult(
            overall_score=overall_score,
            overall_level=overall_level,
            overall_confidence=overall_confidence,
            business_confidence_score=business_score,
            business_confidence_level=business_level,
            public_mood_score=public_score,
            public_mood_level=public_level,
            economic_outlook_score=economic_score,
            economic_outlook_level=economic_level,
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            tone=tone,
            positive_drivers=positive_drivers,
            negative_drivers=negative_drivers,
            summary=response.summary[:500],
            analysis_source="llm"
        )
    
    def _create_neutral_result(
        self,
        start_time: float,
        source: str = "short_text"
    ) -> AdvancedSentimentResult:
        """Create a neutral sentiment result."""
        import time
        
        return AdvancedSentimentResult(
            overall_score=0.0,
            overall_level=SentimentLevel.NEUTRAL,
            overall_confidence=0.8,
            business_confidence_score=0.0,
            business_confidence_level=SentimentLevel.NEUTRAL,
            public_mood_score=0.0,
            public_mood_level=SentimentLevel.NEUTRAL,
            economic_outlook_score=0.0,
            economic_outlook_level=SentimentLevel.NEUTRAL,
            primary_emotion=EmotionType.NEUTRAL,
            secondary_emotions=[],
            tone=ToneType.OBJECTIVE,
            positive_drivers=[],
            negative_drivers=[],
            summary="Neutral content with no significant sentiment",
            analysis_source=source,
            processing_time_ms=(time.time() - start_time) * 1000
        )
    
    async def _fallback_analyze(
        self,
        text: str,
        start_time: float
    ) -> AdvancedSentimentResult:
        """
        Fall back to basic sentiment analysis.
        """
        import time
        
        self._fallback_analyses += 1
        
        if self.fallback_analyzer:
            try:
                # Use existing SentimentAnalyzer
                basic_result = await self._run_basic_analyzer(text)
                basic_result.analysis_source = "basic_fallback"
                basic_result.processing_time_ms = (time.time() - start_time) * 1000
                return basic_result
            except Exception as e:
                logger.error(f"Fallback analyzer also failed: {e}")
        
        # Ultimate fallback - keyword based
        result = self._keyword_based_analysis(text)
        result.processing_time_ms = (time.time() - start_time) * 1000
        result.analysis_source = "keyword_fallback"
        return result
    
    async def _run_basic_analyzer(self, text: str) -> AdvancedSentimentResult:
        """
        Run the existing basic SentimentAnalyzer.
        """
        # Integration with existing SentimentAnalyzer would go here
        # For now, return keyword-based analysis
        return self._keyword_based_analysis(text)
    
    def _keyword_based_analysis(self, text: str) -> AdvancedSentimentResult:
        """
        Simple keyword-based sentiment analysis as fallback.
        """
        text_lower = text.lower()
        
        # Extended sentiment word lists
        positive_words = {
            "growth": 0.3, "increase": 0.2, "improve": 0.3, "success": 0.4,
            "positive": 0.3, "gain": 0.2, "rise": 0.2, "boost": 0.3,
            "advance": 0.2, "progress": 0.3, "optimistic": 0.4, "confident": 0.3,
            "strong": 0.2, "stable": 0.2, "recovery": 0.3, "opportunity": 0.2
        }
        
        negative_words = {
            "decline": -0.3, "decrease": -0.2, "fall": -0.2, "crisis": -0.5,
            "concern": -0.2, "risk": -0.2, "worry": -0.3, "drop": -0.2,
            "loss": -0.3, "negative": -0.3, "fear": -0.3, "uncertain": -0.2,
            "weak": -0.2, "unstable": -0.3, "recession": -0.4, "threat": -0.3
        }
        
        # Calculate scores
        positive_score = sum(
            score for word, score in positive_words.items() if word in text_lower
        )
        negative_score = sum(
            score for word, score in negative_words.items() if word in text_lower
        )
        
        overall_score = max(-1.0, min(1.0, positive_score + negative_score))
        
        return AdvancedSentimentResult(
            overall_score=overall_score,
            overall_level=score_to_level(overall_score),
            overall_confidence=0.5,  # Low confidence for keyword-based
            business_confidence_score=overall_score * 0.8,
            business_confidence_level=score_to_level(overall_score * 0.8),
            public_mood_score=overall_score * 0.7,
            public_mood_level=score_to_level(overall_score * 0.7),
            economic_outlook_score=overall_score * 0.9,
            economic_outlook_level=score_to_level(overall_score * 0.9),
            primary_emotion=EmotionType.NEUTRAL,
            secondary_emotions=[],
            tone=ToneType.OBJECTIVE,
            positive_drivers=[],
            negative_drivers=[],
            summary="Keyword-based sentiment analysis"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        llm_stats = self.llm_client.get_stats()
        return {
            "total_analyses": self._total_analyses,
            "llm_analyses": self._llm_analyses,
            "fallback_analyses": self._fallback_analyses,
            "neutral_skips": self._neutral_skips,
            "errors": self._errors,
            "llm_usage_rate": (
                self._llm_analyses / self._total_analyses
                if self._total_analyses > 0 else 0
            ),
            "llm_client_stats": llm_stats
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_advanced_sentiment_analyzer(
    api_key: Optional[str] = None,
    cache_enabled: bool = True,
    fallback_analyzer: Optional[Any] = None,
    skip_neutral: bool = True
) -> AdvancedSentimentAnalyzer:
    """
    Factory function to create an AdvancedSentimentAnalyzer instance.
    
    Args:
        api_key: Groq API key (uses env var if not provided)
        cache_enabled: Whether to enable response caching
        fallback_analyzer: Basic SentimentAnalyzer instance for fallback
        skip_neutral: Skip LLM for clearly neutral content
    
    Returns:
        Configured AdvancedSentimentAnalyzer instance
    """
    llm_config = LLMConfig(
        model="llama-3.1-70b-versatile",
        temperature=0.3,  # Slightly higher for nuanced sentiment
        max_tokens=1500
    )
    
    cache_config = CacheConfig(
        enabled=cache_enabled,
        ttl_hours=24,
        prefix="sentiment_analyzer"
    )
    
    return AdvancedSentimentAnalyzer(
        llm_config=llm_config,
        cache_config=cache_config,
        fallback_analyzer=fallback_analyzer,
        skip_neutral_llm=skip_neutral
    )
