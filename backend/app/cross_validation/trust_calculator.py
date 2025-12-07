"""
Trust Calculator

Calculates final trust scores by combining multiple factors:
- Source reputation (30%)
- Corroboration score (35%)
- Source diversity (20%)
- Recency match (15%)

Produces trust levels and detailed breakdowns.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .source_reputation import SourceReputationTracker, SourceReputation
from .corroboration_engine import CorroborationResult, CorroborationLevel

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels based on validation score."""
    VERIFIED = "verified"          # 85-100: Multiple credible sources confirm
    HIGH_TRUST = "high_trust"      # 70-84: At least 2 sources confirm
    MODERATE = "moderate"          # 50-69: Single credible source
    LOW_TRUST = "low_trust"        # 30-49: Unverified or conflicting
    UNVERIFIED = "unverified"      # 0-29: No corroboration


@dataclass
class TrustFactorScore:
    """Score for a single trust factor."""
    factor_name: str
    score: float               # 0-100
    weight: float              # Factor weight
    weighted_score: float      # score * weight
    details: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "factor": self.factor_name,
            "score": round(self.score, 1),
            "weight": self.weight,
            "weighted_score": round(self.weighted_score, 2),
            "details": self.details
        }


@dataclass
class TrustScore:
    """Complete trust score with breakdown."""
    article_id: str
    source_name: str
    
    # Overall score
    total_score: float         # 0-100
    trust_level: TrustLevel
    
    # Factor scores
    source_reputation_score: TrustFactorScore
    corroboration_score: TrustFactorScore
    source_diversity_score: TrustFactorScore
    recency_score: TrustFactorScore
    
    # Additional factors
    has_official_confirmation: bool = False
    has_conflicts: bool = False
    conflict_severity: float = 0.0
    
    # Metadata
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.8
    
    @property
    def factor_scores(self) -> List[TrustFactorScore]:
        return [
            self.source_reputation_score,
            self.corroboration_score,
            self.source_diversity_score,
            self.recency_score
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "article_id": self.article_id,
            "source": self.source_name,
            "total_score": round(self.total_score, 1),
            "trust_level": self.trust_level.value,
            "factors": [f.to_dict() for f in self.factor_scores],
            "has_official_confirmation": self.has_official_confirmation,
            "has_conflicts": self.has_conflicts,
            "conflict_severity": round(self.conflict_severity, 2),
            "confidence": round(self.confidence, 2),
            "calculated_at": self.calculated_at.isoformat()
        }


