"""
Source Reputation Management Service

This service manages dynamic source reputation scoring,
quality filtering, and automatic source management.

Key Features:
- Dynamic reputation calculation based on article quality
- Automatic tier classification (Platinum → Blacklisted)
- Quality-based article filtering
- Trend detection and auto-disable for poor sources
- Integration with Layer 1 & Layer 2 pipelines
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration & Constants
# ============================================================================

class ReputationTier(str, Enum):
    """Source reputation tier classification."""
    PLATINUM = "platinum"    # 0.90+ - Premium trusted sources
    GOLD = "gold"            # 0.75-0.89 - Highly reliable
    SILVER = "silver"        # 0.60-0.74 - Generally reliable
    BRONZE = "bronze"        # 0.45-0.59 - Use with caution
    PROBATION = "probation"  # 0.30-0.44 - Needs monitoring
    BLACKLISTED = "blacklisted"  # <0.30 - Disabled


class FilterAction(str, Enum):
    """Action taken during quality filtering."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    BOOSTED = "boosted"
    DOWNGRADED = "downgraded"


@dataclass
class ReputationConfig:
    """Configuration for reputation system."""
    # Tier thresholds
    tier_thresholds: Dict[str, float] = field(default_factory=lambda: {
        ReputationTier.PLATINUM: 0.90,
        ReputationTier.GOLD: 0.75,
        ReputationTier.SILVER: 0.60,
        ReputationTier.BRONZE: 0.45,
        ReputationTier.PROBATION: 0.30,
        ReputationTier.BLACKLISTED: 0.0
    })
    
    # Filtering thresholds
    min_reputation_active: float = 0.30
    min_reputation_trusted: float = 0.75
    min_article_quality: float = 40.0
    warning_quality: float = 60.0
    excellent_quality: float = 85.0
    
    # Auto-disable settings
    max_consecutive_poor_days: int = 7
    
    # Reputation adjustment rates
    boost_rate: float = 0.01       # Boost for quality articles
    penalty_rate: float = 0.02    # Penalty for poor articles
    decay_rate: float = 0.001     # Daily decay for inactivity
    
    # Weight multipliers by tier
    weight_multipliers: Dict[str, float] = field(default_factory=lambda: {
        ReputationTier.PLATINUM: 1.3,
        ReputationTier.GOLD: 1.15,
        ReputationTier.SILVER: 1.0,
        ReputationTier.BRONZE: 0.85,
        ReputationTier.PROBATION: 0.7,
        ReputationTier.BLACKLISTED: 0.0
    })
    
    # Rolling window for calculations
    rolling_window_days: int = 30


@dataclass
class FilterResult:
    """Result of quality filtering."""
    action: FilterAction
    reason: str
    weight_multiplier: float = 1.0
    source_reputation: float = 0.0
    article_quality: Optional[float] = None
    processing_time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "reason": self.reason,
            "weight_multiplier": self.weight_multiplier,
            "source_reputation": round(self.source_reputation, 3),
            "article_quality": round(self.article_quality, 1) if self.article_quality else None,
            "processing_time_ms": self.processing_time_ms
        }


@dataclass
class ReputationUpdate:
    """Details of a reputation update."""
    source_name: str
    old_score: float
    new_score: float
    old_tier: str
    new_tier: str
    change_reason: str
    tier_changed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "old_score": round(self.old_score, 3),
            "new_score": round(self.new_score, 3),
            "score_change": round(self.new_score - self.old_score, 4),
            "old_tier": self.old_tier,
            "new_tier": self.new_tier,
            "tier_changed": self.tier_changed,
            "reason": self.change_reason
        }


# ============================================================================
# Reputation Manager Service
# ============================================================================

