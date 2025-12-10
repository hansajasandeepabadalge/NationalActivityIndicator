"""
Source Reputation Tracker

Tracks and calculates dynamic reputation scores for news sources based on:
- Historical accuracy (confirmed vs. incorrect reports)
- Correction rate (how often source issues corrections)
- Consistency (alignment with official sources)
- Timeliness (first to report vs. following others)

Reputation decays over time to prioritize recent performance.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class ReputationTier(Enum):
    """Source reputation tiers."""
    OFFICIAL = "official"          # Government, regulatory bodies
    TIER_1 = "tier_1"              # Major established news outlets
    TIER_2 = "tier_2"              # Regional/specialized news
    TIER_3 = "tier_3"              # Blogs, social media
    UNKNOWN = "unknown"            # New or untracked sources


class SourceCategory(Enum):
    """Source type categories."""
    GOVERNMENT = "government"
    REGULATORY = "regulatory"
    MAINSTREAM_NEWS = "mainstream_news"
    REGIONAL_NEWS = "regional_news"
    WIRE_SERVICE = "wire_service"
    SOCIAL_MEDIA = "social_media"
    BLOG = "blog"
    UNKNOWN = "unknown"


@dataclass
class SourceReputation:
    """Reputation data for a single source."""
    source_id: str
    source_name: str
    category: SourceCategory
    tier: ReputationTier
    
    # Core reputation metrics (0-100)
    base_reputation: float          # Starting reputation based on tier
    current_reputation: float       # Dynamic reputation
    
    # Tracking metrics
    total_articles: int = 0
    confirmed_reports: int = 0      # Reports verified by other sources
    contradicted_reports: int = 0   # Reports contradicted by official sources
    corrections_issued: int = 0     # Self-corrections
    first_to_report: int = 0        # Breaking news count
    
    # Time tracking
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate."""
        total = self.confirmed_reports + self.contradicted_reports
        if total == 0:
            return 0.5  # Neutral for unknown
        return self.confirmed_reports / total
    
    @property
    def correction_rate(self) -> float:
        """Calculate correction rate (lower is better)."""
        if self.total_articles == 0:
            return 0.0
        return self.corrections_issued / self.total_articles
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "category": self.category.value,
            "tier": self.tier.value,
            "base_reputation": self.base_reputation,
            "current_reputation": round(self.current_reputation, 1),
            "total_articles": self.total_articles,
            "confirmed_reports": self.confirmed_reports,
            "contradicted_reports": self.contradicted_reports,
            "accuracy_rate": round(self.accuracy_rate, 3),
            "correction_rate": round(self.correction_rate, 3),
            "first_to_report": self.first_to_report,
            "last_updated": self.last_updated.isoformat()
        }


