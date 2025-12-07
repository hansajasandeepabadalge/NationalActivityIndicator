"""
Cross-Source Validation Network

This module provides intelligent cross-source validation for trust and credibility:

1. Source Reputation Tracking - Dynamic reputation based on historical accuracy
2. Claim Extraction - Extract and normalize verifiable claims from content
3. Corroboration Engine - Find articles that confirm or contradict claims
4. Trust Score Calculator - Weighted trust score based on multiple factors

Trust Score Formula:
    Trust_Score = (source_reputation × 0.30) + 
                  (corroboration_score × 0.35) + 
                  (source_diversity × 0.20) + 
                  (recency_match × 0.15)

Trust Levels:
- VERIFIED (85-100): Multiple credible sources confirm
- HIGH_TRUST (70-84): At least 2 sources confirm
- MODERATE (50-69): Single credible source
- LOW_TRUST (30-49): Unverified or conflicting reports
- UNVERIFIED (0-29): No corroboration, low credibility source
"""

from .source_reputation import (
    SourceReputationTracker,
    SourceReputation,
    ReputationTier,
    SourceCategory
)
from .claim_extractor import (
    ClaimExtractor,
    ExtractedClaim,
    ExtractedEntity,
    ClaimType,
    EntityType
)
from .corroboration_engine import (
    CorroborationEngine,
    CorroborationResult,
    CorroboratingArticle,
    ConflictingArticle,
    CorroborationLevel
)
from .trust_calculator import (
    TrustCalculator,
    TrustScore,
    TrustFactorScore,
    TrustLevel
)
from .validation_network import (
    CrossSourceValidator,
    CrossValidationResult,
    ValidationMetrics,
    get_validator,
    reset_validator
)
from typing import Optional

# Backward compatibility alias
ValidationResult = CrossValidationResult
CorroborationStatus = CorroborationLevel
CorroborationType = CorroborationLevel
TrustFactors = TrustFactorScore


def get_validator_sync() -> CrossSourceValidator:
    """
    Get global cross-source validator instance (sync version).
    
    Returns:
        CrossSourceValidator instance
    """
    return get_validator()


__all__ = [
    # Main Validator
    "CrossSourceValidator",
    "CrossValidationResult",
    "ValidationResult",  # Alias
    "ValidationMetrics",
    "get_validator",
    "get_validator_sync",
    "reset_validator",
    
    # Trust
    "TrustLevel",
    "TrustScore",
    "TrustFactorScore",
    "TrustFactors",  # Alias
    "TrustCalculator",
    
    # Source Reputation
    "SourceReputationTracker",
    "SourceReputation",
    "ReputationTier",
    "SourceCategory",
    
    # Claims
    "ClaimExtractor",
    "ExtractedClaim",
    "ExtractedEntity",
    "ClaimType",
    "EntityType",
    
    # Corroboration
    "CorroborationEngine",
    "CorroborationResult",
    "CorroboratingArticle",
    "ConflictingArticle",
    "CorroborationLevel",
    "CorroborationStatus",  # Alias
    "CorroborationType",  # Alias
]
