import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.services.reputation.config import ReputationConfig, ReputationUpdate
from app.services.reputation.repository import ReputationRepository

logger = logging.getLogger(__name__)

class ReputationTasks:
    """Background tasks for scheduled rep adjustments."""
    def __init__(self, db: Session, config: ReputationConfig, repository: ReputationRepository):
        self.db = db
        self.config = config
        self.repository = repository
        
    async def apply_inactivity_decay(self) -> List[ReputationUpdate]:
        """Apply reputation decay to sources that haven't published recently."""
        from app.models.source_reputation_models import SourceReputation
        
        cutoff = datetime.utcnow() - timedelta(days=7)
        inactive_sources = self.db.query(SourceReputation).filter(
            and_(
                SourceReputation.is_active == True,
                or_(
                    SourceReputation.last_article_at == None,
                    SourceReputation.last_article_at < cutoff
                )
            )
        ).all()
        
        updates = []
        for source in inactive_sources:
            old_score = source.reputation_score
            old_tier = source.reputation_tier
            
            new_score = max(0.3, source.reputation_score - self.config.decay_rate)
            source.reputation_score = new_score
            
            new_tier = self.repository.score_to_tier(new_score)
            source.reputation_tier = new_tier.value
            source.last_evaluated_at = datetime.utcnow()
            
            updates.append(ReputationUpdate(
                source_name=source.source_name,
                old_score=old_score,
                new_score=new_score,
                old_tier=old_tier,
                new_tier=new_tier.value,
                change_reason="Inactivity decay",
                tier_changed=old_tier != new_tier.value
            ))
            
        if updates:
            self.db.commit()
            logger.info(f"Applied inactivity decay to {len(updates)} sources")
            
        return updates

    async def create_daily_snapshot(self, source_name: str) -> None:
        """Create a daily reputation snapshot for trend analysis."""
        from app.models.source_reputation_models import SourceReputation, SourceReputationHistory
        
        source = self.db.query(SourceReputation).filter(
            SourceReputation.source_name == source_name
        ).first()
        
        if not source:
            return
            
        yesterday = datetime.utcnow() - timedelta(days=1)
        prev_snapshot = self.db.query(SourceReputationHistory).filter(
            and_(
                SourceReputationHistory.source_id == source.id,
                SourceReputationHistory.snapshot_date >= yesterday
            )
        ).order_by(SourceReputationHistory.snapshot_date.desc()).first()
        
        score_change = 0.0
        tier_changed = False
        
        if prev_snapshot:
            score_change = source.reputation_score - prev_snapshot.reputation_score
            tier_changed = source.reputation_tier != prev_snapshot.reputation_tier
            
        snapshot = SourceReputationHistory(
            source_id=source.id,
            snapshot_date=datetime.utcnow(),
            reputation_score=source.reputation_score,
            reputation_tier=source.reputation_tier,
            avg_quality_score=source.avg_quality_score,
            articles_count=source.articles_last_30_days,
            accepted_count=source.accepted_articles,
            rejected_count=source.rejected_articles,
            flagged_count=source.flagged_articles,
            score_change=score_change,
            tier_changed=tier_changed,
            acceptance_rate=source.acceptance_rate
        )
        
        self.db.add(snapshot)
        self.db.commit()
