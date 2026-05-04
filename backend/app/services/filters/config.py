from dataclasses import dataclass, field
from typing import Dict, Any

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
