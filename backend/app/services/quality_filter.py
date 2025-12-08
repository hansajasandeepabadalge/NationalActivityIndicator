"""
Quality Filter Service

This service provides automatic article filtering based on
source reputation and content quality scores.

It sits between Layer 1 (data acquisition) and Layer 2 (processing)
to filter out low-quality content before expensive processing.

Key Features:
- Pre-processing filter based on source reputation
- Post-processing filter based on article quality
- Weight adjustment based on source tier
- Filtering statistics and analytics
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.services.reputation_manager import (
    ReputationManager, 
    ReputationConfig, 
    FilterAction, 
    FilterResult,
    ReputationTier
)

logger = logging.getLogger(__name__)


# ============================================================================
# Filter Configuration
# ============================================================================

@dataclass
class FilterConfig:
    """Configuration for quality filtering."""
    # Enable/disable filtering
    enabled: bool = True
    
    # Pre-filter (before processing)
    pre_filter_enabled: bool = True
    reject_blacklisted: bool = True
    reject_probation: bool = False  # Be lenient by default
    
    # Post-filter (after quality scoring)
    post_filter_enabled: bool = True
    min_quality_score: float = 40.0
    flag_below_quality: float = 60.0
    
    # Boost settings
    boost_platinum_sources: bool = True
    boost_gold_sources: bool = True
    
    # Logging
    log_all_decisions: bool = True
    log_rejections_only: bool = False
    
    # Soft mode (log but don't reject)
    soft_mode: bool = False  # Set to True during initial rollout


@dataclass
class FilterStats:
    """Statistics from filtering operations."""
    total_processed: int = 0
    accepted: int = 0
    rejected: int = 0
    flagged: int = 0
    boosted: int = 0
    downgraded: int = 0
    
    # By source tier
    by_tier: Dict[str, int] = field(default_factory=dict)
    
    # Performance
    avg_filter_time_ms: float = 0.0
    total_filter_time_ms: int = 0
    
    # Quality distribution
    avg_quality_score: float = 0.0
    avg_reputation_score: float = 0.0
    
    def acceptance_rate(self) -> float:
        total = self.accepted + self.rejected
        return self.accepted / total if total > 0 else 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_processed": self.total_processed,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "flagged": self.flagged,
            "boosted": self.boosted,
            "downgraded": self.downgraded,
            "acceptance_rate": round(self.acceptance_rate(), 3),
            "by_tier": self.by_tier,
            "avg_filter_time_ms": round(self.avg_filter_time_ms, 2),
            "avg_quality_score": round(self.avg_quality_score, 1),
            "avg_reputation_score": round(self.avg_reputation_score, 3)
        }


# ============================================================================
# Quality Filter Service
# ============================================================================

class QualityFilter:
    """
    Filters articles based on source reputation and content quality.
    
    This service integrates with:
    - ReputationManager: For source reputation scores
    - QualityScorer (Layer 2): For article quality scores
    
    Usage:
        filter = QualityFilter(db_session)
        
        # Pre-filter before processing
        result = await filter.pre_filter(article, source_name)
        if result.action == FilterAction.REJECTED:
            skip_processing(article)
        
        # Post-filter after quality scoring
        result = await filter.post_filter(
            article, 
            source_name, 
            quality_score=85.0
        )
    """
    
    def __init__(
        self,
        db: Session,
        config: Optional[FilterConfig] = None,
        reputation_manager: Optional[ReputationManager] = None
    ):
        self.db = db
        self.config = config or FilterConfig()
        self.reputation_manager = reputation_manager or ReputationManager(db)
        
        # Session statistics
        self._stats = FilterStats()
        self._session_start = datetime.utcnow()
    
    async def pre_filter(
        self,
        article_id: str,
        source_name: str,
        article_metadata: Optional[Dict[str, Any]] = None
    ) -> FilterResult:
        """
        Pre-filter article before expensive processing.
        
        This is a fast check based on source reputation only.
        Use this to skip processing for blacklisted sources.
        
        Args:
            article_id: Unique article identifier
            source_name: Source identifier
            article_metadata: Optional metadata for additional checks
            
        Returns:
            FilterResult with action and reason
        """
        start_time = time.time()
        
        if not self.config.enabled or not self.config.pre_filter_enabled:
            return FilterResult(
                action=FilterAction.ACCEPTED,
                reason="Pre-filtering disabled",
                weight_multiplier=1.0
            )
        
        # Get source reputation
        source = await self.reputation_manager.get_or_create_source(source_name)
        reputation_score = source.reputation_score
        tier = ReputationTier(source.reputation_tier)
        
        # Check if source is active
        if not source.is_active:
            result = FilterResult(
                action=FilterAction.REJECTED,
                reason=f"Source is disabled (reputation: {reputation_score:.2f})",
                weight_multiplier=0.0,
                source_reputation=reputation_score
            )
            await self._log_decision(article_id, source.id, result)
            return result
        
        # Check blacklisted tier
        if tier == ReputationTier.BLACKLISTED and self.config.reject_blacklisted:
            if not self.config.soft_mode:
                result = FilterResult(
                    action=FilterAction.REJECTED,
                    reason=f"Source is blacklisted (reputation: {reputation_score:.2f})",
                    weight_multiplier=0.0,
                    source_reputation=reputation_score
                )
                await self._log_decision(article_id, source.id, result)
                return result
        
        # Check probation tier
        if tier == ReputationTier.PROBATION and self.config.reject_probation:
            if not self.config.soft_mode:
                result = FilterResult(
                    action=FilterAction.REJECTED,
                    reason=f"Source is on probation (reputation: {reputation_score:.2f})",
                    weight_multiplier=0.0,
                    source_reputation=reputation_score
                )
                await self._log_decision(article_id, source.id, result)
                return result
        
        # Get weight multiplier for accepted sources
        weight = await self.reputation_manager.get_weight_multiplier(source_name)
        
        # Determine action
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
        
        result = FilterResult(
            action=action,
            reason=reason,
            weight_multiplier=weight,
            source_reputation=reputation_score,
            processing_time_ms=processing_time
        )
        
        await self._log_decision(article_id, source.id, result)
        self._update_stats(result)
        
        return result
    
    async def post_filter(
        self,
        article_id: str,
        source_name: str,
        quality_score: float,
        confidence_score: Optional[float] = None
    ) -> FilterResult:
        """
        Post-filter article after quality scoring.
        
        This uses the actual quality score from QualityScorer
        to make a final acceptance decision.
        
        Args:
            article_id: Unique article identifier
            source_name: Source identifier
            quality_score: Quality score from QualityScorer (0-100)
            confidence_score: Optional classification confidence (0-1)
            
        Returns:
            FilterResult with final action
        """
        start_time = time.time()
        
        if not self.config.enabled or not self.config.post_filter_enabled:
            return FilterResult(
                action=FilterAction.ACCEPTED,
                reason="Post-filtering disabled",
                weight_multiplier=1.0,
                article_quality=quality_score
            )
        
        # Get source reputation
        source = await self.reputation_manager.get_or_create_source(source_name)
        reputation_score = source.reputation_score
        tier = ReputationTier(source.reputation_tier)
        weight = await self.reputation_manager.get_weight_multiplier(source_name)
        
        # Check quality threshold
        if quality_score < self.config.min_quality_score:
            if not self.config.soft_mode:
                # Record rejection
                await self.reputation_manager.record_article_result(
                    source_name=source_name,
                    article_id=article_id,
                    quality_score=quality_score,
                    was_accepted=False,
                    confidence_score=confidence_score
                )
                
                processing_time = int((time.time() - start_time) * 1000)
                result = FilterResult(
                    action=FilterAction.REJECTED,
                    reason=f"Quality score {quality_score:.1f} below threshold {self.config.min_quality_score}",
                    weight_multiplier=0.0,
                    source_reputation=reputation_score,
                    article_quality=quality_score,
                    processing_time_ms=processing_time
                )
                
                await self._log_decision(article_id, source.id, result)
                self._update_stats(result, quality_score, reputation_score)
                return result
        
        # Determine action based on quality
        action = FilterAction.ACCEPTED
        reason = f"Passed quality filter (score: {quality_score:.1f})"
        
        if quality_score >= 85.0:
            action = FilterAction.BOOSTED
            reason = f"Excellent quality (score: {quality_score:.1f})"
            weight *= 1.1  # Additional boost for high quality
            
        elif quality_score < self.config.flag_below_quality:
            action = FilterAction.DOWNGRADED
            reason = f"Below-average quality (score: {quality_score:.1f})"
            weight *= 0.9  # Slight penalty
        
        # Record acceptance
        await self.reputation_manager.record_article_result(
            source_name=source_name,
            article_id=article_id,
            quality_score=quality_score,
            was_accepted=True,
            confidence_score=confidence_score
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        result = FilterResult(
            action=action,
            reason=reason,
            weight_multiplier=weight,
            source_reputation=reputation_score,
            article_quality=quality_score,
            processing_time_ms=processing_time
        )
        
        await self._log_decision(article_id, source.id, result)
        self._update_stats(result, quality_score, reputation_score)
        
        return result
    
    async def filter_batch(
        self,
        articles: List[Dict[str, Any]],
        quality_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, FilterResult]:
        """
        Filter a batch of articles.
        
        Args:
            articles: List of articles with 'id' and 'source_name' fields
            quality_scores: Optional dict mapping article_id to quality score
            
        Returns:
            Dict mapping article_id to FilterResult
        """
        results = {}
        
        for article in articles:
            article_id = article.get('id') or article.get('article_id')
            source_name = article.get('source_name') or article.get('source', {}).get('name')
            
            if not article_id or not source_name:
                continue
            
            if quality_scores and article_id in quality_scores:
                # Post-filter with quality score
                result = await self.post_filter(
                    article_id=article_id,
                    source_name=source_name,
                    quality_score=quality_scores[article_id]
                )
            else:
                # Pre-filter only
                result = await self.pre_filter(
                    article_id=article_id,
                    source_name=source_name,
                    article_metadata=article
                )
            
            results[article_id] = result
        
        return results
    
    async def _log_decision(
        self,
        article_id: str,
        source_id: int,
        result: FilterResult
    ) -> None:
        """Log filtering decision to database."""
        from app.models.source_reputation_models import QualityFilterLog
        
        if not self.config.log_all_decisions:
            if self.config.log_rejections_only and result.action != FilterAction.REJECTED:
                return
        
        log_entry = QualityFilterLog(
            article_id=article_id,
            source_id=source_id,
            action=result.action.value,
            action_reason=result.reason,
            source_reputation_score=result.source_reputation,
            article_quality_score=result.article_quality,
            threshold_applied=self.config.min_quality_score,
            weight_multiplier=result.weight_multiplier,
            filter_latency_ms=result.processing_time_ms
        )
        
        self.db.add(log_entry)
        # Don't commit here - let the caller handle transaction
    
    def _update_stats(
        self,
        result: FilterResult,
        quality_score: Optional[float] = None,
        reputation_score: Optional[float] = None
    ) -> None:
        """Update session statistics."""
        self._stats.total_processed += 1
        
        if result.action == FilterAction.ACCEPTED:
            self._stats.accepted += 1
        elif result.action == FilterAction.REJECTED:
            self._stats.rejected += 1
        elif result.action == FilterAction.FLAGGED:
            self._stats.flagged += 1
        elif result.action == FilterAction.BOOSTED:
            self._stats.boosted += 1
        elif result.action == FilterAction.DOWNGRADED:
            self._stats.downgraded += 1
        
        # Update timing stats
        self._stats.total_filter_time_ms += result.processing_time_ms
        self._stats.avg_filter_time_ms = (
            self._stats.total_filter_time_ms / self._stats.total_processed
        )
        
        # Update quality stats (rolling average)
        if quality_score is not None:
            n = self._stats.total_processed
            self._stats.avg_quality_score = (
                (self._stats.avg_quality_score * (n - 1) + quality_score) / n
            )
        
        if reputation_score is not None:
            n = self._stats.total_processed
            self._stats.avg_reputation_score = (
                (self._stats.avg_reputation_score * (n - 1) + reputation_score) / n
            )
    
    def get_session_stats(self) -> FilterStats:
        """Get current session statistics."""
        return self._stats
    
    def reset_session_stats(self) -> None:
        """Reset session statistics."""
        self._stats = FilterStats()
        self._session_start = datetime.utcnow()
    
    async def get_filter_analytics(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get filtering analytics for the specified time period."""
        from app.models.source_reputation_models import QualityFilterLog
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Total counts by action
        action_counts = self.db.query(
            QualityFilterLog.action,
            func.count(QualityFilterLog.id)
        ).filter(
            QualityFilterLog.created_at >= cutoff
        ).group_by(QualityFilterLog.action).all()
        
        action_dict = {action: count for action, count in action_counts}
        
        # Average scores
        avg_quality = self.db.query(
            func.avg(QualityFilterLog.article_quality_score)
        ).filter(
            and_(
                QualityFilterLog.created_at >= cutoff,
                QualityFilterLog.article_quality_score != None
            )
        ).scalar() or 0.0
        
        avg_reputation = self.db.query(
            func.avg(QualityFilterLog.source_reputation_score)
        ).filter(
            QualityFilterLog.created_at >= cutoff
        ).scalar() or 0.0
        
        avg_latency = self.db.query(
            func.avg(QualityFilterLog.filter_latency_ms)
        ).filter(
            QualityFilterLog.created_at >= cutoff
        ).scalar() or 0.0
        
        total = sum(action_dict.values())
        accepted = action_dict.get('accepted', 0) + action_dict.get('boosted', 0)
        
        return {
            "time_period_hours": hours,
            "total_filtered": total,
            "action_breakdown": action_dict,
            "acceptance_rate": round(accepted / total, 3) if total > 0 else 1.0,
            "rejection_rate": round(action_dict.get('rejected', 0) / total, 3) if total > 0 else 0.0,
            "avg_quality_score": round(avg_quality, 1),
            "avg_reputation_score": round(avg_reputation, 3),
            "avg_latency_ms": round(avg_latency, 2),
            "config": {
                "enabled": self.config.enabled,
                "soft_mode": self.config.soft_mode,
                "min_quality_score": self.config.min_quality_score
            }
        }


