import time
from typing import Optional
from sqlalchemy.orm import Session

from app.services.reputation import ReputationManager, ReputationTier, FilterAction, FilterResult
from app.services.filters.config import FilterConfig

class PostProcessor:
    """Handles article quality scoring after classification."""
    
    def __init__(self, db: Session, config: FilterConfig, reputation_manager: ReputationManager, logger):
        self.db = db
        self.config = config
        self.reputation_manager = reputation_manager
        self.logger = logger
        
    async def process(
        self,
        article_id: str,
        source_name: str,
        quality_score: float,
        confidence_score: Optional[float] = None
    ) -> FilterResult:
        start_time = time.time()
        
        if not self.config.enabled or not self.config.post_filter_enabled:
            return FilterResult(
                action=FilterAction.ACCEPTED,
                reason="Post-filtering disabled",
                weight_multiplier=1.0,
                article_quality=quality_score
            )
            
        source = await self.reputation_manager.get_or_create_source(source_name)
        reputation_score = source.reputation_score
        weight = await self.reputation_manager.get_weight_multiplier(source_name)
        
        if quality_score < self.config.min_quality_score:
            if not self.config.soft_mode:
                await self.reputation_manager.record_article_result(
                    source_name=source_name,
                    article_id=article_id,
                    quality_score=quality_score,
                    was_accepted=False,
                    confidence_score=confidence_score
                )
                
                processing_time = int((time.time() - start_time) * 1000)
                return FilterResult(
                    action=FilterAction.REJECTED,
                    reason=f"Quality score {quality_score:.1f} below threshold {self.config.min_quality_score}",
                    weight_multiplier=0.0,
                    source_reputation=reputation_score,
                    article_quality=quality_score,
                    processing_time_ms=processing_time
                )
                
        action = FilterAction.ACCEPTED
        reason = f"Passed quality filter (score: {quality_score:.1f})"
        
        if quality_score >= 85.0:
            action = FilterAction.BOOSTED
            reason = f"Excellent quality (score: {quality_score:.1f})"
            weight *= 1.1
        elif quality_score < self.config.flag_below_quality:
            action = FilterAction.DOWNGRADED
            reason = f"Below-average quality (score: {quality_score:.1f})"
            weight *= 0.9
            
        await self.reputation_manager.record_article_result(
            source_name=source_name,
            article_id=article_id,
            quality_score=quality_score,
            was_accepted=True,
            confidence_score=confidence_score
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        return FilterResult(
            action=action,
            reason=reason,
            weight_multiplier=weight,
            source_reputation=reputation_score,
            article_quality=quality_score,
            processing_time_ms=processing_time
        )
