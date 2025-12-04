from typing import Dict, Type
from app.layer2.indicators.calculator import IndicatorCalculator

class IndicatorRegistry:
    """
    Registry to manage and retrieve indicator calculators.
    """
    
    _calculators: Dict[str, Type[IndicatorCalculator]] = {}
    
    @classmethod
    def register(cls, calculation_type: str):
        """
        Decorator to register a calculator class for a specific calculation type.
        """
        def wrapper(calculator_cls):
            cls._calculators[calculation_type] = calculator_cls
            return calculator_cls
        return wrapper
    
    @classmethod
    def get_calculator(cls, calculation_type: str) -> IndicatorCalculator:
        """
        Get an instance of the calculator for the given type.
        """
        calculator_cls = cls._calculators.get(calculation_type)
        if not calculator_cls:
            raise ValueError(f"No calculator registered for type: {calculation_type}")
        
        return calculator_cls()
