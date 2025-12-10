from typing import List, Dict, Any
from app.layer2.indicators.calculator import IndicatorCalculator
from app.layer2.indicators.registry import IndicatorRegistry
from app.models import IndicatorDefinition

@IndicatorRegistry.register("frequency_count")
class FrequencyCalculator(IndicatorCalculator):
    """
    Calculates indicator value based on the frequency of relevant articles.
    """

    def calculate(self, articles: List[Dict[str, Any]], indicator: IndicatorDefinition, **kwargs) -> float:
        """
        Count articles that match the indicator's keywords or context.
        """
        if not articles:
            return 0.0
        
        # Simple count for now
        # In a real scenario, we might filter articles that specifically match this indicator
        # if the input list isn't already filtered.
        # Assuming 'articles' passed here are already relevant to this indicator.
        
        count = len(articles)
        
        # Normalize based on indicator's expected range
        # If max_value is 50 (e.g., 50 articles/day is max), then 25 articles = 50.0
        min_val = indicator.min_value if indicator.min_value is not None else 0
        max_val = indicator.max_value if indicator.max_value is not None else 100
        
        return self.normalize(count, min_val, max_val)

@IndicatorRegistry.register("keyword_density")
class KeywordDensityCalculator(IndicatorCalculator):
    """
    Calculates based on total keyword occurrences across articles.
    """
    
    def calculate(self, articles: List[Dict[str, Any]], indicator: IndicatorDefinition, **kwargs) -> float:
        if not articles:
            return 0.0
            
        total_keywords = 0
        for article in articles:
            # Assuming article has 'initial_classification' with 'keywords'
            # or we count them from body
            keywords = article.get("initial_classification", {}).get("keywords", [])
            total_keywords += len(keywords)
            
        min_val = indicator.min_value if indicator.min_value is not None else 0
        max_val = indicator.max_value if indicator.max_value is not None else 200
        
        return self.normalize(total_keywords, min_val, max_val)
