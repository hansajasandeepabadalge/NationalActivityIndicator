"""
Business Impact Scorer System

This module provides intelligent multi-factor scoring for article prioritization:

1. Multi-Factor Analysis - Extracts severity, scope, credibility signals
2. Sector Impact Engine - Calculates industry-specific relevance
3. Temporal Weighting - Time-decay and urgency factors
4. Score Aggregation - Weighted combination into final impact score

Impact Score Formula:
    Final_Score = Σ(factor_weight × factor_score) × confidence_multiplier

Scoring Factors:
- Severity (25%): Event magnitude (crisis → minor)
- Sector Relevance (25%): Match to target industries
- Source Credibility (15%): Government → Unverified scale
- Geographic Scope (10%): National → Local coverage
- Temporal Urgency (15%): Breaking → Historical timeline
- Volume/Momentum (10%): Mention frequency and trends
"""

from app.impact_scorer.business_impact_scorer import (
    BusinessImpactScorer,
    ImpactResult,
    ImpactLevel,
    ScoringFactors
)
from app.impact_scorer.multi_factor_analyzer import MultiFactorAnalyzer
from app.impact_scorer.sector_engine import SectorImpactEngine
from app.impact_scorer.score_aggregator import ScoreAggregator
from typing import Optional

# Global scorer instance
_scorer: Optional[BusinessImpactScorer] = None


async def get_impact_scorer() -> BusinessImpactScorer:
    """
    Get global business impact scorer instance (async).
    
    Returns:
        BusinessImpactScorer instance ready for use
    """
    global _scorer
    if _scorer is None:
        _scorer = BusinessImpactScorer()
        await _scorer.initialize()
    return _scorer


def get_impact_scorer_sync() -> BusinessImpactScorer:
    """
    Get global business impact scorer instance (sync version).
    
    Returns:
        BusinessImpactScorer instance
    """
    global _scorer
    if _scorer is None:
        _scorer = BusinessImpactScorer()
    return _scorer


__all__ = [
    "BusinessImpactScorer",
    "ImpactResult",
    "ImpactLevel",
    "ScoringFactors",
    "MultiFactorAnalyzer",
    "SectorImpactEngine",
    "ScoreAggregator",
    "get_impact_scorer",
    "get_impact_scorer_sync"
]
