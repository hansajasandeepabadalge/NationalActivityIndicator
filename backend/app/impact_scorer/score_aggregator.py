"""
Score Aggregator

Combines multiple factor scores into a weighted final impact score.
Supports configurable weights for different use cases.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from app.impact_scorer.multi_factor_analyzer import FactorScores
from app.impact_scorer.sector_engine import SectorAnalysisResult

logger = logging.getLogger(__name__)


class ScoringProfile(Enum):
    """Pre-defined scoring weight profiles."""
    BALANCED = "balanced"           # Equal emphasis on all factors
    URGENCY_FOCUSED = "urgency"     # Prioritize time-sensitive events
    BUSINESS_FOCUSED = "business"   # Prioritize sector relevance
    CREDIBILITY_FOCUSED = "credibility"  # Prioritize source reliability


@dataclass
class WeightConfig:
    """Configuration for scoring factor weights."""
    severity_weight: float = 0.25
    sector_weight: float = 0.25
    credibility_weight: float = 0.15
    geographic_weight: float = 0.10
    temporal_weight: float = 0.15
    volume_weight: float = 0.10
    
    def validate(self) -> bool:
        """Validate weights sum to 1.0."""
        total = (self.severity_weight + self.sector_weight + 
                 self.credibility_weight + self.geographic_weight +
                 self.temporal_weight + self.volume_weight)
        return abs(total - 1.0) < 0.01
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "severity": self.severity_weight,
            "sector": self.sector_weight,
            "credibility": self.credibility_weight,
            "geographic": self.geographic_weight,
            "temporal": self.temporal_weight,
            "volume": self.volume_weight
        }


# Pre-defined weight profiles
WEIGHT_PROFILES: Dict[ScoringProfile, WeightConfig] = {
    ScoringProfile.BALANCED: WeightConfig(
        severity_weight=0.25,
        sector_weight=0.25,
        credibility_weight=0.15,
        geographic_weight=0.10,
        temporal_weight=0.15,
        volume_weight=0.10
    ),
    ScoringProfile.URGENCY_FOCUSED: WeightConfig(
        severity_weight=0.30,
        sector_weight=0.15,
        credibility_weight=0.15,
        geographic_weight=0.05,
        temporal_weight=0.30,
        volume_weight=0.05
    ),
    ScoringProfile.BUSINESS_FOCUSED: WeightConfig(
        severity_weight=0.20,
        sector_weight=0.35,
        credibility_weight=0.15,
        geographic_weight=0.10,
        temporal_weight=0.10,
        volume_weight=0.10
    ),
    ScoringProfile.CREDIBILITY_FOCUSED: WeightConfig(
        severity_weight=0.20,
        sector_weight=0.20,
        credibility_weight=0.30,
        geographic_weight=0.10,
        temporal_weight=0.10,
        volume_weight=0.10
    )
}


@dataclass
class AggregatedScore:
    """Final aggregated impact score with breakdown."""
    final_score: float              # 0-100 final weighted score
    priority_rank: int              # 1-5 priority ranking
    priority_label: str             # "critical", "high", etc.
    
    # Individual factor contributions
    factor_scores: Dict[str, float]
    factor_contributions: Dict[str, float]  # Actual contribution to final
    
    # Metadata
    confidence: float               # Overall confidence 0-1
    weights_used: Dict[str, float]
    scoring_profile: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "final_score": self.final_score,
            "priority_rank": self.priority_rank,
            "priority_label": self.priority_label,
            "factor_scores": self.factor_scores,
            "factor_contributions": self.factor_contributions,
            "confidence": self.confidence,
            "weights_used": self.weights_used,
            "scoring_profile": self.scoring_profile
        }


class ScoreAggregator:
    """
    Aggregates multiple factor scores into final impact score.
    
    Features:
    - Configurable weight profiles
    - Priority rank calculation
    - Factor contribution breakdown
    - Confidence-adjusted scoring
    """
    
    # Priority thresholds (score → rank)
    PRIORITY_THRESHOLDS = [
        (85, 1, "critical"),
        (70, 2, "high"),
        (50, 3, "medium"),
        (30, 4, "low"),
        (0, 5, "minimal")
    ]
    
    def __init__(
        self,
        profile: ScoringProfile = ScoringProfile.BALANCED,
        custom_weights: Optional[WeightConfig] = None
    ):
        """
        Initialize score aggregator.
        
        Args:
            profile: Pre-defined weight profile to use
            custom_weights: Custom weight configuration (overrides profile)
        """
        if custom_weights:
            self.weights = custom_weights
            self.profile_name = "custom"
        else:
            self.weights = WEIGHT_PROFILES[profile]
            self.profile_name = profile.value
        
        if not self.weights.validate():
            raise ValueError("Weight configuration must sum to 1.0")
        
        logger.info(f"ScoreAggregator initialized with profile: {self.profile_name}")
    
    def aggregate(
        self,
        factor_scores: FactorScores,
        sector_result: Optional[SectorAnalysisResult] = None,
        apply_confidence: bool = True
    ) -> AggregatedScore:
        """
        Aggregate all factor scores into final impact score.
        
        Args:
            factor_scores: Multi-factor analysis results
            sector_result: Sector analysis results (optional)
            apply_confidence: Whether to adjust score by confidence
            
        Returns:
            AggregatedScore with final score and breakdown
        """
        # Get sector score from sector analysis or factor scores
        if sector_result:
            sector_score = sector_result.overall_sector_score
        else:
            sector_score = 50.0  # Default neutral sector score
        
        # Build factor score dictionary
        scores = {
            "severity": factor_scores.severity_score,
            "sector": sector_score,
            "credibility": factor_scores.credibility_score,
            "geographic": factor_scores.geographic_score,
            "temporal": factor_scores.temporal_score,
            "volume": factor_scores.volume_score
        }
        
        # Calculate weighted contributions
        contributions = {
            "severity": scores["severity"] * self.weights.severity_weight,
            "sector": scores["sector"] * self.weights.sector_weight,
            "credibility": scores["credibility"] * self.weights.credibility_weight,
            "geographic": scores["geographic"] * self.weights.geographic_weight,
            "temporal": scores["temporal"] * self.weights.temporal_weight,
            "volume": scores["volume"] * self.weights.volume_weight
        }
        
        # Sum to get raw score
        raw_score = sum(contributions.values())
        
        # Apply confidence adjustment if enabled
        if apply_confidence:
            # Confidence adjusts score toward median (50) for low confidence
            # High confidence keeps score as-is
            confidence = factor_scores.confidence
            adjusted_score = (raw_score * confidence) + (50 * (1 - confidence) * 0.3)
            final_score = min(adjusted_score, 100)
        else:
            final_score = raw_score
        
        # Determine priority
        priority_rank, priority_label = self._calculate_priority(final_score)
        
        return AggregatedScore(
            final_score=round(final_score, 1),
            priority_rank=priority_rank,
            priority_label=priority_label,
            factor_scores=scores,
            factor_contributions={k: round(v, 2) for k, v in contributions.items()},
            confidence=factor_scores.confidence,
            weights_used=self.weights.to_dict(),
            scoring_profile=self.profile_name
        )
    
    def _calculate_priority(self, score: float) -> tuple:
        """Calculate priority rank and label from score."""
        for threshold, rank, label in self.PRIORITY_THRESHOLDS:
            if score >= threshold:
                return rank, label
        return 5, "minimal"
    
    def recalculate_with_profile(
        self,
        factor_scores: FactorScores,
        sector_result: Optional[SectorAnalysisResult],
        profile: ScoringProfile
    ) -> AggregatedScore:
        """
        Recalculate score with different weight profile.
        
        Args:
            factor_scores: Multi-factor analysis results
            sector_result: Sector analysis results
            profile: New profile to use
            
        Returns:
            New AggregatedScore with updated weights
        """
        old_weights = self.weights
        old_profile = self.profile_name
        
        try:
            self.weights = WEIGHT_PROFILES[profile]
            self.profile_name = profile.value
            return self.aggregate(factor_scores, sector_result)
        finally:
            self.weights = old_weights
            self.profile_name = old_profile
    
    def compare_profiles(
        self,
        factor_scores: FactorScores,
        sector_result: Optional[SectorAnalysisResult] = None
    ) -> Dict[str, AggregatedScore]:
        """
        Compare scores across all profiles.
        
        Useful for understanding how different weight configurations
        affect the final score.
        
        Returns:
            Dict mapping profile name to AggregatedScore
        """
        results = {}
        
        for profile in ScoringProfile:
            aggregator = ScoreAggregator(profile=profile)
            results[profile.value] = aggregator.aggregate(factor_scores, sector_result)
        
        return results
    
    @staticmethod
    def explain_priority(rank: int) -> Dict[str, Any]:
        """
        Get explanation for a priority rank.
        
        Args:
            rank: Priority rank (1-5)
            
        Returns:
            Dict with processing guidance
        """
        explanations = {
            1: {
                "label": "critical",
                "processing_target": "< 1 minute",
                "notification": True,
                "fast_track": True,
                "description": "Requires immediate attention - potential crisis or major event"
            },
            2: {
                "label": "high",
                "processing_target": "< 5 minutes",
                "notification": True,
                "fast_track": True,
                "description": "Important event requiring quick processing"
            },
            3: {
                "label": "medium",
                "processing_target": "< 15 minutes",
                "notification": False,
                "fast_track": False,
                "description": "Significant but not urgent - standard priority queue"
            },
            4: {
                "label": "low",
                "processing_target": "< 1 hour",
                "notification": False,
                "fast_track": False,
                "description": "Minor impact - process when resources available"
            },
            5: {
                "label": "minimal",
                "processing_target": "best effort",
                "notification": False,
                "fast_track": False,
                "description": "Minimal business relevance - lowest priority"
            }
        }
        
        return explanations.get(rank, explanations[5])
