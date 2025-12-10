"""
Source Reputation System Models

Models for tracking source reputation, quality history, and auto-filtering.
This system enables dynamic quality control and automatic source management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, Text, ForeignKey, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class ReputationTier(str, enum.Enum):
    """Source reputation tier classification."""
    PLATINUM = "platinum"    # 0.90+ score - Premium trusted sources
    GOLD = "gold"            # 0.75-0.89 - Highly reliable
    SILVER = "silver"        # 0.60-0.74 - Generally reliable
    BRONZE = "bronze"        # 0.45-0.59 - Use with caution
    PROBATION = "probation"  # 0.30-0.44 - Needs monitoring
    BLACKLISTED = "blacklisted"  # <0.30 - Disabled


class FilterAction(str, enum.Enum):
    """Action taken during quality filtering."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FLAGGED = "flagged"       # Needs review
    BOOSTED = "boosted"       # High-quality source bonus
    DOWNGRADED = "downgraded" # Quality penalty applied


class SourceReputation(Base):
    """
    Dynamic source reputation tracking.
    
    Updates based on article quality, accuracy, and cross-verification.
    This replaces static credibility_score with a living metric.
    """
    __tablename__ = "source_reputation"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), unique=True, nullable=False, index=True)
    source_url = Column(String(500), nullable=True)
    source_type = Column(String(50), default="news")  # news, social, government, blog
    
    # Current Reputation Score (0.00 - 1.00)
    reputation_score = Column(Float, default=0.75, nullable=False)
    reputation_tier = Column(String(20), default="silver")
    
    # Base scores (initial configuration)
    initial_credibility = Column(Float, default=0.75)  # Original static score
    
    # Quality metrics (rolling averages)
    avg_quality_score = Column(Float, default=70.0)  # 0-100, from QualityScorer
    avg_confidence_score = Column(Float, default=0.7)  # 0-1, classification confidence
    
    # Accuracy tracking
    accuracy_rate = Column(Float, default=0.8)  # How often predictions match reality
    cross_verification_rate = Column(Float, default=0.5)  # How often verified by others
    
    # Volume & consistency
    total_articles = Column(Integer, default=0)
    articles_last_30_days = Column(Integer, default=0)
    accepted_articles = Column(Integer, default=0)
    rejected_articles = Column(Integer, default=0)
    flagged_articles = Column(Integer, default=0)
    
    # Acceptance rate = accepted / (accepted + rejected)
    acceptance_rate = Column(Float, default=1.0)
    
    # Trend indicators
    is_improving = Column(Boolean, default=True)
    is_declining = Column(Boolean, default=False)
    consecutive_quality_days = Column(Integer, default=0)  # Days above threshold
    consecutive_poor_days = Column(Integer, default=0)     # Days below threshold
    
    # Alerts & status
    is_active = Column(Boolean, default=True)
    is_manually_overridden = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    override_by = Column(String(100), nullable=True)
    override_until = Column(DateTime, nullable=True)
    
    # Last activity
    last_article_at = Column(DateTime, nullable=True)
    last_evaluated_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    history = relationship("SourceReputationHistory", back_populates="source", lazy="dynamic")
    filter_logs = relationship("QualityFilterLog", back_populates="source", lazy="dynamic")
    
    __table_args__ = (
        CheckConstraint('reputation_score >= 0.0 AND reputation_score <= 1.0', 
                        name='check_reputation_score_range'),
        CheckConstraint('acceptance_rate >= 0.0 AND acceptance_rate <= 1.0',
                        name='check_acceptance_rate_range'),
        Index('idx_source_reputation_tier', 'reputation_tier'),
        Index('idx_source_is_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<SourceReputation {self.source_name}: {self.reputation_score:.2f} ({self.reputation_tier})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "reputation_score": round(self.reputation_score, 3),
            "reputation_tier": self.reputation_tier,
            "avg_quality_score": round(self.avg_quality_score, 1),
            "acceptance_rate": round(self.acceptance_rate, 3),
            "total_articles": self.total_articles,
            "is_active": self.is_active,
            "is_improving": self.is_improving,
            "last_evaluated_at": self.last_evaluated_at.isoformat() if self.last_evaluated_at else None
        }


class SourceReputationHistory(Base):
    """
    Historical reputation snapshots for trend analysis.
    
    Stores daily snapshots to track reputation changes over time
    and enable trend detection.
    """
    __tablename__ = "source_reputation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("source_reputation.id"), nullable=False, index=True)
    snapshot_date = Column(DateTime, nullable=False, index=True)
    
    # Snapshot of scores at this time
    reputation_score = Column(Float, nullable=False)
    reputation_tier = Column(String(20), nullable=False)
    avg_quality_score = Column(Float, nullable=False)
    
    # Activity in this period
    articles_count = Column(Integer, default=0)
    accepted_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    flagged_count = Column(Integer, default=0)
    
    # Comparison to previous
    score_change = Column(Float, default=0.0)  # vs previous snapshot
    tier_changed = Column(Boolean, default=False)
    
    # Computed metrics
    acceptance_rate = Column(Float, default=1.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    source = relationship("SourceReputation", back_populates="history")
    
    __table_args__ = (
        Index('idx_reputation_history_source_date', 'source_id', 'snapshot_date'),
    )
    
    def __repr__(self):
        return f"<ReputationHistory source={self.source_id} date={self.snapshot_date} score={self.reputation_score:.2f}>"


class QualityFilterLog(Base):
    """
    Log of all quality filtering decisions.
    
    Records every article that passes through the quality filter
    for auditing and analysis.
    """
    __tablename__ = "quality_filter_log"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(String(100), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("source_reputation.id"), nullable=False, index=True)
    
    # Filter decision
    action = Column(String(20), nullable=False, index=True)  # accepted/rejected/flagged
    action_reason = Column(Text, nullable=True)
    
    # Scores at time of filtering
    source_reputation_score = Column(Float, nullable=False)
    article_quality_score = Column(Float, nullable=True)  # If calculated
    
    # Threshold used
    threshold_applied = Column(Float, nullable=True)
    
    # Weight modification (if applied)
    weight_multiplier = Column(Float, default=1.0)  # Applied to article weight
    
    # Processing time
    filter_latency_ms = Column(Integer, default=0)
    
    # Review status (for flagged items)
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String(100), nullable=True)
    review_decision = Column(String(20), nullable=True)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    source = relationship("SourceReputation", back_populates="filter_logs")
    
    __table_args__ = (
        Index('idx_filter_log_action_date', 'action', 'created_at'),
    )
    
    def __repr__(self):
        return f"<QualityFilterLog article={self.article_id} action={self.action}>"


class ReputationThreshold(Base):
    """
    Configurable thresholds for quality filtering.
    
    Allows administrators to tune the filtering system
    without code changes.
    """
    __tablename__ = "reputation_thresholds"
    
    id = Column(Integer, primary_key=True, index=True)
    threshold_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Threshold value
    value = Column(Float, nullable=False)
    
    # Type and category
    threshold_type = Column(String(50), nullable=False)  # min, max, target
    category = Column(String(50), nullable=False)  # reputation, quality, article
    
    # Active flag
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100), default="system")
    
    def __repr__(self):
        return f"<ReputationThreshold {self.threshold_name}: {self.value}>"


