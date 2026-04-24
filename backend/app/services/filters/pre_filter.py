import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.reputation import ReputationManager, ReputationTier, FilterAction, FilterResult
from app.services.filters.config import FilterConfig

class PreProcessor:
    """Handles fast source validation before processing NLP pipelines."""
    
    def __init__(self, db: Session, config: FilterConfig, reputation_manager: ReputationManager, logger):
        self.db = db
        self.config = config
        self.reputation_manager = reputation_manager
        self.logger = logger
        
    async def process(self, article_id: str, source_name: str, article_metadata: Optional[Dict[str, Any]] = None) -> FilterResult:
        start_time = time.time()
        
        if not self.config.enabled or not self.config.pre_filter_enabled:
            return FilterResult(
                action=FilterAction.ACCEPTED,
                reason="Pre-filtering disabled",
                weight_multiplier=1.0
            )

        source = await self.reputation_manager.get_or_create_source(source_name)
        reputation_score = source.reputation_score
        tier = ReputationTier(source.reputation_tier)
        
        if not source.is_active:
            result = FilterResult(
                action=FilterAction.REJECTED,
                reason=f"Source is disabled (reputation: {reputation_score:.2f})",
                weight_multiplier=0.0,
                source_reputation=reputation_score
            )
            return result
            
        if tier == ReputationTier.BLACKLISTED and self.config.reject_blacklisted:
            if not self.config.soft_mode:
                return FilterResult(
                    action=FilterAction.REJECTED,
                    reason=f"Source is blacklisted (reputation: {reputation_score:.2f})",
                    weight_multiplier=0.0,
                    source_reputation=reputation_score
                )
                
        if tier == ReputationTier.PROBATION and self.config.reject_probation:
            if not self.config.soft_mode:
                return FilterResult(
                    action=FilterAction.REJECTED,
                    reason=f"Source is on probation (reputation: {reputation_score:.2f})",
                    weight_multiplier=0.0,
                    source_reputation=reputation_score
                )
                
        weight = await self.reputation_manager.get_weight_multiplier(source_name)
        
        if tier == ReputationTier.PLATINUM and self.config.boost_platinum_sources:
            action = FilterAction.BOOSTED
            reason = f"Premium source (tier: platinum, reputation: {reputation_score:.2f})"
        elif tier == ReputationTier.GOLD and self.config.boost_gold_sources:
            action = FilterAction.BOOSTED
            reason = f"Trusted source (tier: gold, reputation: {reputation_score:.2f})"
        elif tier in [ReputationTier.BRONZE, ReputationTier.PROBATION]:
            action = FilterAction.FLAGGED
            reason = f"Low-tier source (tier: {tier.value}, reputation: {reputation_score:.2f})"
        else:
            action = FilterAction.ACCEPTED
            reason = f"Standard source (tier: {tier.value}, reputation: {reputation_score:.2f})"
            
        processing_time = int((time.time() - start_time) * 1000)
        
        return FilterResult(
            action=action,
            reason=reason,
            weight_multiplier=weight,
            source_reputation=reputation_score,
            processing_time_ms=processing_time
        )
