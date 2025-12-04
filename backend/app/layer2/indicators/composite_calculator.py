from typing import List, Dict, Any
from app.layer2.indicators.calculator import IndicatorCalculator
from app.layer2.indicators.registry import IndicatorRegistry
from app.models import IndicatorDefinition

@IndicatorRegistry.register("composite")
class CompositeCalculator(IndicatorCalculator):
    """
    Calculates indicator value based on other indicators.
    """

    def calculate(self, articles: List[Dict[str, Any]], indicator: IndicatorDefinition, **kwargs) -> float:
        """
        Calculate weighted average of child indicators.
        Requires 'child_values' in kwargs: Dict[indicator_id, value]
        """
        child_values = kwargs.get("child_values", {})
        dependencies = kwargs.get("dependencies", [])
        
        if not dependencies:
            return 0.0
            
        total_weighted_value = 0.0
        total_weight = 0.0
        
        for dep in dependencies:
            child_id = dep.child_indicator_id
            weight = dep.weight
            
            if child_id in child_values:
                value = child_values[child_id]
                total_weighted_value += value * weight
                total_weight += weight
                
        if total_weight == 0:
            return 0.0
            
        return total_weighted_value / total_weight