class ReputationManager:
    """
    Manages source reputation scoring and updates.
    
    This is the core service for dynamic source quality tracking.
    It integrates with the quality scoring system from Layer 2
    and feeds into article weighting across the pipeline.
    
    Usage:
        manager = ReputationManager(db_session)
        
        # Get or create source reputation
        source = await manager.get_or_create_source("Ada Derana")
        
        # Update after processing article
        update = await manager.record_article_result(
            source_name="Ada Derana",
            article_id="ada_001",
            quality_score=85.0,
            was_accepted=True
        )
    """
    
    def __init__(
        self, 
        db: Session,
        config: Optional[ReputationConfig] = None
    ):
        self.db = db
        self.config = config or ReputationConfig()
        self._threshold_cache: Dict[str, float] = {}
        self._cache_loaded = False
    
    async def _load_thresholds_from_db(self) -> None:
        """Load configurable thresholds from database."""
        if self._cache_loaded:
            return
            
        try:
            from app.models.source_reputation_models import ReputationThreshold
            
            thresholds = self.db.query(ReputationThreshold).filter(
                ReputationThreshold.is_active == True
            ).all()
            
            for t in thresholds:
                self._threshold_cache[t.threshold_name] = t.value
            
            # Update config from DB values
            if "MIN_REPUTATION_ACTIVE" in self._threshold_cache:
                self.config.min_reputation_active = self._threshold_cache["MIN_REPUTATION_ACTIVE"]
            if "MIN_ARTICLE_QUALITY" in self._threshold_cache:
                self.config.min_article_quality = self._threshold_cache["MIN_ARTICLE_QUALITY"]
            if "REPUTATION_BOOST_RATE" in self._threshold_cache:
                self.config.boost_rate = self._threshold_cache["REPUTATION_BOOST_RATE"]
            if "REPUTATION_PENALTY_RATE" in self._threshold_cache:
                self.config.penalty_rate = self._threshold_cache["REPUTATION_PENALTY_RATE"]
                
            self._cache_loaded = True
            logger.info(f"Loaded {len(self._threshold_cache)} thresholds from database")
            
        except Exception as e:
            logger.warning(f"Could not load thresholds from DB, using defaults: {e}")
            self._cache_loaded = True
    
    def _score_to_tier(self, score: float) -> ReputationTier:
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
    
    def _tier_to_weight_multiplier(self, tier: ReputationTier) -> float:
        """Get weight multiplier for a tier."""
        return self.config.weight_multipliers.get(tier, 1.0)
    
    async def get_or_create_source(
        self, 
        source_name: str,
        source_url: Optional[str] = None,
        source_type: str = "news",
        initial_credibility: float = 0.75
    ) -> "SourceReputation":
        """
        Get existing source reputation or create new one.
        
        Args:
            source_name: Unique source identifier
            source_url: Base URL of source
            source_type: Type of source (news, social, government)
            initial_credibility: Starting credibility score
            
        Returns:
            SourceReputation model instance
        """
        from app.models.source_reputation_models import SourceReputation
        
        await self._load_thresholds_from_db()
        
        source = self.db.query(SourceReputation).filter(
            SourceReputation.source_name == source_name
        ).first()
        
        if source:
            return source
        
        # Create new source
        tier = self._score_to_tier(initial_credibility)
        
        source = SourceReputation(
            source_name=source_name,
            source_url=source_url,
            source_type=source_type,
            reputation_score=initial_credibility,
            reputation_tier=tier.value,
            initial_credibility=initial_credibility,
            avg_quality_score=70.0,  # Start with reasonable default
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
        """Get current reputation score for a source."""
        from app.models.source_reputation_models import SourceReputation
        
        source = self.db.query(SourceReputation).filter(
            SourceReputation.source_name == source_name
        ).first()
        
        return source.reputation_score if source else None
    
    async def is_source_active(self, source_name: str) -> bool:
        """Check if source is active and above minimum threshold."""
        from app.models.source_reputation_models import SourceReputation
        
        await self._load_thresholds_from_db()
        
        source = self.db.query(SourceReputation).filter(
            SourceReputation.source_name == source_name
        ).first()
        
        if not source:
            return True  # Unknown sources are allowed by default
        
        if not source.is_active:
            return False
        
        # Check if manually overridden
        if source.is_manually_overridden:
            if source.override_until and source.override_until > datetime.utcnow():
                return source.is_active
        
        # Check reputation threshold
        return source.reputation_score >= self.config.min_reputation_active
    
    async def record_article_result(
        self,
        source_name: str,
        article_id: str,
        quality_score: float,
        was_accepted: bool,
        confidence_score: Optional[float] = None,
        classification_correct: Optional[bool] = None
    ) -> ReputationUpdate:
        """
        Record article processing result and update reputation.
        
        This is called after each article is processed to update
        the source's rolling reputation score.
        
        Args:
            source_name: Source identifier
            article_id: Processed article ID
            quality_score: Quality score from QualityScorer (0-100)
            was_accepted: Whether article was accepted into the system
            confidence_score: Classification confidence (0-1)
            classification_correct: If known, whether classification was accurate
            
        Returns:
            ReputationUpdate with old/new scores
        """
        from app.models.source_reputation_models import SourceReputation, QualityFilterLog
        
        await self._load_thresholds_from_db()
        
        source = await self.get_or_create_source(source_name)
        
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
        
        # Update acceptance rate
        total = source.accepted_articles + source.rejected_articles
        source.acceptance_rate = source.accepted_articles / total if total > 0 else 1.0
        
        # Update rolling quality average (exponential moving average)
        alpha = 0.1  # Smoothing factor
        source.avg_quality_score = (alpha * quality_score) + ((1 - alpha) * source.avg_quality_score)
        
        if confidence_score is not None:
            source.avg_confidence_score = (alpha * confidence_score) + ((1 - alpha) * source.avg_confidence_score)
        
        # Calculate reputation adjustment
        adjustment = 0.0
        change_reason = ""
        
        if was_accepted and quality_score >= self.config.excellent_quality:
            # Excellent quality - boost reputation
            adjustment = self.config.boost_rate
            change_reason = f"High quality article ({quality_score:.1f})"
            
        elif was_accepted and quality_score >= self.config.warning_quality:
            # Good quality - small boost
            adjustment = self.config.boost_rate * 0.5
            change_reason = f"Good quality article ({quality_score:.1f})"
            
        elif was_accepted and quality_score >= self.config.min_article_quality:
            # Acceptable quality - minimal change
            adjustment = self.config.boost_rate * 0.1
            change_reason = f"Acceptable quality article ({quality_score:.1f})"
            
        elif not was_accepted:
            # Rejected - penalty
            adjustment = -self.config.penalty_rate
            change_reason = f"Article rejected (quality: {quality_score:.1f})"
            
        else:
            # Below warning threshold but accepted
            adjustment = -self.config.penalty_rate * 0.5
            change_reason = f"Low quality article accepted ({quality_score:.1f})"
        
        # Apply accuracy bonus/penalty if known
        if classification_correct is not None:
            if classification_correct:
                adjustment += self.config.boost_rate * 0.5
                change_reason += " [Accurate classification]"
            else:
                adjustment -= self.config.penalty_rate * 0.5
                change_reason += " [Inaccurate classification]"
        
        # Apply adjustment with bounds
        new_score = max(0.0, min(1.0, source.reputation_score + adjustment))
        source.reputation_score = new_score
        
        # Update tier
        new_tier = self._score_to_tier(new_score)
        source.reputation_tier = new_tier.value
        tier_changed = old_tier != new_tier.value
        
        # Update trend indicators
        if new_score > old_score:
            source.is_improving = True
            source.is_declining = False
        elif new_score < old_score:
            source.is_improving = False
            source.is_declining = True
        
        # Track consecutive quality/poor days
        if quality_score >= self.config.warning_quality:
            source.consecutive_quality_days += 1
            source.consecutive_poor_days = 0
        elif quality_score < self.config.min_article_quality:
            source.consecutive_quality_days = 0
            source.consecutive_poor_days += 1
        
        # Auto-disable if too many consecutive poor days
        if source.consecutive_poor_days >= self.config.max_consecutive_poor_days:
            source.is_active = False
            change_reason += f" [AUTO-DISABLED: {source.consecutive_poor_days} consecutive poor days]"
            logger.warning(f"Source {source_name} auto-disabled due to poor performance")
        
        source.last_evaluated_at = datetime.utcnow()
        
        # Log the filter action
        action = FilterAction.ACCEPTED if was_accepted else FilterAction.REJECTED
        if quality_score >= self.config.excellent_quality and was_accepted:
            action = FilterAction.BOOSTED
        elif quality_score < self.config.warning_quality and was_accepted:
            action = FilterAction.DOWNGRADED
        
        log_entry = QualityFilterLog(
            article_id=article_id,
            source_id=source.id,
            action=action.value,
            action_reason=change_reason,
            source_reputation_score=new_score,
            article_quality_score=quality_score,
            threshold_applied=self.config.min_article_quality,
            weight_multiplier=self._tier_to_weight_multiplier(new_tier)
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
    
    async def get_weight_multiplier(self, source_name: str) -> float:
        """
        Get weight multiplier for a source based on reputation.
        
        This is used to adjust article weights in indicator calculations.
        Higher reputation = higher weight.
        """
        from app.models.source_reputation_models import SourceReputation
        
        source = self.db.query(SourceReputation).filter(
            SourceReputation.source_name == source_name
        ).first()
        
        if not source:
            return 1.0  # Unknown sources get neutral weight
        
        tier = ReputationTier(source.reputation_tier)
        return self._tier_to_weight_multiplier(tier)
    
    async def create_daily_snapshot(self, source_name: str) -> None:
        """Create a daily reputation snapshot for trend analysis."""
        from app.models.source_reputation_models import SourceReputation, SourceReputationHistory
        
        source = self.db.query(SourceReputation).filter(
            SourceReputation.source_name == source_name
        ).first()
        
        if not source:
            return
        
        # Get previous snapshot for comparison
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
    
    async def apply_inactivity_decay(self) -> List[ReputationUpdate]:
        """
        Apply reputation decay to sources that haven't published recently.
        
        This should be run daily to prevent stale sources from
        maintaining high reputation.
        """
        from app.models.source_reputation_models import SourceReputation
        
        await self._load_thresholds_from_db()
        
        # Find sources with no activity in the last 7 days
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
            
            # Apply decay
            new_score = max(0.3, source.reputation_score - self.config.decay_rate)
            source.reputation_score = new_score
            
            new_tier = self._score_to_tier(new_score)
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
    
    async def get_sources_by_tier(self, tier: ReputationTier) -> List[Dict[str, Any]]:
        """Get all sources in a specific tier."""
        from app.models.source_reputation_models import SourceReputation
        
        sources = self.db.query(SourceReputation).filter(
            SourceReputation.reputation_tier == tier.value
        ).all()
        
        return [s.to_dict() for s in sources]
    
    async def get_reputation_summary(self) -> Dict[str, Any]:
        """Get overall reputation system summary."""
        from app.models.source_reputation_models import SourceReputation
        
        total = self.db.query(func.count(SourceReputation.id)).scalar()
        active = self.db.query(func.count(SourceReputation.id)).filter(
            SourceReputation.is_active == True
        ).scalar()
        
        tier_counts = {}
        for tier in ReputationTier:
            count = self.db.query(func.count(SourceReputation.id)).filter(
                SourceReputation.reputation_tier == tier.value
            ).scalar()
            tier_counts[tier.value] = count
        
        avg_reputation = self.db.query(
            func.avg(SourceReputation.reputation_score)
        ).filter(SourceReputation.is_active == True).scalar() or 0.0
        
        avg_quality = self.db.query(
            func.avg(SourceReputation.avg_quality_score)
        ).filter(SourceReputation.is_active == True).scalar() or 0.0
        
        return {
            "total_sources": total,
            "active_sources": active,
            "disabled_sources": total - active,
            "tier_distribution": tier_counts,
            "average_reputation": round(avg_reputation, 3),
            "average_quality_score": round(avg_quality, 1),
            "config": {
                "min_reputation_active": self.config.min_reputation_active,
                "min_article_quality": self.config.min_article_quality,
                "boost_rate": self.config.boost_rate,
                "penalty_rate": self.config.penalty_rate
            }
        }
    
    async def manually_override_source(
        self,
        source_name: str,
        is_active: bool,
        reason: str,
        override_by: str,
        duration_days: Optional[int] = None
    ) -> None:
        """Manually override source status (admin function)."""
        from app.models.source_reputation_models import SourceReputation
        
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


# Factory function
def create_reputation_manager(
    db: Session,
    config: Optional[ReputationConfig] = None
) -> ReputationManager:
    """Create a ReputationManager instance."""
    return ReputationManager(db=db, config=config)
