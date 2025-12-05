"""
Sentiment-based Indicator Calculator.

Uses the unified SentimentAnalyzer for consistent sentiment analysis
across the entire system.
"""
from typing import List, Dict, Any
from app.layer2.indicators.calculator import IndicatorCalculator
from app.layer2.indicators.registry import IndicatorRegistry
from app.layer2.nlp.sentiment_analyzer import SentimentAnalyzer
from app.models import IndicatorDefinition


@IndicatorRegistry.register("sentiment_analysis")
class SentimentCalculator(IndicatorCalculator):
    """
    Calculates indicator value based on sentiment analysis of articles.
    Uses the unified SentimentAnalyzer with VADER backend for speed.
    
    For more accurate analysis, can switch to 'transformers' backend.
    """
    
    def __init__(self, backend: str = 'vader'):
        """
        Initialize sentiment calculator.
        
        Args:
            backend: 'vader' (fast) or 'transformers' (accurate)
        """
        self.analyzer = SentimentAnalyzer(backend=backend)

    def calculate(self, articles: List[Dict[str, Any]], indicator: IndicatorDefinition, **kwargs) -> float:
        """
        Calculate average sentiment score for the articles.
        Returns a value between 0 (Negative) and 100 (Positive).
        
        Args:
            articles: List of article dictionaries
            indicator: Indicator definition (for potential customization)
            **kwargs: Additional options
                - weight_by_credibility: bool (default True)
                - use_transformers: bool (default False)
        
        Returns:
            Sentiment score from 0 to 100
        """
        if not articles:
            return 50.0  # Neutral baseline
        
        weight_by_credibility = kwargs.get('weight_by_credibility', True)
        
        # Use aggregate sentiment with optional credibility weighting
        result = self.analyzer.get_aggregate_sentiment(
            articles, 
            weight_by_credibility=weight_by_credibility
        )
        
        return result.score_normalized
    
    def calculate_detailed(self, articles: List[Dict[str, Any]], 
                           indicator: IndicatorDefinition, **kwargs) -> Dict[str, Any]:
        """
        Calculate sentiment with detailed breakdown.
        
        Returns:
            Dict with score, label, confidence, and per-article details
        """
        if not articles:
            return {
                'score': 50.0,
                'label': 'neutral',
                'confidence': 0.0,
                'article_count': 0,
                'details': []
            }
        
        # Get individual article sentiments
        article_results = []
        for article in articles:
            result = self.analyzer.analyze_article(article)
            article_results.append({
                'article_id': article.get('article_id', 'unknown'),
                'sentiment': result['overall'].to_dict()
            })
        
        # Get aggregate
        aggregate = self.analyzer.get_aggregate_sentiment(articles)
        
        return {
            'score': aggregate.score_normalized,
            'label': aggregate.label.value,
            'confidence': aggregate.confidence,
            'positive_component': aggregate.positive,
            'negative_component': aggregate.negative,
            'neutral_component': aggregate.neutral,
            'article_count': len(articles),
            'processing_time_ms': aggregate.processing_time_ms,
            'details': article_results
        }

