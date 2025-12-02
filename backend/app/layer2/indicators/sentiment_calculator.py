from typing import List, Dict, Any
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from app.layer2.indicators.calculator import IndicatorCalculator
from app.layer2.indicators.registry import IndicatorRegistry
from app.models.indicator import IndicatorDefinition

# Ensure VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

@IndicatorRegistry.register("sentiment_analysis")
class SentimentCalculator(IndicatorCalculator):
    """
    Calculates indicator value based on sentiment analysis of articles.
    Uses NLTK VADER.
    """
    
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def calculate(self, articles: List[Dict[str, Any]], indicator: IndicatorDefinition, **kwargs) -> float:
        """
        Calculate average sentiment score for the articles.
        Returns a value between 0 (Negative) and 100 (Positive).
        """
        if not articles:
            return 50.0 # Neutral baseline
            
        total_compound_score = 0.0
        count = 0
        
        for article in articles:
            # Analyze title and body
            content = article.get("content", {})
            text = f"{content.get('title', '')} {content.get('body', '')}"
            
            if not text.strip():
                continue
                
            scores = self.sia.polarity_scores(text)
            total_compound_score += scores['compound']
            count += 1
            
        if count == 0:
            return 50.0
            
        avg_score = total_compound_score / count
        
        # VADER compound score is -1 to 1
        # Normalize to 0-100
        # -1 -> 0, 0 -> 50, 1 -> 100
        normalized_score = ((avg_score + 1) / 2) * 100
        
        return max(0.0, min(100.0, normalized_score))
