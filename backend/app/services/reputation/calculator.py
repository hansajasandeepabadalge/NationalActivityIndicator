import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.services.reputation.config import ReputationConfig, FilterAction, ReputationUpdate
from app.services.reputation.repository import ReputationRepository

logger = logging.getLogger(__name__)

class ReputationCalculator:
    """Mathematical engine for calculating boosts, drops, and EMA variables."""
    
    def __init__(self, db: Session, config: ReputationConfig, repository: ReputationRepository):
        self.db = db
        self.config = config
        self.repository = repository
        
    async def process_article_result(
        self,
        source_name: str,
        article_id: str,
        quality_score: float,
        was_accepted: bool,
        confidence_score: Optional[float] = None,
        classification_correct: Optional[bool] = None
    ) -> ReputationUpdate:
        from app.models.source_reputation_models import QualityFilterLog
        
        source = await self.repository.get_or_create_source(source_name)
        
        old_score = source.reputation_score
        old_tier = source.reputation_tier
        
        # Update article counts
        source.total_articles += 1
        source.articles_last_30_days += 1
        source.last_article_at = datetime.utcnow()
        
        if was_accepted:
            source.accepted_articles += 1
        else:
            source.rejected_articles += 1
            
        total = source.accepted_articles + source.rejected_articles
        source.acceptance_rate = source.accepted_articles / total if total > 0 else 1.0
        
        # EMA
        alpha = self.config.ema_alpha
        source.avg_quality_score = (alpha * quality_score) + ((1 - alpha) * source.avg_quality_score)
        
        if confidence_score is not None:
            source.avg_confidence_score = (alpha * confidence_score) + ((1 - alpha) * source.avg_confidence_score)
            
        # Rep adjustment calculation
        adjustment = 0.0
        change_reason = ""
        
        if was_accepted and quality_score >= self.config.excellent_quality:
            adjustment = self.config.boost_rate
            change_reason = f"High quality article ({quality_score:.1f})"
        elif was_accepted and quality_score >= self.config.warning_quality:
            adjustment = self.config.boost_rate * 0.5
            change_reason = f"Good quality article ({quality_score:.1f})"
        elif was_accepted and quality_score >= self.config.min_article_quality:
            adjustment = self.config.boost_rate * 0.1
            change_reason = f"Acceptable quality article ({quality_score:.1f})"
        elif not was_accepted:
            adjustment = -self.config.penalty_rate
            change_reason = f"Article rejected (quality: {quality_score:.1f})"
        else:
            adjustment = -self.config.penalty_rate * 0.5
            change_reason = f"Low quality article accepted ({quality_score:.1f})"
            
        if classification_correct is not None:
            if classification_correct:
                adjustment += self.config.boost_rate * 0.5
                change_reason += " [Accurate classification]"
            else:
                adjustment -= self.config.penalty_rate * 0.5
                change_reason += " [Inaccurate classification]"
                
        # Apply adj
        new_score = max(0.0, min(1.0, source.reputation_score + adjustment))
        source.reputation_score = new_score
        
        new_tier = self.repository.score_to_tier(new_score)
        source.reputation_tier = new_tier.value
        tier_changed = old_tier != new_tier.value
        
        if new_score > old_score:
            source.is_improving = True
            source.is_declining = False
        elif new_score < old_score:
            source.is_improving = False
            source.is_declining = True
            
        if quality_score >= self.config.warning_quality:
            source.consecutive_quality_articles += 1
            source.consecutive_poor_articles = 0
        elif quality_score < self.config.min_article_quality:
            source.consecutive_quality_articles = 0
            source.consecutive_poor_articles += 1
            
        if source.consecutive_poor_articles >= self.config.max_consecutive_poor_articles:
            source.is_active = False
            change_reason += f" [AUTO-DISABLED: {source.consecutive_poor_articles} consecutive poor articles]"
            logger.warning(f"Source {source_name} auto-disabled due to poor performance")
            
        source.last_evaluated_at = datetime.utcnow()
        
        # Log filter action
        action = FilterAction.ACCEPTED if was_accepted else FilterAction.REJECTED
        if quality_score >= self.config.excellent_quality and was_accepted:
            action = FilterAction.BOOSTED
        elif quality_score < self.config.warning_quality and was_accepted:
            action = FilterAction.DOWNGRADED
            
        weight_multiplier = self.config.weight_multipliers.get(new_tier, 1.0)
            
        log_entry = QualityFilterLog(
            article_id=article_id,
            source_id=source.id,
            action=action.value,
            action_reason=change_reason,
            source_reputation_score=new_score,
            article_quality_score=quality_score,
            threshold_applied=self.config.min_article_quality,
            weight_multiplier=weight_multiplier
        )
        self.db.add(log_entry)
        self.db.commit()
        
        update = ReputationUpdate(
            source_name=source_name,
            old_score=old_score,
            new_score=new_score,
            old_tier=old_tier,
            new_tier=new_tier.value,
            change_reason=change_reason,
            tier_changed=tier_changed
        )
        
        if tier_changed:
            logger.info(f"Source {source_name} tier changed: {old_tier} → {new_tier.value}")
            
        return update
