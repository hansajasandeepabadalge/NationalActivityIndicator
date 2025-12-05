"""
Indicator Dependency Mapper - Tracks relationships between indicators.

Handles:
- Parent-child dependencies (e.g., fuel shortage → transport disruption)
- Correlation tracking
- Cascade effect prediction
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IndicatorDependency:
    """Represents a dependency between two indicators"""
    parent_id: str  # The causing indicator
    child_id: str   # The affected indicator
    relationship: str  # 'causes', 'correlates', 'influences'
    correlation_strength: float  # -1.0 to 1.0
    time_lag_hours: int = 0  # How long before effect is seen
    confidence: float = 0.8


@dataclass
class CascadeEffect:
    """Predicted secondary effect from indicator change"""
    indicator_id: str
    indicator_name: str
    expected_change: float
    confidence: float
    time_lag_hours: int


class IndicatorDependencyMapper:
    """
    Maps and predicts indicator dependencies and cascade effects.
    """
    
    # Predefined dependency relationships for Sri Lanka indicators
    DEFAULT_DEPENDENCIES = [
        # Economic chain effects
        IndicatorDependency("fuel_shortage", "transport_disruption", "causes", 0.85, 24),
        IndicatorDependency("fuel_shortage", "inflation_pressure", "causes", 0.70, 72),
        IndicatorDependency("currency_instability", "inflation_pressure", "causes", 0.75, 48),
        IndicatorDependency("inflation_pressure", "consumer_confidence", "causes", -0.65, 24),
        IndicatorDependency("consumer_confidence", "business_activity", "correlates", 0.60, 48),
        
        # Political chain effects
        IndicatorDependency("political_unrest", "currency_instability", "influences", 0.55, 24),
        IndicatorDependency("political_unrest", "tourism_activity", "causes", -0.70, 48),
        IndicatorDependency("policy_changes", "business_activity", "influences", 0.45, 72),
        
        # Environmental chain effects
        IndicatorDependency("weather_severity", "flood_risk", "causes", 0.80, 6),
        IndicatorDependency("flood_risk", "transport_disruption", "causes", 0.75, 12),
        IndicatorDependency("drought_concern", "inflation_pressure", "influences", 0.40, 168),
        
        # Social chain effects
        IndicatorDependency("cost_of_living", "public_sentiment", "causes", -0.70, 24),
        IndicatorDependency("power_outages", "business_activity", "causes", -0.55, 12),
    ]
    
    def __init__(self, dependencies: Optional[List[IndicatorDependency]] = None):
        """
        Initialize with dependencies list or use defaults.
        """
        self._dependencies = dependencies or self.DEFAULT_DEPENDENCIES
        self._build_index()
    
    def _build_index(self):
        """Build lookup indices for fast access"""
        # Index by parent (what does this indicator affect?)
        self._by_parent: Dict[str, List[IndicatorDependency]] = {}
        # Index by child (what affects this indicator?)
        self._by_child: Dict[str, List[IndicatorDependency]] = {}
        
        for dep in self._dependencies:
            if dep.parent_id not in self._by_parent:
                self._by_parent[dep.parent_id] = []
            self._by_parent[dep.parent_id].append(dep)
            
            if dep.child_id not in self._by_child:
                self._by_child[dep.child_id] = []
            self._by_child[dep.child_id].append(dep)
    
    def get_affected_indicators(self, indicator_id: str) -> List[IndicatorDependency]:
        """Get all indicators that this one affects (children)"""
        return self._by_parent.get(indicator_id, [])
    
    def get_affecting_indicators(self, indicator_id: str) -> List[IndicatorDependency]:
        """Get all indicators that affect this one (parents)"""
        return self._by_child.get(indicator_id, [])
    
    def predict_cascade_effects(self, indicator_id: str, 
                                 value_change: float,
                                 depth: int = 2) -> List[CascadeEffect]:
        """
        Predict cascading impacts when an indicator changes.
        
        Args:
            indicator_id: The indicator that changed
            value_change: How much it changed (e.g., +10 or -5)
            depth: How many levels deep to trace effects
            
        Returns:
            List of predicted secondary effects
        """
        effects = []
        visited = set()
        
        def trace_effects(ind_id: str, change: float, current_depth: int):
            if current_depth > depth or ind_id in visited:
                return
            visited.add(ind_id)
            
            for dep in self.get_affected_indicators(ind_id):
                # Calculate expected change based on correlation
                expected_change = change * dep.correlation_strength
                
                effects.append(CascadeEffect(
                    indicator_id=dep.child_id,
                    indicator_name=dep.child_id.replace("_", " ").title(),
                    expected_change=expected_change,
                    confidence=dep.confidence * (0.8 ** (current_depth - 1)),
                    time_lag_hours=dep.time_lag_hours
                ))
                
                # Recursively trace further effects
                trace_effects(dep.child_id, expected_change, current_depth + 1)
        
        trace_effects(indicator_id, value_change, 1)
        
        # Sort by confidence
        effects.sort(key=lambda x: x.confidence, reverse=True)
        return effects
    
    def get_dependency_chain(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """
        Find the dependency path between two indicators.
        
        Returns:
            List of indicator IDs forming the path, or None if no path exists
        """
        from collections import deque
        
        queue = deque([(from_id, [from_id])])
        visited = {from_id}
        
        while queue:
            current, path = queue.popleft()
            
            if current == to_id:
                return path
            
            for dep in self.get_affected_indicators(current):
                if dep.child_id not in visited:
                    visited.add(dep.child_id)
                    queue.append((dep.child_id, path + [dep.child_id]))
        
        return None
    
    def get_all_dependencies(self) -> List[Dict[str, Any]]:
        """Get all dependencies as dictionaries"""
        return [
            {
                "parent_id": d.parent_id,
                "child_id": d.child_id,
                "relationship": d.relationship,
                "correlation_strength": d.correlation_strength,
                "time_lag_hours": d.time_lag_hours,
                "confidence": d.confidence
            }
            for d in self._dependencies
        ]
    
    def add_dependency(self, dependency: IndicatorDependency):
        """Add a new dependency"""
        self._dependencies.append(dependency)
        self._build_index()
    
    def get_correlation_matrix(self, indicator_ids: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get correlation matrix for specified indicators.
        
        Returns:
            Nested dict: matrix[from_id][to_id] = correlation
        """
        matrix = {ind: {ind2: 0.0 for ind2 in indicator_ids} for ind in indicator_ids}
        
        for dep in self._dependencies:
            if dep.parent_id in indicator_ids and dep.child_id in indicator_ids:
                matrix[dep.parent_id][dep.child_id] = dep.correlation_strength
        
        # Self-correlation is 1.0
        for ind in indicator_ids:
            matrix[ind][ind] = 1.0
        
        return matrix


# Singleton instance
_mapper_instance: Optional[IndicatorDependencyMapper] = None

def get_dependency_mapper() -> IndicatorDependencyMapper:
    """Get or create the dependency mapper instance"""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = IndicatorDependencyMapper()
    return _mapper_instance
