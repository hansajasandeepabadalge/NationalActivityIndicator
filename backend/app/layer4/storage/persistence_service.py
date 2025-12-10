"""
Layer 4: Persistence Service

Stores Layer 4 outputs (risks, opportunities, recommendations) to the database
so they can be displayed in the Layer 5 dashboard.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.business_insight_models import BusinessInsight, InsightRecommendation
from app.models.company_profile_models import CompanyProfile

logger = logging.getLogger(__name__)


class Layer4PersistenceService:
    """
    Persists Layer 4 pipeline outputs to the database.
    
    Stores:
    - Risks as BusinessInsight (insight_type='risk')
    - Opportunities as BusinessInsight (insight_type='opportunity')
    - Recommendations linked to insights
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def store_pipeline_results(
        self,
        company_id: str,
        layer4_output: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Store complete Layer 4 pipeline output.
        
        Args:
            company_id: Company ID
            layer4_output: Full Layer 4 output dict with risks, opportunities, recommendations
            
        Returns:
            Dict with counts of stored items
        """
        stats = {
            "risks_stored": 0,
            "opportunities_stored": 0,
            "recommendations_stored": 0,
            "errors": 0
        }
        
        try:
            # Get or create company profile
            company = self._get_or_create_company(company_id, layer4_output)
            
            # Store risks
            risks = layer4_output.get("risks", [])
            for risk in risks:
                try:
                    self._store_risk(company.company_id, risk)
                    stats["risks_stored"] += 1
                except Exception as e:
                    logger.error(f"Failed to store risk: {e}")
                    stats["errors"] += 1
            
            # Store opportunities
            opportunities = layer4_output.get("opportunities", [])
            for opp in opportunities:
                try:
                    self._store_opportunity(company.company_id, opp)
                    stats["opportunities_stored"] += 1
                except Exception as e:
                    logger.error(f"Failed to store opportunity: {e}")
                    stats["errors"] += 1
            
            # Store recommendations (linked to insights)
            recommendations = layer4_output.get("recommendations", [])
            for rec in recommendations:
                try:
                    self._store_recommendation(company.company_id, rec)
                    stats["recommendations_stored"] += 1
                except Exception as e:
                    logger.error(f"Failed to store recommendation: {e}")
                    stats["errors"] += 1
            
            self.db.commit()
            logger.info(f"Stored L4 results for {company_id}: {stats}")
            
        except Exception as e:
            logger.error(f"Failed to store L4 results: {e}")
            self.db.rollback()
            raise
        
        return stats
    
    def _get_or_create_company(
        self,
        company_id: str,
        layer4_output: Dict[str, Any]
    ) -> CompanyProfile:
        """Get existing company or create a new one."""
        company = self.db.query(CompanyProfile).filter(
            CompanyProfile.company_id == company_id
        ).first()
        
        if not company:
            company = CompanyProfile(
                company_id=company_id,
                company_name=layer4_output.get("company_name", company_id),
                industry=layer4_output.get("industry", "general"),
                is_active=True
            )
            self.db.add(company)
            self.db.flush()  # Get the ID
            logger.info(f"Created new company profile: {company_id}")
        
        return company
    
    def _store_risk(self, company_id: str, risk: Dict[str, Any]) -> BusinessInsight:
        """Store a risk as BusinessInsight."""
        # Check if this risk already exists (by title for this company)
        risk_title = risk.get("title", risk.get("risk_name", "Unknown Risk"))
        existing = self.db.query(BusinessInsight).filter(
            BusinessInsight.company_id == company_id,
            BusinessInsight.title == risk_title,
            BusinessInsight.insight_type == "risk",
            BusinessInsight.status == "active"
        ).first()
        
        if existing:
            # Update existing risk
            existing.description = risk.get("description", existing.description)
            existing.severity_level = risk.get("severity_level", "medium")
            existing.confidence = float(risk.get("confidence", 0.8))
            existing.final_score = float(risk.get("final_score", 5.0))
            existing.updated_at = datetime.utcnow()
            return existing
        
        # Create new risk
        insight = BusinessInsight(
            company_id=company_id,
            insight_type="risk",
            title=risk_title[:200],
            description=risk.get("description", ""),
            severity_level=risk.get("severity_level", "medium"),
            confidence=float(risk.get("confidence", 0.8)),
            probability=float(risk.get("probability", 0.7)),
            impact=float(risk.get("impact", 5.0)),
            urgency=int(risk.get("urgency", 3)),
            final_score=float(risk.get("final_score", 5.0)),
            category=risk.get("category", "operational"),
            triggering_indicators=risk.get("triggering_indicators", {}),
            status="active",
            detected_at=datetime.utcnow()
        )
        self.db.add(insight)
        return insight
    
    def _store_opportunity(self, company_id: str, opp: Dict[str, Any]) -> BusinessInsight:
        """Store an opportunity as BusinessInsight."""
        opp_title = opp.get("title", opp.get("opportunity_name", "Unknown Opportunity"))
        existing = self.db.query(BusinessInsight).filter(
            BusinessInsight.company_id == company_id,
            BusinessInsight.title == opp_title,
            BusinessInsight.insight_type == "opportunity",
            BusinessInsight.status == "active"
        ).first()
        
        if existing:
            # Update existing opportunity
            existing.description = opp.get("description", existing.description)
            existing.severity_level = opp.get("priority_level", "medium")
            existing.confidence = float(opp.get("feasibility", 0.8))
            existing.final_score = float(opp.get("final_score", 5.0))
            existing.updated_at = datetime.utcnow()
            return existing
        
        # Create new opportunity
        insight = BusinessInsight(
            company_id=company_id,
            insight_type="opportunity",
            title=opp_title[:200],
            description=opp.get("description", ""),
            severity_level=opp.get("priority_level", "medium"),
            confidence=float(opp.get("feasibility", 0.8)),
            probability=float(opp.get("timing_score", 0.7)),
            impact=float(opp.get("potential_value", 5.0)),
            final_score=float(opp.get("final_score", 5.0)),
            category=opp.get("category", "market"),
            triggering_indicators=opp.get("triggering_indicators", {}),
            status="active",
            detected_at=datetime.utcnow()
        )
        self.db.add(insight)
        return insight
    
    def _store_recommendation(self, company_id: str, rec: Dict[str, Any]) -> BusinessInsight:
        """Store a recommendation as BusinessInsight."""
        rec_title = rec.get("action_title", rec.get("title", "Recommendation"))
        
        # Create recommendation as a special insight type
        insight = BusinessInsight(
            company_id=company_id,
            insight_type="recommendation",
            title=rec_title[:200],
            description=rec.get("action_description", rec.get("description", "")),
            severity_level=self._priority_to_severity(rec.get("priority", 3)),
            confidence=0.9,
            probability=0.8,
            impact=5.0,
            final_score=float(rec.get("score", 5.0)),
            category=rec.get("category", "operational_improvement"),
            triggering_indicators={
                "action_steps": rec.get("action_steps", []),
                "timeline": rec.get("estimated_timeframe", "this_week"),
                "effort": rec.get("estimated_effort", "medium"),
                "expected_benefit": rec.get("expected_benefit", ""),
                "source": rec.get("source", "rule_based")
            },
            status="active",
            detected_at=datetime.utcnow()
        )
        self.db.add(insight)
        return insight
    
    def _priority_to_severity(self, priority: Any) -> str:
        """Convert priority (1-5 or string) to severity level."""
        if isinstance(priority, int):
            if priority <= 2:
                return "high"
            elif priority <= 3:
                return "medium"
            else:
                return "low"
        return str(priority).lower() if priority else "medium"
    
    def get_stored_insights(
        self,
        company_id: str,
        insight_type: Optional[str] = None,
        limit: int = 50
    ) -> List[BusinessInsight]:
        """Get stored insights for a company."""
        query = self.db.query(BusinessInsight).filter(
            BusinessInsight.company_id == company_id,
            BusinessInsight.status == "active"
        )
        
        if insight_type:
            query = query.filter(BusinessInsight.insight_type == insight_type)
        
        return query.order_by(BusinessInsight.detected_at.desc()).limit(limit).all()
    
    def clear_old_insights(self, company_id: str, insight_type: Optional[str] = None):
        """Mark old insights as resolved before storing new ones."""
        query = self.db.query(BusinessInsight).filter(
            BusinessInsight.company_id == company_id,
            BusinessInsight.status == "active"
        )
        
        if insight_type:
            query = query.filter(BusinessInsight.insight_type == insight_type)
        
        query.update({"status": "resolved", "resolved_at": datetime.utcnow()})
        self.db.commit()
