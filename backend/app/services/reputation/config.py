from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

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
    max_consecutive_poor_articles: int = 7
    
    # Reputation adjustment rates
    boost_rate: float = 0.01       # Boost for quality articles
    penalty_rate: float = 0.02    # Penalty for poor articles
    decay_rate: float = 0.001     # Daily decay for inactivity
    ema_alpha: float = 0.1        # Smoothing factor for EMA
    
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

class ConfigurationLoader:
    """Loads configuration and thresholds dynamically."""
    
    def __init__(self, db: Session, config: ReputationConfig):
        self.db = db
        self.config = config
        self._threshold_cache: Dict[str, float] = {}
        self._cache_loaded = False
        
    def load(self) -> ReputationConfig:
        """Load configurable thresholds from database."""
        if self._cache_loaded:
            return self.config
            
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
            if "MAX_CONSECUTIVE_POOR_ARTICLES" in self._threshold_cache:
                self.config.max_consecutive_poor_articles = int(self._threshold_cache["MAX_CONSECUTIVE_POOR_ARTICLES"])
            if "EMA_SMOOTHING_ALPHA" in self._threshold_cache:
                self.config.ema_alpha = self._threshold_cache["EMA_SMOOTHING_ALPHA"]
                
            self._cache_loaded = True
            logger.info(f"Loaded {len(self._threshold_cache)} thresholds from database")
            
        except Exception as e:
            logger.warning(f"Could not load thresholds from DB, using defaults: {e}")
            self._cache_loaded = True
            
        return self.config
