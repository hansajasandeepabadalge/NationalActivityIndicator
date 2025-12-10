"""
Layer 4: PostgreSQL Storage Service for Business Insights

Handles persistence of:
- Business insights (risks and opportunities)
- Recommendations
- Insight tracking (TimescaleDB)
- Score history (TimescaleDB)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from decimal import Decimal
import logging

from app.models.business_insight_models import (
    BusinessInsight,
    InsightRecommendation,
    InsightTracking,
    InsightScoreHistory,
    InsightFeedback
)
from app.layer4.schemas.risk_schemas import DetectedRisk
from app.layer4.schemas.opportunity_schemas import DetectedOpportunity

logger = logging.getLogger(__name__)


class InsightStorageService:
    """
    PostgreSQL storage for business insights and recommendations

    Features:
    - Stores risks and opportunities
    - Manages recommendations
    - Tracks score evolution (TimescaleDB)
    - Handles daily snapshots (TimescaleDB)
    - De-duplicates insights
    """

    def __init__(self, db: Session):
        self.db = db

    def store_business_insight(
        self,
        risk: DetectedRisk,
        company_id: str,
        definition_id: Optional[int] = None
    ) -> int:
        """
        Save DetectedRisk to BusinessInsight table

        Args:
            risk: Detected risk to store
            company_id: Company identifier
            definition_id: Optional reference to risk definition

        Returns:
            insight_id of stored/updated insight
        """
        # Check for duplicate (same risk_code, company_id, detected today)
        existing = self._find_duplicate(company_id, risk.risk_code)

        if existing:
            logger.info(f"Found existing insight {existing.insight_id} for {risk.risk_code}")
            return self._update_insight(existing, risk)

        # Create new BusinessInsight record
        insight = BusinessInsight(
            definition_id=definition_id,
            company_id=company_id,
            insight_type='risk',
            category=risk.category,
            title=risk.title,
            description=risk.description,
            probability=risk.probability,
            impact=risk.impact,
            urgency=risk.urgency,
            confidence=risk.confidence,
            final_score=risk.final_score,
            severity_level=risk.severity_level,
            detected_at=datetime.now(),
            expected_impact_time=risk.expected_impact_time,
            expected_duration_hours=risk.expected_duration_hours,
            status='active',
            triggering_indicators=risk.triggering_indicators if isinstance(risk.triggering_indicators, dict) else {},
            is_urgent=risk.is_urgent,
            requires_immediate_action=risk.requires_immediate_action
        )

        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)

        logger.info(f"Stored new insight {insight.insight_id}: {risk.risk_code} for company {company_id}")

        # Store score history
        self._store_score_history(insight)

        return insight.insight_id

    def store_opportunity_insight(
        self,
        opportunity: DetectedOpportunity,
        company_id: str,
        definition_id: Optional[int] = None
    ) -> int:
        """
        Save DetectedOpportunity to BusinessInsight table

        Args:
            opportunity: Detected opportunity to store
            company_id: Company identifier
            definition_id: Optional reference to opportunity definition

        Returns:
            insight_id of stored/updated insight
        """
        # Check for duplicate
        existing = self._find_duplicate(company_id, opportunity.opportunity_code)

        if existing:
            logger.info(f"Found existing opportunity {existing.insight_id} for {opportunity.opportunity_code}")
            return self._update_opportunity_insight(existing, opportunity)

        # Create new BusinessInsight record
        insight = BusinessInsight(
            definition_id=definition_id,
            company_id=company_id,
            insight_type='opportunity',
            category=opportunity.category,
            title=opportunity.title,
            description=opportunity.description,
            probability=Decimal(str(opportunity.potential_value)),  # Map potential_value to probability field
            impact=Decimal(str(opportunity.feasibility * 10)),  # Map feasibility to impact (0-10 scale)
            urgency=opportunity.timing_score,
            confidence=Decimal(str(opportunity.strategic_fit)),
            final_score=opportunity.final_score,
            severity_level=opportunity.priority,  # Map priority to severity_level
            detected_at=datetime.now(),
            expected_duration_hours=opportunity.window_days * 24 if opportunity.window_days else None,
            status='active',
            triggering_indicators=opportunity.triggering_factors if isinstance(opportunity.triggering_factors, dict) else {},
            is_urgent=opportunity.timing_score >= 4,
            requires_immediate_action=opportunity.priority == 'high' and opportunity.timing_score >= 4
        )

        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)

        logger.info(f"Stored new opportunity {insight.insight_id}: {opportunity.opportunity_code} for company {company_id}")

        # Store score history
        self._store_score_history(insight)

        return insight.insight_id

    def store_recommendations(
        self,
        insight_id: int,
        recommendations: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Save recommendations to InsightRecommendation table

        Args:
            insight_id: ID of parent insight
            recommendations: List of recommendation dictionaries

        Returns:
            List of recommendation_ids
        """
        recommendation_ids = []

        for rec in recommendations:
            db_rec = InsightRecommendation(
                insight_id=insight_id,
                category=rec.get('category', 'immediate'),
                priority=rec.get('priority', 1),
                action_title=rec['action_title'],
                action_description=rec.get('action_description', ''),
                responsible_role=rec.get('responsible_role'),
                estimated_effort=rec.get('estimated_effort'),
                estimated_timeframe=rec.get('timeframe') or rec.get('estimated_timeframe'),
                expected_benefit=rec.get('expected_benefit'),
                status='pending'
            )
            self.db.add(db_rec)
            self.db.flush()  # Get ID without committing
            recommendation_ids.append(db_rec.recommendation_id)

        self.db.commit()
        logger.info(f"Stored {len(recommendation_ids)} recommendations for insight {insight_id}")

        return recommendation_ids

    def get_active_insights(
        self,
        company_id: str,
        insight_type: Optional[str] = None,
        severity_level: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[BusinessInsight]:
        """
        Retrieve active insights for a company

        Args:
            company_id: Company identifier
            insight_type: Optional filter ('risk' or 'opportunity')
            severity_level: Optional filter ('critical', 'high', 'medium', 'low')
            limit: Optional limit on results

        Returns:
            List of BusinessInsight records
        """
        query = self.db.query(BusinessInsight).filter(
            and_(
                BusinessInsight.company_id == company_id,
                BusinessInsight.status == 'active'
            )
        )

        if insight_type:
            query = query.filter(BusinessInsight.insight_type == insight_type)

        if severity_level:
            query = query.filter(BusinessInsight.severity_level == severity_level)

        query = query.order_by(BusinessInsight.final_score.desc())

        if limit:
            query = query.limit(limit)

        results = query.all()
        logger.debug(f"Retrieved {len(results)} active insights for company {company_id}")

        return results

    def get_insight_by_id(self, insight_id: int) -> Optional[BusinessInsight]:
        """Retrieve specific insight by ID"""
        return self.db.query(BusinessInsight).filter(
            BusinessInsight.insight_id == insight_id
        ).first()

    def get_recommendations_for_insight(self, insight_id: int) -> List[InsightRecommendation]:
        """Retrieve all recommendations for an insight"""
        return self.db.query(InsightRecommendation).filter(
            InsightRecommendation.insight_id == insight_id
        ).order_by(InsightRecommendation.priority).all()

    def acknowledge_insight(
        self,
        insight_id: int,
        acknowledged_by: str
    ) -> bool:
        """
        Mark insight as acknowledged

        Args:
            insight_id: ID of insight to acknowledge
            acknowledged_by: User who acknowledged

        Returns:
            True if successful
        """
        insight = self.get_insight_by_id(insight_id)

        if not insight:
            logger.warning(f"Insight {insight_id} not found for acknowledgement")
            return False

        insight.status = 'acknowledged'
        insight.acknowledged_at = datetime.now()
        insight.acknowledged_by = acknowledged_by

        self.db.commit()
        logger.info(f"Insight {insight_id} acknowledged by {acknowledged_by}")

        return True

    def resolve_insight(
        self,
        insight_id: int,
        resolution_notes: Optional[str] = None,
        actual_impact: Optional[str] = None
    ) -> bool:
        """
        Mark insight as resolved

        Args:
            insight_id: ID of insight to resolve
            resolution_notes: Optional resolution notes
            actual_impact: Optional actual impact description

        Returns:
            True if successful
        """
        insight = self.get_insight_by_id(insight_id)

        if not insight:
            logger.warning(f"Insight {insight_id} not found for resolution")
            return False

        insight.status = 'resolved'
        insight.resolved_at = datetime.now()
        insight.resolution_notes = resolution_notes
        insight.actual_impact = actual_impact

        self.db.commit()
        logger.info(f"Insight {insight_id} resolved")

        return True

    def store_daily_tracking(
        self,
        company_id: str,
        metrics: Dict[str, int]
    ) -> bool:
        """
        Store daily insight tracking snapshot (TimescaleDB)

        Args:
            company_id: Company identifier
            metrics: Dictionary of metric counts

        Returns:
            True if successful
        """
        tracking = InsightTracking(
            time=datetime.now(),
            company_id=company_id,
            total_active_risks=metrics.get('total_active_risks', 0),
            total_active_opportunities=metrics.get('total_active_opportunities', 0),
            critical_risks=metrics.get('critical_risks', 0),
            high_risks=metrics.get('high_risks', 0),
            medium_risks=metrics.get('medium_risks', 0),
            low_risks=metrics.get('low_risks', 0),
            operational_risks=metrics.get('operational_risks', 0),
            financial_risks=metrics.get('financial_risks', 0),
            competitive_risks=metrics.get('competitive_risks', 0),
            reputational_risks=metrics.get('reputational_risks', 0),
            compliance_risks=metrics.get('compliance_risks', 0),
            strategic_risks=metrics.get('strategic_risks', 0),
            market_opportunities=metrics.get('market_opportunities', 0),
            cost_opportunities=metrics.get('cost_opportunities', 0),
            strategic_opportunities=metrics.get('strategic_opportunities', 0),
            recommendations_generated=metrics.get('recommendations_generated', 0),
            actions_taken=metrics.get('actions_taken', 0),
            actions_completed=metrics.get('actions_completed', 0),
            risks_materialized=metrics.get('risks_materialized', 0),
            risks_avoided=metrics.get('risks_avoided', 0),
            opportunities_captured=metrics.get('opportunities_captured', 0),
            opportunities_missed=metrics.get('opportunities_missed', 0)
        )

        self.db.add(tracking)
        self.db.commit()

        logger.info(f"Stored daily tracking for company {company_id}")
        return True

    def _find_duplicate(
        self,
        company_id: str,
        risk_code: str
    ) -> Optional[BusinessInsight]:
        """
        Check if risk already exists for today

        Args:
            company_id: Company identifier
            risk_code: Risk code to check

        Returns:
            Existing BusinessInsight or None
        """
        today = datetime.now().date()

        return self.db.query(BusinessInsight).filter(
            and_(
                BusinessInsight.company_id == company_id,
                BusinessInsight.title.contains(risk_code),
                func.date(BusinessInsight.detected_at) == today
            )
        ).first()

    def _update_insight(
        self,
        existing: BusinessInsight,
        new_risk: DetectedRisk
    ) -> int:
        """
        Update existing insight with new detection

        Args:
            existing: Existing BusinessInsight record
            new_risk: New DetectedRisk with updated data

        Returns:
            insight_id
        """
        # Update scores if new detection has higher confidence
        if float(new_risk.confidence) > float(existing.confidence):
            existing.probability = new_risk.probability
            existing.impact = new_risk.impact
            existing.urgency = new_risk.urgency
            existing.confidence = new_risk.confidence
            existing.final_score = new_risk.final_score
            existing.severity_level = new_risk.severity_level
            existing.updated_at = datetime.now()
            existing.triggering_indicators = new_risk.triggering_indicators if isinstance(new_risk.triggering_indicators, dict) else {}

            self.db.commit()

            # Store updated score history
            self._store_score_history(existing)

            logger.info(f"Updated insight {existing.insight_id} with higher confidence detection")

        return existing.insight_id

    def _update_opportunity_insight(
        self,
        existing: BusinessInsight,
        new_opportunity: DetectedOpportunity
    ) -> int:
        """
        Update existing opportunity insight with new detection

        Args:
            existing: Existing BusinessInsight record
            new_opportunity: New DetectedOpportunity with updated data

        Returns:
            insight_id
        """
        # Update if new detection has higher strategic fit
        if float(new_opportunity.strategic_fit) > float(existing.confidence):
            existing.probability = Decimal(str(new_opportunity.potential_value))
            existing.impact = Decimal(str(new_opportunity.feasibility * 10))
            existing.urgency = new_opportunity.timing_score
            existing.confidence = Decimal(str(new_opportunity.strategic_fit))
            existing.final_score = new_opportunity.final_score
            existing.severity_level = new_opportunity.priority
            existing.updated_at = datetime.now()
            existing.triggering_indicators = new_opportunity.triggering_factors if isinstance(new_opportunity.triggering_factors, dict) else {}

            self.db.commit()

            # Store updated score history
            self._store_score_history(existing)

            logger.info(f"Updated opportunity {existing.insight_id} with higher strategic fit")

        return existing.insight_id

    def _store_score_history(self, insight: BusinessInsight):
        """
        Store score snapshot in TimescaleDB hypertable

        Args:
            insight: BusinessInsight to track
        """
        history = InsightScoreHistory(
            time=datetime.now(),
            insight_id=insight.insight_id,
            probability=insight.probability,
            impact=insight.impact,
            urgency=insight.urgency,
            confidence=insight.confidence,
            final_score=insight.final_score,
            severity_level=insight.severity_level,
            triggering_indicators=insight.triggering_indicators
        )

        self.db.add(history)
        # Don't commit here - let parent method handle commit

        logger.debug(f"Stored score history for insight {insight.insight_id}")
