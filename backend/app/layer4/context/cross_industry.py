"""
Layer 4: Cross-Industry Intelligence

Analyzes how events in one industry affect other industries.
Identifies inter-industry dependencies and propagation effects.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ImpactDirection(Enum):
    """Direction of cross-industry impact"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    MIXED = "mixed"


class ImpactStrength(Enum):
    """Strength of cross-industry relationship"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    CRITICAL = "critical"


@dataclass
class IndustryRelationship:
    """Represents a relationship between two industries"""
    source_industry: str
    target_industry: str
    relationship_type: str  # 'supplier', 'customer', 'complementary', 'substitute'
    strength: ImpactStrength
    
    # How source events affect target
    impact_mapping: Dict[str, str]
    """
    Maps source events to target effects:
    {
        "supply_disruption": "input_shortage",
        "labor_strike": "delivery_delays",
    }
    """
    
    # Lag in days for impact to propagate
    propagation_lag_days: int
    
    # Historical examples
    historical_examples: List[str]
    
    # Description
    description: str


@dataclass
class CrossIndustryInsight:
    """An insight about cross-industry effects"""
    insight_id: str
    source_industry: str
    source_event: str
    
    # Affected industries
    affected_industries: List[str]
    
    # Impact details
    impact_direction: ImpactDirection
    impact_strength: ImpactStrength
    
    # Timeline
    expected_lag_days: int
    expected_duration_days: Optional[int]
    
    # What to expect
    expected_effects: List[str]
    
    # Recommended actions for affected industries
    recommended_actions: Dict[str, List[str]]
    
    # Confidence
    confidence: float
    
    # Human-readable summary
    narrative: str
    
    # Timestamp
    generated_at: datetime = field(default_factory=datetime.now)


class CrossIndustryAnalyzer:
    """
    Analyzes cross-industry dependencies and impact propagation.
    
    Features:
    - Industry dependency mapping
    - Impact propagation prediction
    - Supply chain effect analysis
    - Inter-industry early warnings
    """
    
    def __init__(self):
        self._relationships = self._load_industry_relationships()
        self._dependency_graph = self._build_dependency_graph()
        
        logger.info(f"Initialized CrossIndustryAnalyzer with {len(self._relationships)} relationships")
    
    def analyze_cross_industry_effects(
        self,
        source_industry: str,
        event_type: str,
        severity: float,
    ) -> List[CrossIndustryInsight]:
        """
        Analyze how an event in one industry affects others.
        
        Args:
            source_industry: Industry where event is occurring
            event_type: Type of event (e.g., 'supply_disruption', 'labor_strike')
            severity: Event severity (0-1)
            
        Returns:
            List of cross-industry insights
        """
        insights = []
        
        # Find all industries affected by source industry
        affected = self._find_affected_industries(source_industry)
        
        for target_industry, relationship in affected:
            # Check if this event type has a known effect
            if event_type in relationship.impact_mapping or self._matches_event_type(event_type, relationship):
                insight = self._create_insight(
                    relationship=relationship,
                    event_type=event_type,
                    severity=severity,
                )
                insights.append(insight)
        
        # Sort by impact strength and confidence
        insights.sort(
            key=lambda i: (
                i.impact_strength == ImpactStrength.CRITICAL,
                i.impact_strength == ImpactStrength.STRONG,
                i.confidence,
            ),
            reverse=True,
        )
        
        return insights
    
    def get_industry_dependencies(
        self,
        industry: str,
        direction: str = "both",
    ) -> Dict[str, Any]:
        """
        Get dependency map for an industry.
        
        Args:
            industry: Industry to analyze
            direction: 'incoming' (what affects this industry), 
                       'outgoing' (what this industry affects),
                       'both'
                       
        Returns:
            Dependency map with industries and relationships
        """
        incoming = []
        outgoing = []
        
        for rel in self._relationships:
            if rel.target_industry == industry:
                incoming.append({
                    "industry": rel.source_industry,
                    "relationship_type": rel.relationship_type,
                    "strength": rel.strength.value,
                    "description": rel.description,
                })
            if rel.source_industry == industry:
                outgoing.append({
                    "industry": rel.target_industry,
                    "relationship_type": rel.relationship_type,
                    "strength": rel.strength.value,
                    "description": rel.description,
                })
        
        result = {"industry": industry}
        
        if direction in ("incoming", "both"):
            result["incoming_dependencies"] = incoming
            result["critical_inputs"] = [
                d for d in incoming 
                if d["strength"] in ("critical", "strong")
            ]
        
        if direction in ("outgoing", "both"):
            result["outgoing_dependencies"] = outgoing
            result["critical_outputs"] = [
                d for d in outgoing 
                if d["strength"] in ("critical", "strong")
            ]
        
        if direction == "both":
            result["total_dependencies"] = len(incoming) + len(outgoing)
            result["critical_dependencies"] = len(result["critical_inputs"]) + len(result["critical_outputs"])
        
        return result
    
    def identify_vulnerable_chains(
        self,
        current_indicators: Dict[str, Dict[str, float]],
    ) -> List[Dict[str, Any]]:
        """
        Identify supply chain vulnerabilities across industries.
        
        Args:
            current_indicators: Dict of industry -> indicator values
            
        Returns:
            List of vulnerable chain analyses
        """
        vulnerable_chains = []
        
        for industry, indicators in current_indicators.items():
            # Check if any indicators are concerning
            concerning_indicators = [
                (k, v) for k, v in indicators.items()
                if v < 0.4  # Threshold for concern
            ]
            
            if concerning_indicators:
                # Find downstream industries that could be affected
                affected = self._trace_downstream_effects(industry, concerning_indicators)
                
                if affected:
                    vulnerable_chains.append({
                        "source_industry": industry,
                        "concerning_indicators": concerning_indicators,
                        "downstream_effects": affected,
                        "total_industries_at_risk": len(affected),
                        "recommended_actions": self._get_chain_mitigation_actions(industry, affected),
                    })
        
        return vulnerable_chains
    
    def get_early_warning_signals(
        self,
        target_industry: str,
        related_industry_indicators: Dict[str, Dict[str, float]],
    ) -> List[Dict[str, Any]]:
        """
        Get early warning signals from related industries.
        
        Args:
            target_industry: Industry to get warnings for
            related_industry_indicators: Indicators from related industries
            
        Returns:
            List of early warning signals
        """
        warnings = []
        
        # Get incoming dependencies
        deps = self.get_industry_dependencies(target_industry, "incoming")
        
        for dep in deps.get("incoming_dependencies", []):
            source_industry = dep["industry"]
            
            if source_industry in related_industry_indicators:
                indicators = related_industry_indicators[source_industry]
                
                # Check for concerning trends in source industry
                concerning = [
                    (k, v) for k, v in indicators.items()
                    if v < 0.4
                ]
                
                if concerning:
                    # Find the relationship
                    relationship = self._find_relationship(source_industry, target_industry)
                    
                    warnings.append({
                        "source_industry": source_industry,
                        "concerning_indicators": concerning,
                        "relationship": dep["relationship_type"],
                        "strength": dep["strength"],
                        "expected_lag_days": relationship.propagation_lag_days if relationship else 3,
                        "potential_effects": self._predict_effects(concerning, relationship) if relationship else [],
                        "warning_level": "critical" if dep["strength"] in ("critical", "strong") else "moderate",
                    })
        
        # Sort by warning level
        warnings.sort(key=lambda w: w["warning_level"] == "critical", reverse=True)
        
        return warnings
    
    def _find_affected_industries(
        self,
        source_industry: str,
    ) -> List[Tuple[str, IndustryRelationship]]:
        """Find all industries affected by source industry."""
        affected = []
        
        for rel in self._relationships:
            if rel.source_industry == source_industry:
                affected.append((rel.target_industry, rel))
        
        return affected
    
    def _find_relationship(
        self,
        source: str,
        target: str,
    ) -> Optional[IndustryRelationship]:
        """Find relationship between two industries."""
        for rel in self._relationships:
            if rel.source_industry == source and rel.target_industry == target:
                return rel
        return None
    
    def _matches_event_type(
        self,
        event_type: str,
        relationship: IndustryRelationship,
    ) -> bool:
        """Check if event type could have cross-industry effects."""
        # Generic event types that always propagate
        general_events = {"supply_disruption", "labor_action", "infrastructure_failure", "price_surge"}
        
        if event_type in general_events:
            return True
        
        # Check for partial matches in impact mapping
        for key in relationship.impact_mapping.keys():
            if event_type in key or key in event_type:
                return True
        
        return False
    
    def _create_insight(
        self,
        relationship: IndustryRelationship,
        event_type: str,
        severity: float,
    ) -> CrossIndustryInsight:
        """Create a cross-industry insight from relationship and event."""
        # Determine impact direction based on event type
        negative_events = {"disruption", "shortage", "strike", "failure", "crisis"}
        is_negative = any(neg in event_type.lower() for neg in negative_events)
        
        impact_direction = ImpactDirection.NEGATIVE if is_negative else ImpactDirection.POSITIVE
        
        # Scale impact strength by severity
        if severity >= 0.8 and relationship.strength == ImpactStrength.CRITICAL:
            impact_strength = ImpactStrength.CRITICAL
        elif severity >= 0.6 or relationship.strength in (ImpactStrength.CRITICAL, ImpactStrength.STRONG):
            impact_strength = ImpactStrength.STRONG
        elif severity >= 0.4:
            impact_strength = ImpactStrength.MODERATE
        else:
            impact_strength = ImpactStrength.WEAK
        
        # Get expected effects
        expected_effects = self._get_expected_effects(relationship, event_type)
        
        # Get recommended actions
        recommended_actions = self._get_recommended_actions(
            relationship.target_industry,
            event_type,
            impact_strength,
        )
        
        # Generate narrative
        narrative = self._generate_narrative(
            relationship,
            event_type,
            severity,
            expected_effects,
        )
        
        return CrossIndustryInsight(
            insight_id=f"cross_{relationship.source_industry}_{relationship.target_industry}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            source_industry=relationship.source_industry,
            source_event=event_type,
            affected_industries=[relationship.target_industry],
            impact_direction=impact_direction,
            impact_strength=impact_strength,
            expected_lag_days=relationship.propagation_lag_days,
            expected_duration_days=self._estimate_duration(event_type, severity),
            expected_effects=expected_effects,
            recommended_actions=recommended_actions,
            confidence=self._calculate_confidence(relationship, severity),
            narrative=narrative,
        )
    
    def _get_expected_effects(
        self,
        relationship: IndustryRelationship,
        event_type: str,
    ) -> List[str]:
        """Get expected effects on target industry."""
        effects = []
        
        # From impact mapping
        for source_event, target_effect in relationship.impact_mapping.items():
            if source_event in event_type or event_type in source_event:
                effects.append(target_effect)
        
        # Generic effects based on relationship type
        if not effects:
            if relationship.relationship_type == "supplier":
                effects = ["Input availability may be affected", "Cost increases possible"]
            elif relationship.relationship_type == "customer":
                effects = ["Demand may change", "Payment timing may be affected"]
            elif relationship.relationship_type == "complementary":
                effects = ["Market conditions may shift", "Consumer behavior may change"]
        
        return effects
    
    def _get_recommended_actions(
        self,
        target_industry: str,
        event_type: str,
        impact_strength: ImpactStrength,
    ) -> Dict[str, List[str]]:
        """Get recommended actions for affected industries."""
        actions = {target_industry: []}
        
        if impact_strength in (ImpactStrength.CRITICAL, ImpactStrength.STRONG):
            actions[target_industry].extend([
                "Increase inventory buffer for affected inputs",
                "Identify alternative suppliers immediately",
                "Communicate with key customers about potential impacts",
            ])
        
        if "supply" in event_type.lower() or "shortage" in event_type.lower():
            actions[target_industry].extend([
                "Review supply chain resilience",
                "Check safety stock levels",
            ])
        
        if "price" in event_type.lower() or "cost" in event_type.lower():
            actions[target_industry].extend([
                "Review pricing strategy",
                "Assess cost pass-through options",
            ])
        
        if "labor" in event_type.lower() or "strike" in event_type.lower():
            actions[target_industry].extend([
                "Review workforce contingency plans",
                "Assess automation options for critical processes",
            ])
        
        return actions
    
    def _generate_narrative(
        self,
        relationship: IndustryRelationship,
        event_type: str,
        severity: float,
        expected_effects: List[str],
    ) -> str:
        """Generate human-readable narrative for insight."""
        severity_text = "severe" if severity >= 0.7 else "moderate" if severity >= 0.4 else "minor"
        
        narrative = (
            f"A {severity_text} {event_type.replace('_', ' ')} in the {relationship.source_industry} industry "
            f"is expected to affect {relationship.target_industry} "
            f"(relationship: {relationship.relationship_type}, strength: {relationship.strength.value}). "
        )
        
        if relationship.propagation_lag_days:
            narrative += f"Effects typically appear within {relationship.propagation_lag_days} days. "
        
        if expected_effects:
            narrative += f"Expected effects: {expected_effects[0]}."
        
        return narrative
    
    def _estimate_duration(self, event_type: str, severity: float) -> Optional[int]:
        """Estimate duration of cross-industry effects."""
        base_durations = {
            "supply_disruption": 14,
            "labor_strike": 7,
            "infrastructure_failure": 21,
            "price_surge": 30,
            "demand_shift": 60,
        }
        
        for key, base_duration in base_durations.items():
            if key in event_type.lower():
                return int(base_duration * (0.5 + severity))
        
        return int(14 * (0.5 + severity))  # Default 7-21 days based on severity
    
    def _calculate_confidence(
        self,
        relationship: IndustryRelationship,
        severity: float,
    ) -> float:
        """Calculate confidence level for the insight."""
        base_confidence = 0.6
        
        # Higher confidence for stronger relationships
        if relationship.strength == ImpactStrength.CRITICAL:
            base_confidence += 0.2
        elif relationship.strength == ImpactStrength.STRONG:
            base_confidence += 0.1
        
        # More confident with higher severity (clearer signal)
        base_confidence += severity * 0.15
        
        # Historical examples increase confidence
        if relationship.historical_examples:
            base_confidence += 0.05 * min(len(relationship.historical_examples), 3)
        
        return min(0.95, base_confidence)
    
    def _trace_downstream_effects(
        self,
        source_industry: str,
        concerning_indicators: List[Tuple[str, float]],
    ) -> List[Dict[str, Any]]:
        """Trace downstream effects through industry chain."""
        affected = []
        visited = {source_industry}
        to_process = [(source_industry, 0)]  # (industry, depth)
        
        while to_process:
            current_industry, depth = to_process.pop(0)
            
            if depth > 3:  # Limit chain depth
                continue
            
            for rel in self._relationships:
                if rel.source_industry == current_industry and rel.target_industry not in visited:
                    visited.add(rel.target_industry)
                    
                    affected.append({
                        "industry": rel.target_industry,
                        "depth": depth + 1,
                        "path": f"{source_industry} → {rel.target_industry}" if depth == 0 else f"... → {rel.target_industry}",
                        "relationship": rel.relationship_type,
                        "expected_lag_days": rel.propagation_lag_days * (depth + 1),
                    })
                    
                    # Continue tracing
                    to_process.append((rel.target_industry, depth + 1))
        
        return affected
    
    def _get_chain_mitigation_actions(
        self,
        source_industry: str,
        affected: List[Dict[str, Any]],
    ) -> List[str]:
        """Get mitigation actions for supply chain vulnerability."""
        actions = []
        
        if len(affected) > 2:
            actions.append("Issue early warning to all downstream partners")
        
        actions.extend([
            f"Monitor {source_industry} indicators closely",
            "Pre-position critical inventory",
            "Activate alternative supplier agreements",
        ])
        
        return actions
    
    def _predict_effects(
        self,
        concerning_indicators: List[Tuple[str, float]],
        relationship: IndustryRelationship,
    ) -> List[str]:
        """Predict effects based on concerning indicators and relationship."""
        effects = []
        
        for indicator, value in concerning_indicators:
            if "SUPPLY" in indicator:
                effects.append("Supply chain disruptions possible")
            elif "POWER" in indicator:
                effects.append("Production capacity may be affected")
            elif "TRANSPORT" in indicator:
                effects.append("Delivery delays expected")
            elif "LABOR" in indicator:
                effects.append("Workforce availability concerns")
        
        return effects[:3]  # Return top 3
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build a graph of industry dependencies."""
        graph: Dict[str, Set[str]] = {}
        
        for rel in self._relationships:
            if rel.source_industry not in graph:
                graph[rel.source_industry] = set()
            graph[rel.source_industry].add(rel.target_industry)
        
        return graph
    
    def _load_industry_relationships(self) -> List[IndustryRelationship]:
        """Load industry relationship mappings."""
        return [
            # Logistics → Others (logistics affects multiple industries)
            IndustryRelationship(
                source_industry="logistics",
                target_industry="retail",
                relationship_type="supplier",
                strength=ImpactStrength.CRITICAL,
                impact_mapping={
                    "supply_disruption": "inventory_shortage",
                    "fuel_crisis": "delivery_delays",
                    "labor_strike": "stock_outs",
                },
                propagation_lag_days=2,
                historical_examples=[
                    "2022 Transport Strike: 15% revenue drop for retail",
                ],
                description="Logistics provides delivery services critical to retail operations",
            ),
            IndustryRelationship(
                source_industry="logistics",
                target_industry="manufacturing",
                relationship_type="supplier",
                strength=ImpactStrength.STRONG,
                impact_mapping={
                    "supply_disruption": "input_delays",
                    "fuel_crisis": "production_slowdown",
                },
                propagation_lag_days=3,
                historical_examples=[
                    "2022 Fuel Shortage: Manufacturing output dropped 20%",
                ],
                description="Logistics delivers raw materials and components to manufacturers",
            ),
            
            # Manufacturing → Others
            IndustryRelationship(
                source_industry="manufacturing",
                target_industry="retail",
                relationship_type="supplier",
                strength=ImpactStrength.STRONG,
                impact_mapping={
                    "production_halt": "inventory_shortage",
                    "quality_issues": "returns_increase",
                },
                propagation_lag_days=7,
                historical_examples=[
                    "Factory closures led to 3-week retail shortages",
                ],
                description="Manufacturing supplies products sold by retail",
            ),
            IndustryRelationship(
                source_industry="manufacturing",
                target_industry="export_oriented",
                relationship_type="supplier",
                strength=ImpactStrength.CRITICAL,
                impact_mapping={
                    "production_halt": "export_delays",
                    "quality_issues": "order_cancellations",
                },
                propagation_lag_days=5,
                historical_examples=[
                    "Power outages led to missed export deadlines",
                ],
                description="Manufacturing produces goods for export",
            ),
            
            # Banking/Financial → Others
            IndustryRelationship(
                source_industry="banking",
                target_industry="retail",
                relationship_type="supplier",
                strength=ImpactStrength.STRONG,
                impact_mapping={
                    "payment_system_issues": "transaction_failures",
                    "credit_tightening": "reduced_purchasing",
                    "bank_strike": "cash_handling_issues",
                },
                propagation_lag_days=1,
                historical_examples=[
                    "Banking strike → Retail payment processing delays",
                ],
                description="Banking provides payment processing and credit for retail",
            ),
            IndustryRelationship(
                source_industry="banking",
                target_industry="manufacturing",
                relationship_type="supplier",
                strength=ImpactStrength.MODERATE,
                impact_mapping={
                    "credit_tightening": "working_capital_shortage",
                    "forex_issues": "import_payment_delays",
                },
                propagation_lag_days=7,
                historical_examples=[
                    "Credit restrictions slowed manufacturing investment",
                ],
                description="Banking provides financing for manufacturing operations",
            ),
            
            # Agriculture → Others
            IndustryRelationship(
                source_industry="agriculture",
                target_industry="hospitality",
                relationship_type="supplier",
                strength=ImpactStrength.STRONG,
                impact_mapping={
                    "harvest_failure": "food_cost_increase",
                    "supply_shortage": "menu_adjustments",
                },
                propagation_lag_days=14,
                historical_examples=[
                    "Drought conditions increased hospitality food costs 25%",
                ],
                description="Agriculture provides food inputs for hospitality sector",
            ),
            IndustryRelationship(
                source_industry="agriculture",
                target_industry="retail",
                relationship_type="supplier",
                strength=ImpactStrength.MODERATE,
                impact_mapping={
                    "harvest_failure": "produce_shortage",
                    "price_surge": "margin_pressure",
                },
                propagation_lag_days=7,
                historical_examples=[
                    "Crop failures led to retail price increases",
                ],
                description="Agriculture supplies food products for retail sale",
            ),
            
            # Energy/Power → Others
            IndustryRelationship(
                source_industry="energy",
                target_industry="manufacturing",
                relationship_type="supplier",
                strength=ImpactStrength.CRITICAL,
                impact_mapping={
                    "power_outages": "production_halt",
                    "price_surge": "cost_increase",
                },
                propagation_lag_days=0,
                historical_examples=[
                    "Load shedding caused immediate production stoppages",
                ],
                description="Energy is critical input for manufacturing operations",
            ),
            IndustryRelationship(
                source_industry="energy",
                target_industry="retail",
                relationship_type="supplier",
                strength=ImpactStrength.MODERATE,
                impact_mapping={
                    "power_outages": "store_closures",
                    "price_surge": "operating_cost_increase",
                },
                propagation_lag_days=0,
                historical_examples=[
                    "Extended outages closed retail stores for days",
                ],
                description="Retail requires power for operations",
            ),
            
            # Hospitality/Tourism → Others
            IndustryRelationship(
                source_industry="hospitality",
                target_industry="retail",
                relationship_type="complementary",
                strength=ImpactStrength.MODERATE,
                impact_mapping={
                    "tourism_surge": "increased_sales",
                    "tourism_decline": "reduced_footfall",
                },
                propagation_lag_days=0,
                historical_examples=[
                    "Tourism recovery boosted retail sales 15%",
                ],
                description="Tourism activity drives retail demand",
            ),
            IndustryRelationship(
                source_industry="hospitality",
                target_industry="logistics",
                relationship_type="customer",
                strength=ImpactStrength.WEAK,
                impact_mapping={
                    "tourism_surge": "increased_logistics_demand",
                },
                propagation_lag_days=3,
                historical_examples=[
                    "Tourism season increased logistics volumes",
                ],
                description="Hospitality creates demand for logistics services",
            ),
        ]


# Export for easy importing
__all__ = [
    "CrossIndustryAnalyzer",
    "CrossIndustryInsight",
    "IndustryRelationship",
    "ImpactDirection",
    "ImpactStrength",
]
