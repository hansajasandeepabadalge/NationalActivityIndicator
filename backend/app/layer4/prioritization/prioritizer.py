"""
Layer 4: Insight Prioritization Engine

Combines risks and opportunities into a unified, ranked priority list.
Helps business leaders focus on what matters most.

Key Features:
- Unified scoring across risks and opportunities
- Actionability assessment
- Strategic importance weighting
- Urgency-based ranking
- Top N priorities extraction
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from decimal import Decimal

from app.layer4.schemas.risk_schemas import DetectedRisk
from app.layer4.schemas.opportunity_schemas import DetectedOpportunity
from app.layer4.schemas.insight_schemas import (
    InsightPriority,
    TopPriorities,
)

logger = logging.getLogger(__name__)


class PrioritizedInsight:
    """Internal representation of a prioritized insight"""
    
    def __init__(
        self,
        insight_id: int,
        company_id: str,
        insight_type: str,
        title: str,
        description: str,
        category: str,
        final_score: Decimal,
        severity_level: str,
        urgency: int,
        confidence: Decimal,
        triggering_indicators: Dict[str, Any],
        detected_at: datetime,
        status: str = "active",
    ):
        self.insight_id = insight_id
        self.company_id = company_id
        self.insight_type = insight_type
        self.title = title
        self.description = description
        self.category = category
        self.final_score = final_score
        self.severity_level = severity_level
        self.urgency = urgency
        self.confidence = confidence
        self.triggering_indicators = triggering_indicators
        self.detected_at = detected_at
        self.status = status
        
        # Computed fields
        self.priority_rank: int = 0
        self.is_urgent: bool = False
        self.requires_immediate_action: bool = False
        self.actionability_score: Decimal = Decimal("0.5")
        self.strategic_importance: Decimal = Decimal("0.5")
        self.priority_score: Decimal = Decimal("0.0")


class InsightPrioritizer:
    """
    Prioritization Engine for Business Insights
    
    Combines risks and opportunities into a unified priority list,
    scoring each based on:
    - Severity/Value (from the insight's final score)
    - Urgency (time sensitivity)
    - Actionability (can we do something about it?)
    - Strategic importance (alignment with business goals)
    
    Output: Ranked list with top priorities highlighted
    """
    
    def __init__(self, company_profile: Optional[Dict[str, Any]] = None):
        """
        Initialize the prioritizer.
        
        Args:
            company_profile: Optional company context for customization
        """
        self.company_profile = company_profile or {}
        
        # Configurable weights for priority calculation
        self.urgency_weight = 0.30
        self.actionability_weight = 0.25
        self.severity_weight = 0.25
        self.strategic_weight = 0.15
        self.time_sensitivity_weight = 0.05
        
        # Legacy weights dict for backwards compatibility
        self.weights = {
            "base_score": 0.40,      # Raw risk/opportunity score
            "urgency": 0.25,         # Time sensitivity
            "actionability": 0.20,   # Can we act on it?
            "strategic": 0.15,       # Strategic alignment
        }
        
        # Category actionability scores (how much can we influence)
        self.category_actionability = {
            # Risk categories
            "operational": 0.90,     # Highly actionable
            "infrastructure": 0.85,
            "supply_chain": 0.80,
            "workforce": 0.75,
            "financial": 0.70,
            "competitive": 0.50,     # Less controllable
            "reputational": 0.65,
            "compliance": 0.60,
            "strategic": 0.55,
            # Opportunity categories
            "market": 0.75,
            "market_expansion": 0.70,
            "cost_reduction": 0.85,
            "talent": 0.70,
            "innovation": 0.65,
            "growth": 0.70,
            "technology": 0.75,
        }
        
        # Strategic importance by category
        self.category_strategic_importance = {
            # Risk categories
            "operational": 0.85,
            "infrastructure": 0.80,
            "supply_chain": 0.90,
            "workforce": 0.75,
            "financial": 0.95,
            "competitive": 0.85,
            "reputational": 0.80,
            "compliance": 0.70,
            "strategic": 1.00,
            # Opportunity categories
            "market": 0.90,
            "market_expansion": 0.85,
            "cost_reduction": 0.80,
            "talent": 0.70,
            "innovation": 0.85,
            "growth": 0.95,
            "technology": 0.80,
        }
        
        logger.info("Initialized InsightPrioritizer")
    
    def prioritize(
        self,
        risks: List[DetectedRisk],
        opportunities: List[DetectedOpportunity],
        top_n: int = 5,
        include_all: bool = False,
    ) -> TopPriorities:
        """
        Prioritize all insights and return top priorities.
        
        Args:
            risks: List of detected risks
            opportunities: List of detected opportunities
            top_n: Number of top priorities to return (default 5, max 5)
            include_all: Deprecated - use prioritize_all() method instead
            
        Returns:
            TopPriorities object with ranked insights (max 5 due to schema)
        """
        all_insights: List[PrioritizedInsight] = []
        
        # Convert risks to prioritized insights
        for i, risk in enumerate(risks):
            insight = self._risk_to_prioritized_insight(risk, i + 1)
            self._calculate_priority_score(insight)
            all_insights.append(insight)
        
        # Convert opportunities to prioritized insights
        for i, opp in enumerate(opportunities):
            insight = self._opportunity_to_prioritized_insight(opp, len(risks) + i + 1)
            self._calculate_priority_score(insight)
            all_insights.append(insight)
        
        # Sort by priority score (highest first)
        all_insights.sort(key=lambda x: float(x.priority_score), reverse=True)
        
        # Assign ranks
        for rank, insight in enumerate(all_insights, 1):
            insight.priority_rank = rank
            # Mark top 3 as urgent
            if rank <= 3 and insight.severity_level in ["critical", "high"]:
                insight.is_urgent = True
            # Mark critical items as requiring immediate action
            if insight.severity_level == "critical":
                insight.requires_immediate_action = True
        
        # Get company_id from first insight or default
        company_id = all_insights[0].company_id if all_insights else "UNKNOWN"
        
        # Build response - always limited to top_n (max 5 per schema)
        # Note: TopPriorities schema has max_length=5 constraint
        limited_top_n = min(top_n, 5)  # Schema limits to 5
        priorities = []
        items_to_include = all_insights[:limited_top_n]
        
        for insight in items_to_include:
            priorities.append(InsightPriority(
                insight_id=insight.insight_id,
                company_id=insight.company_id,
                insight_type=insight.insight_type,
                title=insight.title,
                category=insight.category,
                final_score=insight.final_score,
                severity_level=insight.severity_level,
                priority_rank=insight.priority_rank,
                is_urgent=insight.is_urgent,
                requires_immediate_action=insight.requires_immediate_action,
                actionability_score=insight.actionability_score,
                strategic_importance=insight.strategic_importance,
                priority_score=insight.priority_score,
                detected_at=insight.detected_at,
                status=insight.status,
            ))
        
        return TopPriorities(
            company_id=company_id,
            as_of=datetime.now(),
            total_active_insights=len(all_insights),
            total_risks=len(risks),
            total_opportunities=len(opportunities),
            priorities=priorities,
        )
    
    def prioritize_all(
        self,
        risks: List[DetectedRisk],
        opportunities: List[DetectedOpportunity],
        company_profile: Optional[Dict[str, Any]] = None,
    ) -> List[InsightPriority]:
        """
        Prioritize all insights and return all as a list.
        
        This method does not use TopPriorities wrapper since that has a max_length=5.
        Instead, it directly calculates priorities and returns them as a list.
        
        Args:
            risks: List of detected risks
            opportunities: List of detected opportunities
            company_profile: Optional company context (updates internal profile)
            
        Returns:
            List of all prioritized insights, sorted by priority score
        """
        # Update company profile if provided
        if company_profile:
            self.company_profile = company_profile
        
        all_insights: List[PrioritizedInsight] = []
        
        # Convert risks to prioritized insights
        for i, risk in enumerate(risks):
            insight = self._risk_to_prioritized_insight(risk, i + 1)
            self._calculate_priority_score(insight)
            all_insights.append(insight)
        
        # Convert opportunities to prioritized insights
        for i, opp in enumerate(opportunities):
            insight = self._opportunity_to_prioritized_insight(opp, len(risks) + i + 1)
            self._calculate_priority_score(insight)
            all_insights.append(insight)
        
        # Sort by priority score (highest first)
        all_insights.sort(key=lambda x: float(x.priority_score), reverse=True)
        
        # Assign ranks and urgent flags
        for rank, insight in enumerate(all_insights, 1):
            insight.priority_rank = rank
            if rank <= 3 and insight.severity_level in ["critical", "high"]:
                insight.is_urgent = True
            if insight.severity_level == "critical":
                insight.requires_immediate_action = True
        
        # Convert to InsightPriority objects
        priorities = []
        for insight in all_insights:
            priorities.append(InsightPriority(
                insight_id=insight.insight_id,
                company_id=insight.company_id,
                insight_type=insight.insight_type,
                title=insight.title,
                category=insight.category,
                final_score=insight.final_score,
                severity_level=insight.severity_level,
                priority_rank=insight.priority_rank,
                is_urgent=insight.is_urgent,
                requires_immediate_action=insight.requires_immediate_action,
                actionability_score=insight.actionability_score,
                strategic_importance=insight.strategic_importance,
                priority_score=insight.priority_score,
                detected_at=insight.detected_at,
                status=insight.status,
            ))
        
        return priorities
    
    def get_top_priorities(
        self,
        risks: List[DetectedRisk],
        opportunities: List[DetectedOpportunity],
        company_profile: Optional[Dict[str, Any]] = None,
        limit: int = 5,
    ) -> TopPriorities:
        """
        Get the top N priorities combining risks and opportunities.
        
        This is a convenience wrapper around prioritize() that allows
        specifying a limit parameter and optional company profile.
        
        Args:
            risks: List of detected risks
            opportunities: List of detected opportunities
            company_profile: Optional company context (updates internal profile)
            limit: Number of top priorities to return (default 5)
            
        Returns:
            TopPriorities object with the top ranked insights
        """
        # Update company profile if provided
        if company_profile:
            self.company_profile = company_profile
        
        return self.prioritize(risks, opportunities, top_n=limit)
    
    def prioritize_risks_only(
        self,
        risks: List[DetectedRisk],
        top_n: int = 5,
    ) -> List[InsightPriority]:
        """
        Prioritize only risks.
        
        Args:
            risks: List of detected risks
            top_n: Number of top priorities to return
            
        Returns:
            List of prioritized risks
        """
        result = self.prioritize(risks, [], top_n=top_n)
        return result.priorities
    
    def prioritize_opportunities_only(
        self,
        opportunities: List[DetectedOpportunity],
        top_n: int = 5,
    ) -> List[InsightPriority]:
        """
        Prioritize only opportunities.
        
        Args:
            opportunities: List of detected opportunities
            top_n: Number of top priorities to return
            
        Returns:
            List of prioritized opportunities
        """
        result = self.prioritize([], opportunities, top_n=top_n)
        return result.priorities
    
    def get_urgent_items(
        self,
        risks: List[DetectedRisk],
        opportunities: List[DetectedOpportunity],
    ) -> List[InsightPriority]:
        """
        Get only urgent items requiring immediate attention.
        
        Args:
            risks: List of detected risks
            opportunities: List of detected opportunities
            
        Returns:
            List of urgent prioritized insights
        """
        all_priorities = self.prioritize_all(risks, opportunities)
        return [p for p in all_priorities if p.is_urgent or p.requires_immediate_action]
    
    def get_by_category(
        self,
        risks: List[DetectedRisk],
        opportunities: List[DetectedOpportunity],
        category: str,
        top_n: int = 5,
    ) -> List[InsightPriority]:
        """
        Get prioritized items filtered by category.
        
        Args:
            risks: List of detected risks
            opportunities: List of detected opportunities
            category: Category to filter by
            top_n: Number of top priorities to return
            
        Returns:
            List of prioritized insights in that category
        """
        all_priorities = self.prioritize_all(risks, opportunities)
        filtered = [p for p in all_priorities if p.category == category]
        return filtered[:top_n]
    
    def get_by_severity(
        self,
        risks: List[DetectedRisk],
        opportunities: List[DetectedOpportunity],
        severity: str,
        top_n: int = 10,
    ) -> List[InsightPriority]:
        """
        Get prioritized items filtered by severity level.
        
        Args:
            risks: List of detected risks
            opportunities: List of detected opportunities
            severity: Severity level to filter by (critical, high, medium, low)
            top_n: Number of top priorities to return
            
        Returns:
            List of prioritized insights at that severity
        """
        all_priorities = self.prioritize_all(risks, opportunities)
        filtered = [p for p in all_priorities if p.severity_level == severity]
        return filtered[:top_n]
    
    def _risk_to_prioritized_insight(
        self,
        risk: DetectedRisk,
        insight_id: int,
    ) -> PrioritizedInsight:
        """Convert DetectedRisk to PrioritizedInsight"""
        return PrioritizedInsight(
            insight_id=insight_id,
            company_id=risk.company_id,
            insight_type="risk",
            title=risk.title,
            description=risk.description,
            category=risk.category,
            final_score=risk.final_score,
            severity_level=risk.severity_level,
            urgency=risk.urgency,
            confidence=risk.confidence,
            triggering_indicators=risk.triggering_indicators,
            detected_at=datetime.now(),
            status="active",
        )
    
    def _opportunity_to_prioritized_insight(
        self,
        opp: DetectedOpportunity,
        insight_id: int,
    ) -> PrioritizedInsight:
        """Convert DetectedOpportunity to PrioritizedInsight"""
        # Map opportunity priority_level to severity_level
        priority_to_severity = {
            "high": "high",
            "medium": "medium",
            "low": "low",
        }
        severity = priority_to_severity.get(opp.priority_level, "medium")
        
        # Map timing_score to urgency (1-5)
        urgency = max(1, min(5, int(float(opp.timing_score) * 5) + 1))
        
        return PrioritizedInsight(
            insight_id=insight_id,
            company_id=opp.company_id,
            insight_type="opportunity",
            title=opp.title,
            description=opp.description,
            category=opp.category,
            final_score=opp.final_score,
            severity_level=severity,
            urgency=urgency,
            confidence=opp.feasibility,  # Use feasibility as confidence proxy
            triggering_indicators=opp.triggering_indicators,
            detected_at=datetime.now(),
            status="identified",
        )
    
    def _calculate_priority_score(self, insight: PrioritizedInsight) -> None:
        """
        Calculate the unified priority score for an insight.
        
        Formula:
        Priority = (Base × W1) + (Urgency × W2) + (Actionability × W3) + (Strategic × W4)
        
        Where:
        - Base: Normalized final score (0-100)
        - Urgency: Urgency factor (0-100)
        - Actionability: How actionable (0-100)
        - Strategic: Strategic importance (0-100)
        """
        # 1. Base Score (normalize to 0-100)
        if insight.insight_type == "risk":
            # Risk scores are typically 0-50
            base_score = min(float(insight.final_score) * 2, 100)
        else:
            # Opportunity scores are 0-10
            base_score = min(float(insight.final_score) * 10, 100)
        
        # 2. Urgency Score (1-5 → 0-100)
        urgency_score = (insight.urgency / 5.0) * 100
        
        # 3. Actionability Score
        actionability = self.category_actionability.get(
            insight.category,
            0.6  # Default moderate actionability
        )
        insight.actionability_score = Decimal(str(actionability))
        actionability_score = actionability * 100
        
        # 4. Strategic Importance Score
        strategic = self.category_strategic_importance.get(
            insight.category,
            0.7  # Default moderate importance
        )
        insight.strategic_importance = Decimal(str(strategic))
        strategic_score = strategic * 100
        
        # Apply company-specific adjustments if available
        if self.company_profile:
            base_score = self._apply_company_adjustments(
                insight, base_score, actionability_score, strategic_score
            )
        
        # Calculate weighted priority score
        priority_score = (
            base_score * self.weights["base_score"] +
            urgency_score * self.weights["urgency"] +
            actionability_score * self.weights["actionability"] +
            strategic_score * self.weights["strategic"]
        )
        
        # Boost for critical severity
        if insight.severity_level == "critical":
            priority_score *= 1.2
        elif insight.severity_level == "high":
            priority_score *= 1.1
        
        insight.priority_score = Decimal(str(round(priority_score, 2)))
    
    def _apply_company_adjustments(
        self,
        insight: PrioritizedInsight,
        base_score: float,
        actionability: float,
        strategic: float,
    ) -> float:
        """
        Apply company-specific adjustments to scoring.
        
        Factors considered:
        - Industry relevance
        - Business scale
        - Risk appetite
        - Strategic priorities
        """
        adjusted_score = base_score
        
        # Industry relevance
        company_industry = self.company_profile.get("industry", "")
        if company_industry:
            # Supply chain risks more important for retail/manufacturing
            if insight.category == "supply_chain" and company_industry in ["retail", "manufacturing"]:
                adjusted_score *= 1.15
            
            # Financial risks more important for services
            if insight.category == "financial" and company_industry in ["services", "hospitality"]:
                adjusted_score *= 1.10
        
        # Risk appetite adjustment
        risk_appetite = self.company_profile.get("risk_appetite", "moderate")
        if risk_appetite == "conservative":
            # Boost risk scores for conservative companies
            if insight.insight_type == "risk":
                adjusted_score *= 1.15
        elif risk_appetite == "aggressive":
            # Boost opportunity scores for aggressive companies
            if insight.insight_type == "opportunity":
                adjusted_score *= 1.15
        
        # Strategic priorities
        strategic_priorities = self.company_profile.get("strategic_priorities", [])
        if "cost_reduction" in strategic_priorities and insight.category == "cost_reduction":
            adjusted_score *= 1.20
        if "growth" in strategic_priorities and insight.category in ["market", "market_expansion", "growth"]:
            adjusted_score *= 1.20
        
        return adjusted_score
    
    def calculate_priority_summary(
        self,
        risks: List[DetectedRisk],
        opportunities: List[DetectedOpportunity],
    ) -> Dict[str, Any]:
        """
        Calculate a summary of priorities.
        
        Args:
            risks: List of detected risks
            opportunities: List of detected opportunities
            
        Returns:
            Summary statistics about priorities
        """
        all_priorities = self.prioritize_all(risks, opportunities)
        
        # Count by type
        risk_count = sum(1 for p in all_priorities if p.insight_type == "risk")
        opp_count = sum(1 for p in all_priorities if p.insight_type == "opportunity")
        
        # Count by severity
        critical_count = sum(1 for p in all_priorities if p.severity_level == "critical")
        high_count = sum(1 for p in all_priorities if p.severity_level == "high")
        medium_count = sum(1 for p in all_priorities if p.severity_level == "medium")
        low_count = sum(1 for p in all_priorities if p.severity_level == "low")
        
        # Count urgent
        urgent_count = sum(1 for p in all_priorities if p.is_urgent)
        immediate_count = sum(1 for p in all_priorities if p.requires_immediate_action)
        
        # Category breakdown
        categories = {}
        for p in all_priorities:
            categories[p.category] = categories.get(p.category, 0) + 1
        
        return {
            "total_insights": len(all_priorities),
            "total_risks": risk_count,
            "total_opportunities": opp_count,
            "by_severity": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
            },
            "urgent_items": urgent_count,
            "requires_immediate_action": immediate_count,
            "by_category": categories,
            "top_priority": all_priorities[0] if all_priorities else None,
            "average_priority_score": (
                sum(float(p.priority_score) for p in all_priorities) / len(all_priorities)
                if all_priorities else 0
            ),
        }


# Export for easy importing
__all__ = ["InsightPrioritizer", "PrioritizedInsight"]