class SourceReputationTracker:
    """
    Tracks and manages source reputation over time.
    
    Features:
    - Base reputation by source tier/category
    - Dynamic reputation updates based on performance
    - Time-decayed reputation (recent performance matters more)
    - Cross-source validation tracking
    """
    
    # Base reputation by tier (0-100)
    TIER_BASE_REPUTATION: Dict[ReputationTier, float] = {
        ReputationTier.OFFICIAL: 95.0,
        ReputationTier.TIER_1: 80.0,
        ReputationTier.TIER_2: 65.0,
        ReputationTier.TIER_3: 40.0,
        ReputationTier.UNKNOWN: 30.0
    }
    
    # Known sources with their categories and tiers (Sri Lanka specific)
    KNOWN_SOURCES: Dict[str, Dict[str, Any]] = {
        # Official Government Sources
        "government": {"category": SourceCategory.GOVERNMENT, "tier": ReputationTier.OFFICIAL},
        "dmc": {"category": SourceCategory.GOVERNMENT, "tier": ReputationTier.OFFICIAL},
        "central_bank": {"category": SourceCategory.REGULATORY, "tier": ReputationTier.OFFICIAL},
        "cbsl": {"category": SourceCategory.REGULATORY, "tier": ReputationTier.OFFICIAL},
        "president": {"category": SourceCategory.GOVERNMENT, "tier": ReputationTier.OFFICIAL},
        "prime_minister": {"category": SourceCategory.GOVERNMENT, "tier": ReputationTier.OFFICIAL},
        "ministry": {"category": SourceCategory.GOVERNMENT, "tier": ReputationTier.OFFICIAL},
        "parliament": {"category": SourceCategory.GOVERNMENT, "tier": ReputationTier.OFFICIAL},
        "met_department": {"category": SourceCategory.GOVERNMENT, "tier": ReputationTier.OFFICIAL},
        "elections_commission": {"category": SourceCategory.GOVERNMENT, "tier": ReputationTier.OFFICIAL},
        
        # Wire Services
        "reuters": {"category": SourceCategory.WIRE_SERVICE, "tier": ReputationTier.TIER_1},
        "afp": {"category": SourceCategory.WIRE_SERVICE, "tier": ReputationTier.TIER_1},
        "ap": {"category": SourceCategory.WIRE_SERVICE, "tier": ReputationTier.TIER_1},
        
        # Tier 1 News Outlets
        "daily_mirror": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        "daily_news": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        "sunday_times": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        "island": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        "ada_derana": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        "hiru_news": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        "newsfirst": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        "lankadeepa": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        "divaina": {"category": SourceCategory.MAINSTREAM_NEWS, "tier": ReputationTier.TIER_1},
        
        # Tier 2 News Outlets
        "economynext": {"category": SourceCategory.REGIONAL_NEWS, "tier": ReputationTier.TIER_2},
        "colombo_gazette": {"category": SourceCategory.REGIONAL_NEWS, "tier": ReputationTier.TIER_2},
        "news_lk": {"category": SourceCategory.REGIONAL_NEWS, "tier": ReputationTier.TIER_2},
        "ceylon_today": {"category": SourceCategory.REGIONAL_NEWS, "tier": ReputationTier.TIER_2},
        
        # Social Media
        "twitter": {"category": SourceCategory.SOCIAL_MEDIA, "tier": ReputationTier.TIER_3},
        "facebook": {"category": SourceCategory.SOCIAL_MEDIA, "tier": ReputationTier.TIER_3},
    }
    
    # Reputation update weights
    CONFIRMATION_BOOST = 2.0       # Points gained when report is confirmed
    CONTRADICTION_PENALTY = 5.0    # Points lost when report is contradicted
    CORRECTION_PENALTY = 1.0       # Points lost when source issues correction
    FIRST_TO_REPORT_BOOST = 1.5    # Bonus for breaking news (if confirmed)
    
    # Decay settings
    DECAY_HALF_LIFE_DAYS = 90      # Reputation changes decay to 50% after this many days
    
    def __init__(self):
        """Initialize the source reputation tracker."""
        # In-memory reputation cache
        self._reputations: Dict[str, SourceReputation] = {}
        
        # Recent events for decay calculation
        self._reputation_events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        logger.info("SourceReputationTracker initialized")
    
    def get_reputation(self, source_name: str) -> SourceReputation:
        """
        Get reputation for a source.
        
        Creates a new reputation entry if source is unknown.
        
        Args:
            source_name: Source identifier
            
        Returns:
            SourceReputation object
        """
        source_id = self._normalize_source_id(source_name)
        
        if source_id not in self._reputations:
            self._reputations[source_id] = self._create_reputation(source_id, source_name)
        
        return self._reputations[source_id]
    
    def get_reputation_score(self, source_name: str) -> float:
        """
        Get numeric reputation score for a source.
        
        Args:
            source_name: Source identifier
            
        Returns:
            Reputation score 0-100
        """
        reputation = self.get_reputation(source_name)
        return reputation.current_reputation
    
    def record_article(self, source_name: str):
        """Record that an article was received from source."""
        reputation = self.get_reputation(source_name)
        reputation.total_articles += 1
        reputation.last_updated = datetime.utcnow()
    
    def record_confirmation(
        self,
        source_name: str,
        confirming_sources: List[str],
        was_first_to_report: bool = False
    ):
        """
        Record that a source's report was confirmed by others.
        
        Args:
            source_name: Source that made the original report
            confirming_sources: Sources that confirmed the report
            was_first_to_report: Whether this source broke the news
        """
        reputation = self.get_reputation(source_name)
        reputation.confirmed_reports += 1
        reputation.last_updated = datetime.utcnow()
        
        if was_first_to_report:
            reputation.first_to_report += 1
        
        # Calculate reputation boost
        boost = self.CONFIRMATION_BOOST
        
        # Extra boost if confirmed by official sources
        official_confirmations = sum(
            1 for s in confirming_sources
            if self._get_source_tier(s) == ReputationTier.OFFICIAL
        )
        boost += official_confirmations * 0.5
        
        # Extra boost for first to report
        if was_first_to_report:
            boost += self.FIRST_TO_REPORT_BOOST
        
        # Apply boost with decay
        self._apply_reputation_change(reputation, boost)
        
        # Record event
        self._record_event(reputation.source_id, "confirmation", boost)
    
    def record_contradiction(
        self,
        source_name: str,
        contradicting_sources: List[str]
    ):
        """
        Record that a source's report was contradicted.
        
        Args:
            source_name: Source that made the contradicted report
            contradicting_sources: Sources that contradicted the report
        """
        reputation = self.get_reputation(source_name)
        reputation.contradicted_reports += 1
        reputation.last_updated = datetime.utcnow()
        
        # Calculate penalty
        penalty = self.CONTRADICTION_PENALTY
        
        # Higher penalty if contradicted by official sources
        official_contradictions = sum(
            1 for s in contradicting_sources
            if self._get_source_tier(s) == ReputationTier.OFFICIAL
        )
        penalty += official_contradictions * 2.0
        
        # Apply penalty
        self._apply_reputation_change(reputation, -penalty)
        
        # Record event
        self._record_event(reputation.source_id, "contradiction", -penalty)
    
    def record_correction(self, source_name: str):
        """
        Record that a source issued a correction.
        
        Corrections are a minor negative (shows errors) but also
        a slight positive (shows integrity to correct).
        """
        reputation = self.get_reputation(source_name)
        reputation.corrections_issued += 1
        reputation.last_updated = datetime.utcnow()
        
        # Small penalty for needing correction
        self._apply_reputation_change(reputation, -self.CORRECTION_PENALTY)
        
        # Record event
        self._record_event(reputation.source_id, "correction", -self.CORRECTION_PENALTY)
    
    def get_source_tier(self, source_name: str) -> ReputationTier:
        """Get the tier for a source."""
        return self._get_source_tier(source_name)
    
    def get_source_category(self, source_name: str) -> SourceCategory:
        """Get the category for a source."""
        source_id = self._normalize_source_id(source_name)
        
        if source_id in self.KNOWN_SOURCES:
            return self.KNOWN_SOURCES[source_id]["category"]
        
        # Try partial matches
        for known_id, info in self.KNOWN_SOURCES.items():
            if known_id in source_id or source_id in known_id:
                return info["category"]
        
        return SourceCategory.UNKNOWN
    
    def recalculate_reputation(self, source_name: str) -> float:
        """
        Recalculate reputation with time decay.
        
        Args:
            source_name: Source identifier
            
        Returns:
            New reputation score
        """
        reputation = self.get_reputation(source_name)
        events = self._reputation_events.get(reputation.source_id, [])
        
        if not events:
            return reputation.current_reputation
        
        # Start from base reputation
        decayed_total = 0.0
        weight_total = 0.0
        
        now = datetime.utcnow()
        
        for event in events:
            event_time = event.get("timestamp", now)
            age_days = (now - event_time).days
            
            # Calculate decay weight (exponential decay)
            decay_weight = math.exp(-0.693 * age_days / self.DECAY_HALF_LIFE_DAYS)
            
            change = event.get("change", 0)
            decayed_total += change * decay_weight
            weight_total += decay_weight
        
        # Apply decayed changes to base reputation
        if weight_total > 0:
            avg_change = decayed_total / weight_total
            reputation.current_reputation = max(0, min(100, 
                reputation.base_reputation + avg_change * 5  # Scale factor
            ))
        
        return reputation.current_reputation
    
    def get_all_reputations(self) -> List[SourceReputation]:
        """Get all tracked source reputations."""
        return list(self._reputations.values())
    
    def get_top_sources(self, limit: int = 10) -> List[SourceReputation]:
        """Get top sources by reputation."""
        reputations = list(self._reputations.values())
        reputations.sort(key=lambda x: x.current_reputation, reverse=True)
        return reputations[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        reputations = list(self._reputations.values())
        
        if not reputations:
            return {
                "total_sources": 0,
                "avg_reputation": 0,
                "by_tier": {},
                "by_category": {}
            }
        
        avg_rep = sum(r.current_reputation for r in reputations) / len(reputations)
        
        by_tier = defaultdict(list)
        for r in reputations:
            by_tier[r.tier.value].append(r.current_reputation)
        
        by_category = defaultdict(list)
        for r in reputations:
            by_category[r.category.value].append(r.current_reputation)
        
        return {
            "total_sources": len(reputations),
            "avg_reputation": round(avg_rep, 1),
            "by_tier": {k: round(sum(v)/len(v), 1) for k, v in by_tier.items()},
            "by_category": {k: round(sum(v)/len(v), 1) for k, v in by_category.items()},
            "total_articles_tracked": sum(r.total_articles for r in reputations),
            "total_confirmations": sum(r.confirmed_reports for r in reputations),
            "total_contradictions": sum(r.contradicted_reports for r in reputations)
        }
    
    def _normalize_source_id(self, source_name: str) -> str:
        """Normalize source name to ID."""
        return source_name.lower().replace(" ", "_").replace("-", "_")
    
    def _get_source_tier(self, source_name: str) -> ReputationTier:
        """Get tier for a source."""
        source_id = self._normalize_source_id(source_name)
        
        if source_id in self.KNOWN_SOURCES:
            return self.KNOWN_SOURCES[source_id]["tier"]
        
        # Try partial matches
        for known_id, info in self.KNOWN_SOURCES.items():
            if known_id in source_id or source_id in known_id:
                return info["tier"]
        
        return ReputationTier.UNKNOWN
    
    def _create_reputation(self, source_id: str, source_name: str) -> SourceReputation:
        """Create a new reputation entry for a source."""
        tier = self._get_source_tier(source_name)
        category = self.get_source_category(source_name)
        base_rep = self.TIER_BASE_REPUTATION[tier]
        
        return SourceReputation(
            source_id=source_id,
            source_name=source_name,
            category=category,
            tier=tier,
            base_reputation=base_rep,
            current_reputation=base_rep
        )
    
    def _apply_reputation_change(self, reputation: SourceReputation, change: float):
        """Apply a reputation change with bounds checking."""
        new_rep = reputation.current_reputation + change
        reputation.current_reputation = max(0, min(100, new_rep))
    
    def _record_event(self, source_id: str, event_type: str, change: float):
        """Record a reputation event for decay calculation."""
        self._reputation_events[source_id].append({
            "type": event_type,
            "change": change,
            "timestamp": datetime.utcnow()
        })
        
        # Keep only last 100 events per source
        if len(self._reputation_events[source_id]) > 100:
            self._reputation_events[source_id] = self._reputation_events[source_id][-100:]
