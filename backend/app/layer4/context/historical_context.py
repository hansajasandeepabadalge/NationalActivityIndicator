"""
Layer 4: Historical Context Analyzer

Provides historical event matching and outcome analysis.
Matches current situations to past events to provide context and predictions.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
import math

logger = logging.getLogger(__name__)


@dataclass
class HistoricalEvent:
    """A past event with known outcomes"""
    event_id: str
    event_type: str
    event_name: str
    category: str
    
    # When it happened
    start_date: datetime
    end_date: Optional[datetime]
    duration_days: int
    
    # What the indicators looked like
    indicator_profile: Dict[str, float]
    
    # What happened
    severity: str  # 'minor', 'moderate', 'major', 'severe'
    description: str
    
    # Business impact
    business_impacts: Dict[str, Dict[str, Any]]
    """
    Structure:
    {
        "retail": {"revenue_impact": -0.30, "duration_days": 12},
        "manufacturing": {"revenue_impact": -0.20, "duration_days": 8}
    }
    """
    
    # Leading indicators that preceded it
    leading_indicators: List[str]
    
    # What helped / what made it worse
    mitigating_factors: List[str]
    aggravating_factors: List[str]
    
    # Tags for searching
    tags: List[str] = field(default_factory=list)


@dataclass
class HistoricalMatch:
    """Result of matching current situation to historical event"""
    event: HistoricalEvent
    similarity_score: float  # 0-1
    matching_indicators: List[Tuple[str, float, float]]  # (indicator, current, historical)
    key_differences: List[str]
    
    # Predictions based on historical outcome
    predicted_duration_days: int
    predicted_severity: str
    predicted_impact: Dict[str, float]
    
    # Context
    time_since_event: int  # days
    relevance_narrative: str


@dataclass
class TrendContext:
    """Historical trend context for an indicator"""
    indicator_code: str
    current_value: float
    historical_average: float
    historical_min: float
    historical_max: float
    percentile_historically: int  # 0-100
    trend_vs_history: str  # 'at_historic_low', 'below_average', 'average', 'above_average', 'at_historic_high'
    similar_periods: List[Dict[str, Any]]


class HistoricalContextAnalyzer:
    """
    Analyzes current situations by comparing to historical events.
    
    Features:
    - Event matching based on indicator profiles
    - Outcome prediction based on historical patterns
    - Duration and severity estimation
    - Leading indicator detection
    """
    
    def __init__(self):
        # Load historical events database
        self._events = self._load_historical_events()
        self._indicator_history = self._load_indicator_history()
        
        logger.info(f"Initialized HistoricalContextAnalyzer with {len(self._events)} historical events")
    
    def find_similar_events(
        self,
        current_indicators: Dict[str, float],
        industry: Optional[str] = None,
        category: Optional[str] = None,
        top_n: int = 5,
        min_similarity: float = 0.5,
    ) -> List[HistoricalMatch]:
        """
        Find historical events similar to current situation.
        
        Args:
            current_indicators: Current indicator values
            industry: Optional industry filter
            category: Optional event category filter
            top_n: Number of top matches to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of HistoricalMatch objects
        """
        matches = []
        
        for event in self._events:
            # Filter by category if specified
            if category and event.category != category:
                continue
            
            # Calculate similarity
            similarity = self._calculate_similarity(
                current_indicators,
                event.indicator_profile,
            )
            
            if similarity >= min_similarity:
                match = self._create_match(
                    event=event,
                    similarity=similarity,
                    current_indicators=current_indicators,
                    industry=industry,
                )
                matches.append(match)
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        
        return matches[:top_n]
    
    def get_historical_context(
        self,
        indicator_code: str,
        current_value: float,
        lookback_days: int = 365,
    ) -> TrendContext:
        """
        Get historical context for a specific indicator.
        
        Args:
            indicator_code: Indicator to analyze
            current_value: Current indicator value
            lookback_days: Days of history to consider
            
        Returns:
            TrendContext with historical comparison
        """
        history = self._indicator_history.get(indicator_code, [])
        
        if not history:
            return TrendContext(
                indicator_code=indicator_code,
                current_value=current_value,
                historical_average=0.5,
                historical_min=0.0,
                historical_max=1.0,
                percentile_historically=50,
                trend_vs_history="average",
                similar_periods=[],
            )
        
        # Calculate statistics
        values = [h["value"] for h in history]
        avg = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        
        # Calculate percentile
        below_count = sum(1 for v in values if v < current_value)
        percentile = int(100 * below_count / len(values))
        
        # Determine trend vs history
        if current_value <= min_val * 1.05:
            trend = "at_historic_low"
        elif current_value < avg * 0.85:
            trend = "below_average"
        elif current_value > max_val * 0.95:
            trend = "at_historic_high"
        elif current_value > avg * 1.15:
            trend = "above_average"
        else:
            trend = "average"
        
        # Find similar periods
        similar = self._find_similar_periods(indicator_code, current_value, history)
        
        return TrendContext(
            indicator_code=indicator_code,
            current_value=current_value,
            historical_average=avg,
            historical_min=min_val,
            historical_max=max_val,
            percentile_historically=percentile,
            trend_vs_history=trend,
            similar_periods=similar,
        )
    
    def predict_event_impact(
        self,
        current_indicators: Dict[str, float],
        industry: str,
        event_category: str,
    ) -> Dict[str, Any]:
        """
        Predict impact based on historical patterns.
        
        Args:
            current_indicators: Current indicator values
            industry: Company's industry
            event_category: Type of event (e.g., 'fuel_crisis', 'transport_disruption')
            
        Returns:
            Impact prediction based on historical data
        """
        # Find similar historical events
        matches = self.find_similar_events(
            current_indicators=current_indicators,
            category=event_category,
            top_n=3,
        )
        
        if not matches:
            return {
                "has_historical_precedent": False,
                "prediction_confidence": 0.0,
                "message": "No similar historical events found",
            }
        
        # Aggregate predictions from matches
        predicted_durations = []
        predicted_impacts = []
        
        for match in matches:
            weight = match.similarity_score
            predicted_durations.append((match.predicted_duration_days, weight))
            
            if industry in match.predicted_impact:
                predicted_impacts.append((match.predicted_impact[industry], weight))
        
        # Weighted average duration
        total_weight = sum(w for _, w in predicted_durations)
        avg_duration = sum(d * w for d, w in predicted_durations) / total_weight if total_weight > 0 else 7
        
        # Weighted average impact
        if predicted_impacts:
            impact_weight = sum(w for _, w in predicted_impacts)
            avg_impact = sum(i * w for i, w in predicted_impacts) / impact_weight if impact_weight > 0 else 0
        else:
            avg_impact = None
        
        # Top match for context
        top_match = matches[0]
        
        return {
            "has_historical_precedent": True,
            "prediction_confidence": top_match.similarity_score,
            "predicted_duration_days": round(avg_duration),
            "predicted_impact_percent": round(avg_impact * 100, 1) if avg_impact else None,
            "most_similar_event": {
                "name": top_match.event.event_name,
                "date": top_match.event.start_date.strftime("%Y-%m-%d"),
                "outcome": top_match.event.description,
                "similarity": round(top_match.similarity_score * 100),
            },
            "historical_range": {
                "shortest_duration": min(m.predicted_duration_days for m in matches),
                "longest_duration": max(m.predicted_duration_days for m in matches),
            },
            "lessons_learned": top_match.event.mitigating_factors[:3] if top_match.event.mitigating_factors else [],
        }
    
    def get_leading_indicator_context(
        self,
        current_indicators: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Identify leading indicators that historically preceded problems.
        
        Args:
            current_indicators: Current indicator values
            
        Returns:
            Analysis of potential leading indicators
        """
        warnings = []
        
        # Check each indicator against historical patterns
        for indicator_code, current_value in current_indicators.items():
            context = self.get_historical_context(indicator_code, current_value)
            
            # Flag if at historic extremes
            if context.trend_vs_history == "at_historic_low":
                warnings.append({
                    "indicator": indicator_code,
                    "current_value": current_value,
                    "status": "historic_low",
                    "message": f"{indicator_code} is at historic lows, similar to periods that preceded past crises",
                    "similar_periods": context.similar_periods[:2],
                })
            elif context.trend_vs_history == "below_average" and context.percentile_historically < 20:
                warnings.append({
                    "indicator": indicator_code,
                    "current_value": current_value,
                    "status": "concerning",
                    "message": f"{indicator_code} is in the bottom 20% historically",
                    "similar_periods": context.similar_periods[:2],
                })
        
        # Sort by severity
        warnings.sort(key=lambda w: w["status"] == "historic_low", reverse=True)
        
        return {
            "analysis_date": datetime.now(),
            "indicators_analyzed": len(current_indicators),
            "warnings_found": len(warnings),
            "warnings": warnings,
            "overall_assessment": self._assess_overall_risk(warnings),
        }
    
    def _calculate_similarity(
        self,
        current: Dict[str, float],
        historical: Dict[str, float],
    ) -> float:
        """
        Calculate similarity between current and historical indicator profiles.
        Uses cosine similarity with weighted differences.
        """
        # Find common indicators
        common_keys = set(current.keys()) & set(historical.keys())
        
        if not common_keys:
            return 0.0
        
        # Calculate weighted similarity
        total_similarity = 0.0
        total_weight = 0.0
        
        for key in common_keys:
            current_val = current[key]
            historical_val = historical[key]
            
            # Calculate difference (normalized 0-1)
            diff = abs(current_val - historical_val)
            similarity = 1 - diff
            
            # Weight by indicator importance (could be enhanced)
            weight = 1.0
            if "SUPPLY" in key or "POWER" in key:
                weight = 1.5  # Higher weight for critical indicators
            
            total_similarity += similarity * weight
            total_weight += weight
        
        # Coverage bonus - reward having more matching indicators
        coverage = len(common_keys) / max(len(current), len(historical))
        
        base_similarity = total_similarity / total_weight if total_weight > 0 else 0
        final_similarity = base_similarity * (0.7 + 0.3 * coverage)
        
        return min(1.0, final_similarity)
    
    def _create_match(
        self,
        event: HistoricalEvent,
        similarity: float,
        current_indicators: Dict[str, float],
        industry: Optional[str],
    ) -> HistoricalMatch:
        """Create a HistoricalMatch object from event and current indicators."""
        # Find matching indicators
        matching = []
        for key in set(current_indicators.keys()) & set(event.indicator_profile.keys()):
            matching.append((
                key,
                current_indicators[key],
                event.indicator_profile[key],
            ))
        
        # Identify key differences
        differences = []
        for indicator, current, historical in matching:
            if abs(current - historical) > 0.2:
                direction = "higher" if current > historical else "lower"
                differences.append(f"{indicator} is {direction} now than during {event.event_name}")
        
        # Predict impact for industry
        predicted_impact = {}
        if industry and industry in event.business_impacts:
            impact_data = event.business_impacts[industry]
            predicted_impact[industry] = impact_data.get("revenue_impact", 0)
        
        # Generate relevance narrative
        narrative = self._generate_relevance_narrative(event, similarity, differences)
        
        return HistoricalMatch(
            event=event,
            similarity_score=similarity,
            matching_indicators=matching,
            key_differences=differences,
            predicted_duration_days=event.duration_days,
            predicted_severity=event.severity,
            predicted_impact=predicted_impact,
            time_since_event=(datetime.now() - event.start_date).days,
            relevance_narrative=narrative,
        )
    
    def _generate_relevance_narrative(
        self,
        event: HistoricalEvent,
        similarity: float,
        differences: List[str],
    ) -> str:
        """Generate a narrative explaining the relevance of historical match."""
        similarity_pct = int(similarity * 100)
        
        if similarity >= 0.8:
            base = f"Current conditions closely mirror the {event.event_name} ({event.start_date.strftime('%b %Y')})"
        elif similarity >= 0.6:
            base = f"Current conditions are similar to the {event.event_name} ({event.start_date.strftime('%b %Y')})"
        else:
            base = f"Some parallels exist with the {event.event_name} ({event.start_date.strftime('%b %Y')})"
        
        base += f" with {similarity_pct}% similarity."
        
        if differences:
            base += f" Key difference: {differences[0]}."
        
        if event.duration_days:
            base += f" That event lasted {event.duration_days} days."
        
        return base
    
    def _find_similar_periods(
        self,
        indicator_code: str,
        current_value: float,
        history: List[Dict[str, Any]],
        tolerance: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """Find historical periods with similar indicator values."""
        similar = []
        
        for entry in history:
            if abs(entry["value"] - current_value) <= tolerance:
                similar.append({
                    "date": entry["date"],
                    "value": entry["value"],
                    "what_followed": entry.get("outcome", "Unknown"),
                })
        
        return similar[:5]  # Return top 5
    
    def _assess_overall_risk(self, warnings: List[Dict[str, Any]]) -> str:
        """Assess overall risk level based on warnings."""
        if not warnings:
            return "Indicators are within normal historical ranges."
        
        historic_lows = sum(1 for w in warnings if w["status"] == "historic_low")
        
        if historic_lows >= 3:
            return "ELEVATED: Multiple indicators at historic lows - similar patterns preceded past crises."
        elif historic_lows >= 1:
            return "CAUTION: Some indicators at concerning levels historically."
        else:
            return "MONITORING: Some indicators below average but not at critical levels."
    
    def _load_historical_events(self) -> List[HistoricalEvent]:
        """Load historical events database."""
        return [
            HistoricalEvent(
                event_id="evt_fuel_2022",
                event_type="fuel_crisis",
                event_name="2022 Fuel Shortage Crisis",
                category="supply_chain",
                start_date=datetime(2022, 5, 15),
                end_date=datetime(2022, 5, 27),
                duration_days=12,
                indicator_profile={
                    "OPS_TRANSPORT_AVAIL": 0.35,
                    "OPS_SUPPLY_CHAIN": 0.40,
                    "OPS_POWER_RELIABILITY": 0.55,
                },
                severity="severe",
                description="Nationwide fuel shortage causing widespread delivery delays",
                business_impacts={
                    "retail": {"revenue_impact": -0.30, "duration_days": 12},
                    "logistics": {"revenue_impact": -0.45, "duration_days": 12},
                    "manufacturing": {"revenue_impact": -0.20, "duration_days": 8},
                },
                leading_indicators=[
                    "Government fuel distribution issues reported 5 days prior",
                    "Queue lengths increasing 3 days prior",
                ],
                mitigating_factors=[
                    "Companies with alternative fuel arrangements recovered faster",
                    "Remote work policies reduced impact",
                ],
                aggravating_factors=[
                    "Single fuel supplier dependency",
                    "No contingency inventory",
                ],
                tags=["fuel", "transport", "crisis", "supply_chain"],
            ),
            HistoricalEvent(
                event_id="evt_power_2022",
                event_type="power_crisis",
                event_name="2022 Power Outage Period",
                category="infrastructure",
                start_date=datetime(2022, 6, 1),
                end_date=datetime(2022, 6, 15),
                duration_days=14,
                indicator_profile={
                    "OPS_POWER_RELIABILITY": 0.30,
                    "OPS_PRODUCTION_CAP": 0.45,
                    "OPS_EQUIPMENT_STATUS": 0.50,
                },
                severity="severe",
                description="Extended power outages affecting operations nationwide",
                business_impacts={
                    "manufacturing": {"revenue_impact": -0.35, "duration_days": 14},
                    "retail": {"revenue_impact": -0.20, "duration_days": 14},
                    "hospitality": {"revenue_impact": -0.25, "duration_days": 14},
                },
                leading_indicators=[
                    "Grid capacity warnings 7 days prior",
                    "Industrial power allocation cuts announced",
                ],
                mitigating_factors=[
                    "Backup generator capacity",
                    "Flexible shift scheduling",
                ],
                aggravating_factors=[
                    "Heavy machinery requiring continuous power",
                    "Cold storage dependencies",
                ],
                tags=["power", "infrastructure", "crisis"],
            ),
            HistoricalEvent(
                event_id="evt_strike_2022",
                event_type="labor_action",
                event_name="2022 Transport Strike",
                category="operational",
                start_date=datetime(2022, 7, 10),
                end_date=datetime(2022, 7, 15),
                duration_days=5,
                indicator_profile={
                    "OPS_TRANSPORT_AVAIL": 0.25,
                    "OPS_LABOR_AVAIL": 0.40,
                    "OPS_SUPPLY_CHAIN": 0.50,
                },
                severity="major",
                description="Transport worker strike disrupting logistics",
                business_impacts={
                    "logistics": {"revenue_impact": -0.60, "duration_days": 5},
                    "retail": {"revenue_impact": -0.15, "duration_days": 5},
                    "manufacturing": {"revenue_impact": -0.10, "duration_days": 5},
                },
                leading_indicators=[
                    "Union negotiations broke down 3 days prior",
                    "Strike notice issued 2 days prior",
                ],
                mitigating_factors=[
                    "Pre-positioned inventory",
                    "Alternative transport arrangements",
                ],
                aggravating_factors=[
                    "Just-in-time inventory model",
                    "Single transport provider dependency",
                ],
                tags=["strike", "labor", "transport", "logistics"],
            ),
            HistoricalEvent(
                event_id="evt_currency_2022",
                event_type="currency_crisis",
                event_name="2022 Currency Depreciation",
                category="financial",
                start_date=datetime(2022, 4, 1),
                end_date=datetime(2022, 6, 30),
                duration_days=90,
                indicator_profile={
                    "OPS_INPUT_COSTS": 0.25,
                    "OPS_PRICING_POWER": 0.60,
                    "OPS_CREDIT_ACCESS": 0.40,
                },
                severity="severe",
                description="Significant currency depreciation increasing import costs",
                business_impacts={
                    "retail": {"revenue_impact": -0.15, "duration_days": 90},
                    "manufacturing": {"revenue_impact": -0.25, "duration_days": 90},
                    "hospitality": {"revenue_impact": 0.10, "duration_days": 90},  # Benefited from tourism
                },
                leading_indicators=[
                    "Foreign reserve depletion warnings",
                    "Import cover falling below 2 months",
                ],
                mitigating_factors=[
                    "Export revenue provided hedge",
                    "Local sourcing reduced impact",
                ],
                aggravating_factors=[
                    "High import dependency",
                    "USD-denominated loans",
                ],
                tags=["currency", "financial", "imports", "costs"],
            ),
            HistoricalEvent(
                event_id="evt_demand_recovery_2023",
                event_type="demand_surge",
                event_name="2023 Tourism Recovery",
                category="market",
                start_date=datetime(2023, 3, 1),
                end_date=datetime(2023, 6, 30),
                duration_days=120,
                indicator_profile={
                    "OPS_DEMAND_LEVEL": 0.85,
                    "OPS_LABOR_AVAIL": 0.60,
                    "OPS_PRICING_POWER": 0.80,
                },
                severity="moderate",  # Positive event
                description="Strong tourism recovery creating demand surge",
                business_impacts={
                    "hospitality": {"revenue_impact": 0.40, "duration_days": 120},
                    "retail": {"revenue_impact": 0.15, "duration_days": 120},
                    "logistics": {"revenue_impact": 0.10, "duration_days": 120},
                },
                leading_indicators=[
                    "Visa approval numbers increasing 30 days prior",
                    "Flight bookings surge 45 days prior",
                ],
                mitigating_factors=[],  # Positive event
                aggravating_factors=[
                    "Staff shortage limited capacity",
                    "Supply chain couldn't scale fast enough",
                ],
                tags=["tourism", "demand", "recovery", "positive"],
            ),
        ]
    
    def _load_indicator_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load indicator historical data."""
        # Simulated historical data - in production, from database
        base_date = datetime.now() - timedelta(days=365)
        
        history = {}
        indicators = ["OPS_SUPPLY_CHAIN", "OPS_POWER_RELIABILITY", "OPS_TRANSPORT_AVAIL", 
                      "OPS_LABOR_AVAIL", "OPS_DEMAND_LEVEL"]
        
        import random
        random.seed(42)  # For reproducibility
        
        for indicator in indicators:
            history[indicator] = []
            base_value = 0.7
            
            for i in range(365):
                date = base_date + timedelta(days=i)
                # Add some variation
                value = base_value + random.gauss(0, 0.1)
                value = max(0.2, min(0.95, value))
                
                # Simulate the 2022 crisis period (around day 60-100)
                if 60 <= i <= 100:
                    value -= 0.3
                    value = max(0.2, value)
                
                history[indicator].append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": round(value, 2),
                    "outcome": "Crisis period" if 60 <= i <= 100 else "Normal operations",
                })
        
        return history


# Export for easy importing
__all__ = [
    "HistoricalContextAnalyzer",
    "HistoricalEvent",
    "HistoricalMatch",
    "TrendContext",
]