# Default thresholds to seed
DEFAULT_THRESHOLDS = [
    {
        "threshold_name": "MIN_REPUTATION_ACTIVE",
        "description": "Minimum reputation score to keep source active",
        "value": 0.30,
        "threshold_type": "min",
        "category": "reputation"
    },
    {
        "threshold_name": "MIN_REPUTATION_TRUSTED",
        "description": "Minimum reputation for trusted source status",
        "value": 0.75,
        "threshold_type": "min",
        "category": "reputation"
    },
    {
        "threshold_name": "MIN_ARTICLE_QUALITY",
        "description": "Minimum quality score for article acceptance",
        "value": 40.0,
        "threshold_type": "min",
        "category": "quality"
    },
    {
        "threshold_name": "WARNING_QUALITY",
        "description": "Quality score triggering warning flag",
        "value": 60.0,
        "threshold_type": "target",
        "category": "quality"
    },
    {
        "threshold_name": "EXCELLENT_QUALITY",
        "description": "Quality score for boosted weight",
        "value": 85.0,
        "threshold_type": "target",
        "category": "quality"
    },
    {
        "threshold_name": "MAX_CONSECUTIVE_POOR_DAYS",
        "description": "Days of poor performance before auto-disable",
        "value": 7.0,
        "threshold_type": "max",
        "category": "reputation"
    },
    {
        "threshold_name": "REPUTATION_DECAY_RATE",
        "description": "Daily decay rate for reputation (no activity)",
        "value": 0.001,
        "threshold_type": "target",
        "category": "reputation"
    },
    {
        "threshold_name": "REPUTATION_BOOST_RATE",
        "description": "Boost rate for quality articles",
        "value": 0.01,
        "threshold_type": "target",
        "category": "reputation"
    },
    {
        "threshold_name": "REPUTATION_PENALTY_RATE",
        "description": "Penalty rate for poor quality articles",
        "value": 0.02,
        "threshold_type": "target",
        "category": "reputation"
    }
]
