"""
Layer 4: Insight Persistence Service

Stores Layer 4 pipeline outputs (risks, opportunities, recommendations)
to the PostgreSQL database for dashboard display.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from app.models.business_insight_models import (
    BusinessInsight,
    InsightRecommendation,
    RiskOpportunityDefinition
)

logger = logging.getLogger(__name__)


class InsightPersistenceService:
    """
    Persists Layer 4 outputs to the database.
    
    Handles:
    - Storing detected risks
    - Storing detected opportunities  
    - Storing recommendations
    - Deduplication to avoid duplicate insights
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def store_pipeline_results(
        self,
        company_id: str,
        layer4_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store complete Layer 4 pipeline results.
        
        Args:
            company_id: Company identifier
            layer4_output: Output from the integration pipeline
            
        Returns:
            Summary of stored items
        """
        stored = {
            "risks_stored": 0,
            "opportunities_stored": 0,
            "recommendations_stored": 0,
            "skipped_duplicates": 0
        }
        
        try:
            # Store risks
            risks = layer4_output.get("risks", [])
            for risk in risks:
                result = self._store_risk(company_id, risk)
                if result:
                    stored["risks_stored"] += 1
                else:
                    stored["skipped_duplicates"] += 1
            
            # Store opportunities
            opportunities = layer4_output.get("opportunities", [])
            for opp in opportunities:
                result = self._store_opportunity(company_id, opp)
                if result:
                    stored["opportunities_stored"] += 1
                else:
                    stored["skipped_duplicates"] += 1
            
            # Commit all changes
            self.db.commit()
            
            # Store recommendations (linked to insights)
            recommendations = layer4_output.get("recommendations", [])
            for rec in recommendations:
                self._store_recommendation(company_id, rec)
            
            stored["recommendations_stored"] = len(recommendations)
            self.db.commit()
            
            logger.info(f"Stored L4 results for {company_id}: {stored}")
            return stored
            
        except Exception as e:
            logger.error(f"Failed to store L4 results: {e}")
            self.db.rollback()
            raise
    
    def _store_risk(self, company_id: str, risk: Dict[str, Any]) -> Optional[BusinessInsight]:
        """Store a detected risk."""
        # Check for duplicate (same risk code in last 24 hours)
        risk_code = risk.get("risk_code", "UNKNOWN")
        existing = self._find_recent_insight(company_id, risk_code, "risk")
        
        if existing:
            # Update existing instead of creating duplicate
            existing.updated_at = datetime.now()
            existing.final_score = self._to_decimal(risk.get("final_score", 5.0))
            return None
        
        # Create new insight
        insight = BusinessInsight(
            company_id=company_id,
            insight_type="risk",
            category=risk.get("category", "operational"),
            title=risk.get("title", risk.get("risk_code", "Risk")),
            description=risk.get("description", ""),
            probability=self._to_decimal(risk.get("probability", 0.5)),
            impact=self._to_decimal(risk.get("impact", 5.0)),
            urgency=risk.get("urgency", 3),
            confidence=self._to_decimal(risk.get("confidence", 0.8)),
            final_score=self._to_decimal(risk.get("final_score", 5.0)),
            severity_level=risk.get("severity_level", "medium"),
            detected_at=datetime.now(),
            status="active",
            triggering_indicators=risk.get("triggering_indicators", {}),
            is_urgent=risk.get("is_urgent", False),
            requires_immediate_action=risk.get("requires_immediate_action", False)
        )
        
        self.db.add(insight)
        self.db.flush()  # Get the ID
        return insight
    
    def _store_opportunity(self, company_id: str, opp: Dict[str, Any]) -> Optional[BusinessInsight]:
        """Store a detected opportunity."""
        opp_code = opp.get("opportunity_code", "UNKNOWN")
        existing = self._find_recent_insight(company_id, opp_code, "opportunity")
        
        if existing:
            existing.updated_at = datetime.now()
            existing.final_score = self._to_decimal(opp.get("final_score", 5.0))
            return None
        
        insight = BusinessInsight(
            company_id=company_id,
            insight_type="opportunity",
            category=opp.get("category", "market"),
            title=opp.get("title", opp.get("opportunity_code", "Opportunity")),
            description=opp.get("description", ""),
            probability=self._to_decimal(opp.get("feasibility", 0.7)),
            impact=self._to_decimal(opp.get("potential_value", 6.0)),
            urgency=3,  # Opportunities typically medium urgency
            confidence=self._to_decimal(opp.get("confidence", 0.8)),
            final_score=self._to_decimal(opp.get("final_score", 6.0)),
            severity_level=opp.get("priority_level", "medium"),
            detected_at=datetime.now(),
            status="active",
            triggering_indicators=opp.get("triggering_indicators", {}),
            is_urgent=False,
            requires_immediate_action=False
        )
        
        self.db.add(insight)
        self.db.flush()
        return insight
    
    def _store_recommendation(self, company_id: str, rec: Dict[str, Any]) -> InsightRecommendation:
        """Store a recommendation."""
        # Find the most recent related insight for this company
        insight = self.db.execute(
            select(BusinessInsight)
            .where(BusinessInsight.company_id == company_id)
            .where(BusinessInsight.status == "active")
            .order_by(desc(BusinessInsight.detected_at))
            .limit(1)
        ).scalar_one_or_none()
        
        insight_id = insight.insight_id if insight else None
        
        recommendation = InsightRecommendation(
            insight_id=insight_id,
            category=rec.get("category", "operational_improvement"),
            priority=rec.get("priority", 3),
            action_title=rec.get("action_title", "Recommendation")[:200],
            action_description=rec.get("action_description", rec.get("description", "")),
            responsible_role=rec.get("responsible_role"),
            estimated_effort=rec.get("estimated_effort", "medium"),
            estimated_timeframe=rec.get("estimated_timeframe", "this_week"),
            expected_benefit=rec.get("expected_benefit", ""),
            success_metrics=rec.get("success_metrics", []),
            status="pending"
        )
        
        self.db.add(recommendation)
        return recommendation
    
    def _find_recent_insight(
        self,
        company_id: str,
        code: str,
        insight_type: str,
        hours: int = 24
    ) -> Optional[BusinessInsight]:
        """Find a recent insight with the same code to avoid duplicates."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Look for insights with matching title (which contains the code)
        result = self.db.execute(
            select(BusinessInsight)
            .where(and_(
                BusinessInsight.company_id == company_id,
                BusinessInsight.insight_type == insight_type,
                BusinessInsight.title.contains(code),
                BusinessInsight.detected_at >= cutoff
            ))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    def _to_decimal(self, value: Any) -> Optional[Decimal]:
        """Convert value to Decimal."""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except:
            return Decimal("0.5")
    
    def get_company_insights(
        self,
        company_id: str,
        insight_type: Optional[str] = None,
        status: str = "active",
        limit: int = 50
    ) -> List[BusinessInsight]:
        """Get insights for a company."""
        query = select(BusinessInsight).where(
            BusinessInsight.company_id == company_id
        )
        
        if insight_type:
            query = query.where(BusinessInsight.insight_type == insight_type)
        
        if status:
            query = query.where(BusinessInsight.status == status)
        
        query = query.order_by(desc(BusinessInsight.detected_at)).limit(limit)
        
        result = self.db.execute(query)
        return list(result.scalars().all())
    
    def get_company_recommendations(
        self,
        company_id: str,
        status: str = "pending",
        limit: int = 20
    ) -> List[InsightRecommendation]:
        """Get recommendations for a company."""
        # Get insight IDs for this company
        insight_ids = self.db.execute(
            select(BusinessInsight.insight_id)
            .where(BusinessInsight.company_id == company_id)
        ).scalars().all()
        
        if not insight_ids:
            return []
        
        query = select(InsightRecommendation).where(
            InsightRecommendation.insight_id.in_(insight_ids)
        )
        
        if status:
            query = query.where(InsightRecommendation.status == status)
        
        query = query.order_by(InsightRecommendation.priority).limit(limit)
        
        result = self.db.execute(query)
        return list(result.scalars().all())
    
    def clear_old_insights(self, company_id: str, days: int = 30) -> int:
        """Archive old resolved insights."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        result = self.db.execute(
            select(BusinessInsight)
            .where(and_(
                BusinessInsight.company_id == company_id,
                BusinessInsight.status.in_(["resolved", "expired"]),
                BusinessInsight.detected_at < cutoff
            ))
        )
        
        count = 0
        for insight in result.scalars():
            insight.status = "archived"
            count += 1
        
        self.db.commit()
        return count
