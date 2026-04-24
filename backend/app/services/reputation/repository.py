import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.reputation.config import ReputationTier

logger = logging.getLogger(__name__)

class ReputationRepository:
    """Handles direct DB operations for Source Reputation."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def score_to_tier(self, score: float) -> ReputationTier:
        """Convert reputation score to tier."""
        if score >= 0.90:
            return ReputationTier.PLATINUM
        elif score >= 0.75:
            return ReputationTier.GOLD
        elif score >= 0.60:
            return ReputationTier.SILVER
        elif score >= 0.45:
            return ReputationTier.BRONZE
        elif score >= 0.30:
            return ReputationTier.PROBATION
        else:
            return ReputationTier.BLACKLISTED
            
    async def get_or_create_source(
        self, 
        source_name: str,
        source_url: Optional[str] = None,
        source_type: str = "news",
        initial_credibility: float = 0.75
    ) -> Any:
        from app.models.source_reputation_models import SourceReputation
        
        source = self.db.query(SourceReputation).filter(
            SourceReputation.source_name == source_name
        ).first()
        
        if source:
            return source
        
        # Create new source
        tier = self.score_to_tier(initial_credibility)
        
        source = SourceReputation(
            source_name=source_name,
            source_url=source_url,
            source_type=source_type,
            reputation_score=initial_credibility,
            reputation_tier=tier.value,
            initial_credibility=initial_credibility,
            avg_quality_score=70.0,
            avg_confidence_score=0.7,
            is_active=True,
            last_evaluated_at=datetime.utcnow()
        )
        
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        
        logger.info(f"Created new source reputation: {source_name} (tier: {tier.value})")
        return source

    async def get_source_reputation(self, source_name: str) -> Optional[float]:
        from app.models.source_reputation_models import SourceReputation
        source = self.db.query(SourceReputation).filter(SourceReputation.source_name == source_name).first()
        return source.reputation_score if source else None
        
    async def get_sources_by_tier(self, tier: ReputationTier) -> List[Dict[str, Any]]:
        from app.models.source_reputation_models import SourceReputation
        sources = self.db.query(SourceReputation).filter(SourceReputation.reputation_tier == tier.value).all()
        return [s.to_dict() for s in sources]
        
    async def manually_override_source(self, source_name: str, is_active: bool, reason: str, override_by: str, duration_days: Optional[int] = None) -> None:
        source = await self.get_or_create_source(source_name)
        source.is_active = is_active
        source.is_manually_overridden = True
        source.override_reason = reason
        source.override_by = override_by
        
        if duration_days:
            source.override_until = datetime.utcnow() + timedelta(days=duration_days)
        else:
            source.override_until = None
        
        self.db.commit()
        
        action = "enabled" if is_active else "disabled"
        logger.info(f"Source {source_name} manually {action} by {override_by}: {reason}")