class TrustCalculator:
    """
    Calculates trust scores using multiple weighted factors.
    
    Factor weights (total = 100%):
    - Source Reputation: 30%
    - Corroboration: 35%
    - Source Diversity: 20%
    - Recency Match: 15%
    """
    
    # Factor weights
    WEIGHT_SOURCE_REPUTATION = 0.30
    WEIGHT_CORROBORATION = 0.35
    WEIGHT_SOURCE_DIVERSITY = 0.20
    WEIGHT_RECENCY = 0.15
    
    # Trust level thresholds
    THRESHOLD_VERIFIED = 85
    THRESHOLD_HIGH_TRUST = 70
    THRESHOLD_MODERATE = 50
    THRESHOLD_LOW_TRUST = 30
    
    # Source diversity scoring
    MAX_DIVERSITY_SOURCES = 5      # Max sources for full diversity score
    TIER_DIVERSITY_BONUS = 10      # Bonus for each unique tier
    
    # Recency scoring
    RECENCY_WINDOW_HOURS = 24      # Optimal recency window
    RECENCY_DECAY_HOURS = 72       # After this, recency score drops significantly
    
    # Conflict penalties
    CONFLICT_PENALTY_BASE = 15
    OFFICIAL_CONFLICT_PENALTY = 25
    
    def __init__(
        self,
        reputation_tracker: Optional[SourceReputationTracker] = None
    ):
        """
        Initialize the trust calculator.
        
        Args:
            reputation_tracker: Source reputation tracker
        """
        self._reputation_tracker = reputation_tracker or SourceReputationTracker()
        
        logger.info("TrustCalculator initialized")
    
    def set_reputation_tracker(self, tracker: SourceReputationTracker):
        """Set the reputation tracker."""
        self._reputation_tracker = tracker
    
    def calculate_trust(
        self,
        article_id: str,
        source_name: str,
        corroboration_result: Optional[CorroborationResult] = None,
        published_at: Optional[datetime] = None
    ) -> TrustScore:
        """
        Calculate trust score for an article.
        
        Args:
            article_id: Article identifier
            source_name: Source name
            corroboration_result: Corroboration analysis result
            published_at: Article publication time
            
        Returns:
            TrustScore with breakdown
        """
        pub_time = published_at or datetime.utcnow()
        
        # Calculate each factor
        reputation_factor = self._calculate_reputation_score(source_name)
        corroboration_factor = self._calculate_corroboration_score(corroboration_result)
        diversity_factor = self._calculate_diversity_score(corroboration_result)
        recency_factor = self._calculate_recency_score(corroboration_result, pub_time)
        
        # Calculate total weighted score
        total_score = (
            reputation_factor.weighted_score +
            corroboration_factor.weighted_score +
            diversity_factor.weighted_score +
            recency_factor.weighted_score
        )
        
        # Check for conflicts
        has_conflicts = False
        conflict_severity = 0.0
        if corroboration_result:
            has_conflicts = len(corroboration_result.conflicting_articles) > 0
            if has_conflicts:
                conflict_severity = self._calculate_conflict_severity(corroboration_result)
                total_score -= conflict_severity
        
        # Bound score
        total_score = max(0, min(100, total_score))
        
        # Determine trust level
        trust_level = self._determine_trust_level(total_score)
        
        # Check for official confirmation
        has_official = False
        if corroboration_result:
            has_official = "official" in corroboration_result.source_tiers_represented
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(corroboration_result)
        
        return TrustScore(
            article_id=article_id,
            source_name=source_name,
            total_score=total_score,
            trust_level=trust_level,
            source_reputation_score=reputation_factor,
            corroboration_score=corroboration_factor,
            source_diversity_score=diversity_factor,
            recency_score=recency_factor,
            has_official_confirmation=has_official,
            has_conflicts=has_conflicts,
            conflict_severity=conflict_severity,
            confidence=confidence
        )
    
    def batch_calculate(
        self,
        articles: List[Dict[str, Any]],
        corroboration_results: Dict[str, CorroborationResult] = None
    ) -> List[TrustScore]:
        """
        Calculate trust scores for multiple articles.
        
        Args:
            articles: List of article dictionaries
            corroboration_results: Dict mapping article_id to CorroborationResult
            
        Returns:
            List of TrustScore objects
        """
        results = []
        corroboration_results = corroboration_results or {}
        
        for article in articles:
            article_id = article.get("article_id", article.get("id", ""))
            source_name = article.get("source_name", article.get("source", ""))
            published_at = article.get("published_at")
            
            corr_result = corroboration_results.get(article_id)
            
            trust_score = self.calculate_trust(
                article_id=article_id,
                source_name=source_name,
                corroboration_result=corr_result,
                published_at=published_at
            )
            
            results.append(trust_score)
        
        return results
    
    def _calculate_reputation_score(self, source_name: str) -> TrustFactorScore:
        """Calculate reputation factor score."""
        reputation = self._reputation_tracker.get_reputation(source_name)
        score = reputation.current_reputation
        
        details = f"{source_name}: {reputation.tier.value} tier, {score:.0f} reputation"
        
        return TrustFactorScore(
            factor_name="source_reputation",
            score=score,
            weight=self.WEIGHT_SOURCE_REPUTATION,
            weighted_score=score * self.WEIGHT_SOURCE_REPUTATION,
            details=details
        )
    
    def _calculate_corroboration_score(
        self,
        corroboration_result: Optional[CorroborationResult]
    ) -> TrustFactorScore:
        """Calculate corroboration factor score."""
        if not corroboration_result:
            return TrustFactorScore(
                factor_name="corroboration",
                score=30,  # Base score for unchecked
                weight=self.WEIGHT_CORROBORATION,
                weighted_score=30 * self.WEIGHT_CORROBORATION,
                details="No corroboration data available"
            )
        
        score = corroboration_result.corroboration_score
        corr_count = len(corroboration_result.corroborating_articles)
        level = corroboration_result.corroboration_level.value
        
        details = f"{corr_count} corroborating sources, level: {level}"
        
        return TrustFactorScore(
            factor_name="corroboration",
            score=score,
            weight=self.WEIGHT_CORROBORATION,
            weighted_score=score * self.WEIGHT_CORROBORATION,
            details=details
        )
    
    def _calculate_diversity_score(
        self,
        corroboration_result: Optional[CorroborationResult]
    ) -> TrustFactorScore:
        """Calculate source diversity factor score."""
        if not corroboration_result:
            return TrustFactorScore(
                factor_name="source_diversity",
                score=0,
                weight=self.WEIGHT_SOURCE_DIVERSITY,
                weighted_score=0,
                details="No diversity data available"
            )
        
        # Base score from number of unique sources
        unique_sources = corroboration_result.unique_sources
        source_score = min(100, (unique_sources / self.MAX_DIVERSITY_SOURCES) * 100)
        
        # Bonus for tier diversity
        tier_count = len(corroboration_result.source_tiers_represented)
        tier_bonus = min(30, tier_count * self.TIER_DIVERSITY_BONUS)
        
        # Extra bonus for official sources
        if "official" in corroboration_result.source_tiers_represented:
            tier_bonus += 10
        
        score = min(100, source_score + tier_bonus)
        
        details = f"{unique_sources} unique sources across {tier_count} tiers"
        
        return TrustFactorScore(
            factor_name="source_diversity",
            score=score,
            weight=self.WEIGHT_SOURCE_DIVERSITY,
            weighted_score=score * self.WEIGHT_SOURCE_DIVERSITY,
            details=details
        )
    
    def _calculate_recency_score(
        self,
        corroboration_result: Optional[CorroborationResult],
        published_at: datetime
    ) -> TrustFactorScore:
        """Calculate recency match factor score."""
        now = datetime.utcnow()
        
        # Base recency score (how recent is the article)
        age_hours = (now - published_at).total_seconds() / 3600
        
        if age_hours <= self.RECENCY_WINDOW_HOURS:
            base_score = 100
        elif age_hours <= self.RECENCY_DECAY_HOURS:
            decay_factor = (age_hours - self.RECENCY_WINDOW_HOURS) / (
                self.RECENCY_DECAY_HOURS - self.RECENCY_WINDOW_HOURS
            )
            base_score = 100 - (decay_factor * 50)  # Decay to 50
        else:
            base_score = max(20, 50 - (age_hours - self.RECENCY_DECAY_HOURS) / 24 * 5)
        
        # Bonus if corroborating articles are timely
        if corroboration_result and corroboration_result.corroborating_articles:
            # Check if corroboration came within recency window
            earliest = corroboration_result.earliest_report
            if earliest:
                corr_age = (now - earliest).total_seconds() / 3600
                if corr_age <= self.RECENCY_WINDOW_HOURS:
                    base_score += 10
        
        score = min(100, base_score)
        
        details = f"Article age: {age_hours:.1f}h"
        
        return TrustFactorScore(
            factor_name="recency",
            score=score,
            weight=self.WEIGHT_RECENCY,
            weighted_score=score * self.WEIGHT_RECENCY,
            details=details
        )
    
    def _calculate_conflict_severity(
        self,
        corroboration_result: CorroborationResult
    ) -> float:
        """Calculate severity of conflicts."""
        severity = 0.0
        
        for conflict in corroboration_result.conflicting_articles:
            if conflict.source_tier == "official":
                severity += self.OFFICIAL_CONFLICT_PENALTY
            else:
                severity += self.CONFLICT_PENALTY_BASE
        
        return min(50, severity)  # Cap at 50 points
    
    def _determine_trust_level(self, score: float) -> TrustLevel:
        """Determine trust level from score."""
        if score >= self.THRESHOLD_VERIFIED:
            return TrustLevel.VERIFIED
        elif score >= self.THRESHOLD_HIGH_TRUST:
            return TrustLevel.HIGH_TRUST
        elif score >= self.THRESHOLD_MODERATE:
            return TrustLevel.MODERATE
        elif score >= self.THRESHOLD_LOW_TRUST:
            return TrustLevel.LOW_TRUST
        else:
            return TrustLevel.UNVERIFIED
    
    def _calculate_confidence(
        self,
        corroboration_result: Optional[CorroborationResult]
    ) -> float:
        """Calculate confidence in the trust score."""
        if not corroboration_result:
            return 0.5  # Low confidence without corroboration data
        
        # Higher confidence with more sources
        source_confidence = min(1.0, 
            0.6 + (corroboration_result.unique_sources * 0.1)
        )
        
        # Reduce confidence if there are conflicts
        if corroboration_result.conflicting_articles:
            conflict_factor = 1.0 - (
                len(corroboration_result.conflicting_articles) * 0.1
            )
            source_confidence *= max(0.5, conflict_factor)
        
        return round(source_confidence, 2)
    
    def get_trust_summary(self, trust_scores: List[TrustScore]) -> Dict[str, Any]:
        """Get summary statistics for a set of trust scores."""
        if not trust_scores:
            return {
                "total_articles": 0,
                "avg_trust_score": 0,
                "by_level": {},
                "verified_count": 0,
                "conflicts_detected": 0
            }
        
        by_level = {}
        for level in TrustLevel:
            by_level[level.value] = sum(
                1 for ts in trust_scores if ts.trust_level == level
            )
        
        return {
            "total_articles": len(trust_scores),
            "avg_trust_score": round(
                sum(ts.total_score for ts in trust_scores) / len(trust_scores), 1
            ),
            "by_level": by_level,
            "verified_count": by_level.get("verified", 0),
            "high_trust_count": by_level.get("high_trust", 0),
            "conflicts_detected": sum(1 for ts in trust_scores if ts.has_conflicts),
            "official_confirmations": sum(
                1 for ts in trust_scores if ts.has_official_confirmation
            ),
            "avg_confidence": round(
                sum(ts.confidence for ts in trust_scores) / len(trust_scores), 2
            )
        }
