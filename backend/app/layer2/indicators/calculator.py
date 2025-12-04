from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.models import IndicatorDefinition  # Import from unified models package

class IndicatorCalculator(ABC):
    """
    Abstract base class for all indicator calculation strategies.
    Follows the Strategy Pattern.
    """

    @abstractmethod
    def calculate(self, articles: List[Dict[str, Any]], indicator: IndicatorDefinition, **kwargs) -> float:
        """
        Calculate the indicator value based on a list of articles.
        
        Args:
            articles: List of article dictionaries (or objects)
            indicator: The indicator definition object
            **kwargs: Additional arguments
            
        Returns:
            float: The calculated indicator value
        """
        pass
    
    def normalize(self, value: float, min_val: float, max_val: float) -> float:
        """
        Normalize a value to a 0-100 scale (or other target range).
        """
        if max_val == min_val:
            return 0.0
        
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0.0, min(100.0, normalized))