# ============================================================================
# Factory & Integration Functions
# ============================================================================

def create_quality_filter(
    db: Session,
    config: Optional[FilterConfig] = None,
    soft_mode: bool = False
) -> QualityFilter:
    """
    Create a QualityFilter instance.
    
    Args:
        db: Database session
        config: Optional filter configuration
        soft_mode: If True, log but don't reject (for initial rollout)
    """
    if config is None:
        config = FilterConfig()
    
    if soft_mode:
        config.soft_mode = True
    
    return QualityFilter(db=db, config=config)


async def integrate_with_pipeline(
    filter_service: QualityFilter,
    articles: List[Dict[str, Any]],
    quality_scorer: Optional[Any] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Convenience function to integrate filtering with article pipeline.
    
    Returns:
        Tuple of (accepted_articles, rejected_articles)
    """
    accepted = []
    rejected = []
    
    for article in articles:
        article_id = article.get('id') or article.get('article_id')
        source_name = article.get('source_name') or article.get('source', {}).get('name')
        
        if not article_id or not source_name:
            accepted.append(article)  # Don't filter unknown articles
            continue
        
        # Pre-filter
        pre_result = await filter_service.pre_filter(article_id, source_name)
        
        if pre_result.action == FilterAction.REJECTED:
            article['_filter_result'] = pre_result.to_dict()
            rejected.append(article)
            continue
        
        # If quality scorer available, do post-filter
        if quality_scorer:
            try:
                # Assuming quality_scorer has a score() method
                quality_result = quality_scorer.score(article)
                quality_score = quality_result.overall_score
                
                post_result = await filter_service.post_filter(
                    article_id, source_name, quality_score
                )
                
                if post_result.action == FilterAction.REJECTED:
                    article['_filter_result'] = post_result.to_dict()
                    rejected.append(article)
                    continue
                
                # Add filter metadata
                article['_filter_result'] = post_result.to_dict()
                article['_weight_multiplier'] = post_result.weight_multiplier
                
            except Exception as e:
                logger.warning(f"Quality scoring failed for {article_id}: {e}")
                # Use pre-filter result
                article['_filter_result'] = pre_result.to_dict()
                article['_weight_multiplier'] = pre_result.weight_multiplier
        else:
            article['_filter_result'] = pre_result.to_dict()
            article['_weight_multiplier'] = pre_result.weight_multiplier
        
        accepted.append(article)
    
    return accepted, rejected
