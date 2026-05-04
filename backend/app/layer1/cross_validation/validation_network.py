"""
Cross-Source Validation Network

Main orchestrator that coordinates all cross-source validation components:
- Source Reputation Tracking
- Claim Extraction
- Corroboration Engine
- Trust Calculation

Provides unified interface for validating articles across multiple sources.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import time

from .source_reputation import (
    SourceReputationTracker,
    SourceReputation,
    ReputationTier
)
from .claim_extractor import ClaimExtractor, ExtractedClaim, ClaimType
from .corroboration_engine import (
    CorroborationEngine,
    CorroborationResult,
    CorroborationLevel
)
from .trust_calculator import TrustCalculator, TrustScore, TrustLevel

logger = logging.getLogger(__name__)


@dataclass
class ValidationMetrics:
    """Metrics for validation operations."""
    articles_validated: int = 0
    claims_extracted: int = 0
    corroborations_found: int = 0
    conflicts_detected: int = 0
    avg_trust_score: float = 0.0
    avg_processing_time_ms: float = 0.0
    by_trust_level: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "articles_validated": self.articles_validated,
            "claims_extracted": self.claims_extracted,
            "corroborations_found": self.corroborations_found,
            "conflicts_detected": self.conflicts_detected,
            "avg_trust_score": round(self.avg_trust_score, 1),
            "avg_processing_time_ms": round(self.avg_processing_time_ms, 2),
            "by_trust_level": self.by_trust_level
        }


@dataclass
class CrossValidationResult:
    """Complete result of cross-source validation."""
    article_id: str
    source_name: str
    
    # Trust score (final output)
    trust_score: TrustScore
    
    # Extracted claims
    claims: List[ExtractedClaim] = field(default_factory=list)
    
    # Corroboration analysis
    corroboration: Optional[CorroborationResult] = None
    
    # Source reputation
    source_reputation: Optional[SourceReputation] = None
    
    # Processing info
    processing_time_ms: float = 0.0
    validated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def trust_level(self) -> TrustLevel:
        return self.trust_score.trust_level
    
    @property
    def score(self) -> float:
        return self.trust_score.total_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "article_id": self.article_id,
            "source": self.source_name,
            "trust_score": self.trust_score.to_dict(),
            "trust_level": self.trust_level.value,
            "score": round(self.score, 1),
            "claims_count": len(self.claims),
            "claims": [c.to_dict() for c in self.claims[:5]],  # Top 5 claims
            "corroboration": self.corroboration.to_dict() if self.corroboration else None,
            "source_reputation": self.source_reputation.to_dict() if self.source_reputation else None,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "validated_at": self.validated_at.isoformat()
        }


class CrossSourceValidator:
    """
    Cross-Source Validation Network.
    
    Orchestrates the complete validation pipeline:
    1. Extract claims from article
    2. Find corroborating articles
    3. Match claims across sources
    4. Calculate trust score
    5. Update source reputation
    
    Features:
    - Multi-source corroboration
    - Dynamic source reputation
    - Claim-level verification
    - Conflict detection
    - Trust scoring with detailed breakdown
    """
    
    def __init__(
        self,
        reputation_tracker: Optional[SourceReputationTracker] = None,
        claim_extractor: Optional[ClaimExtractor] = None,
        corroboration_engine: Optional[CorroborationEngine] = None,
        trust_calculator: Optional[TrustCalculator] = None,
        deduplicator=None
    ):
        """
        Initialize the cross-source validator.
        
        Args:
            reputation_tracker: Source reputation tracker
            claim_extractor: Claim extractor
            corroboration_engine: Corroboration engine
            trust_calculator: Trust calculator
            deduplicator: SemanticDeduplicator for similarity search
        """
        # Initialize components
        self._reputation_tracker = reputation_tracker or SourceReputationTracker()
        self._claim_extractor = claim_extractor or ClaimExtractor()
        self._corroboration_engine = corroboration_engine or CorroborationEngine(
            deduplicator=deduplicator,
            reputation_tracker=self._reputation_tracker
        )
        self._trust_calculator = trust_calculator or TrustCalculator(
            reputation_tracker=self._reputation_tracker
        )
        
        # Wire up components
        self._corroboration_engine.set_reputation_tracker(self._reputation_tracker)
        self._trust_calculator.set_reputation_tracker(self._reputation_tracker)
        
        # Set deduplicator if provided
        if deduplicator:
            self._corroboration_engine.set_deduplicator(deduplicator)
        
        # Validation cache
        self._validation_cache: Dict[str, CrossValidationResult] = {}
        
        # Metrics tracking
        self._metrics = ValidationMetrics()
        self._processing_times: List[float] = []
        
        logger.info("CrossSourceValidator initialized")
    
    def set_deduplicator(self, deduplicator):
        """Set semantic deduplicator for similarity search."""
        self._corroboration_engine.set_deduplicator(deduplicator)
    
    def validate_article(
        self,
        article_id: str,
        content: str,
        title: str,
        source_name: str,
        published_at: Optional[datetime] = None,
        use_cache: bool = True
    ) -> CrossValidationResult:
        """
        Validate an article using cross-source validation.
        
        Args:
            article_id: Article identifier
            content: Article content/body
            title: Article title
            source_name: Source name
            published_at: Publication time
            use_cache: Whether to use cached results
            
        Returns:
            CrossValidationResult with trust score and details
        """
        start_time = time.time()
        pub_time = published_at or datetime.utcnow()
        
        # Check cache
        if use_cache and article_id in self._validation_cache:
            cached = self._validation_cache[article_id]
            cache_age = (datetime.utcnow() - cached.validated_at).total_seconds()
            if cache_age < 3600:  # 1 hour cache
                return cached
        
        try:
            # Step 1: Record article for source
            self._reputation_tracker.record_article(source_name)
            
            # Step 2: Extract claims
            claims = self._claim_extractor.extract_claims(
                content=content,
                title=title,
                article_id=article_id,
                source_name=source_name
            )
            
            # Step 3: Add to corroboration cache
            self._corroboration_engine.add_article_to_cache(
                article_id=article_id,
                content=content,
                title=title,
                source_name=source_name,
                published_at=pub_time,
                claims=[c.to_dict() for c in claims]
            )
            
            # Step 4: Find corroboration
            corroboration = self._corroboration_engine.find_corroboration(
                article_id=article_id,
                content=content,
                title=title,
                source_name=source_name,
                published_at=pub_time,
                claims=[c.to_dict() for c in claims]
            )
            
            # Step 5: Calculate trust score
            trust_score = self._trust_calculator.calculate_trust(
                article_id=article_id,
                source_name=source_name,
                corroboration_result=corroboration,
                published_at=pub_time
            )
            
            # Step 6: Update source reputation based on results
            self._update_reputation(source_name, corroboration)
            
            # Get source reputation
            reputation = self._reputation_tracker.get_reputation(source_name)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create result
            result = CrossValidationResult(
                article_id=article_id,
                source_name=source_name,
                trust_score=trust_score,
                claims=claims,
                corroboration=corroboration,
                source_reputation=reputation,
                processing_time_ms=processing_time
            )
            
            # Update cache
            self._validation_cache[article_id] = result
            
            # Update metrics
            self._update_metrics(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Validation error for article {article_id}: {e}")
            
            # Return minimal result on error
            processing_time = (time.time() - start_time) * 1000
            
            # Create fallback trust score
            reputation = self._reputation_tracker.get_reputation(source_name)
            fallback_trust = TrustScore(
                article_id=article_id,
                source_name=source_name,
                total_score=reputation.current_reputation * 0.3,  # Base on reputation only
                trust_level=TrustLevel.UNVERIFIED,
                source_reputation_score=self._trust_calculator._calculate_reputation_score(source_name),
                corroboration_score=self._trust_calculator._calculate_corroboration_score(None),
                source_diversity_score=self._trust_calculator._calculate_diversity_score(None),
                recency_score=self._trust_calculator._calculate_recency_score(None, pub_time),
                confidence=0.3
            )
            
            return CrossValidationResult(
                article_id=article_id,
                source_name=source_name,
                trust_score=fallback_trust,
                claims=[],
                corroboration=None,
                source_reputation=reputation,
                processing_time_ms=processing_time
            )
    
    def validate_batch(
        self,
        articles: List[Dict[str, Any]],
        use_cache: bool = True
    ) -> List[CrossValidationResult]:
        """
        Validate multiple articles.
        
        Args:
            articles: List of article dictionaries
            use_cache: Whether to use cached results
            
        Returns:
            List of CrossValidationResult objects
        """
        results = []
        
        # First pass: add all articles to corroboration cache
        for article in articles:
            article_id = article.get("article_id", article.get("id", ""))
            content = article.get("content", article.get("body", ""))
            title = article.get("title", "")
            source_name = article.get("source_name", article.get("source", ""))
            published_at = article.get("published_at")
            
            # Extract claims
            claims = self._claim_extractor.extract_claims(
                content=content,
                title=title,
                article_id=article_id,
                source_name=source_name
            )
            
            # Add to cache
            self._corroboration_engine.add_article_to_cache(
                article_id=article_id,
                content=content,
                title=title,
                source_name=source_name,
                published_at=published_at,
                claims=[c.to_dict() for c in claims]
            )
        
        # Second pass: validate each article
        for article in articles:
            article_id = article.get("article_id", article.get("id", ""))
            content = article.get("content", article.get("body", ""))
            title = article.get("title", "")
            source_name = article.get("source_name", article.get("source", ""))
            published_at = article.get("published_at")
            
            result = self.validate_article(
                article_id=article_id,
                content=content,
                title=title,
                source_name=source_name,
                published_at=published_at,
                use_cache=use_cache
            )
            
            results.append(result)
        
        return results
    
    def get_source_reputation(self, source_name: str) -> SourceReputation:
        """Get reputation for a source."""
        return self._reputation_tracker.get_reputation(source_name)
    
    def get_source_tier(self, source_name: str) -> ReputationTier:
        """Get tier for a source."""
        return self._reputation_tracker.get_source_tier(source_name)
    
    def get_trust_summary(
        self,
        results: Optional[List[CrossValidationResult]] = None
    ) -> Dict[str, Any]:
        """Get trust summary for validation results."""
        if results is None:
            results = list(self._validation_cache.values())
        
        if not results:
            return {
                "total_validated": 0,
                "avg_trust_score": 0,
                "by_level": {}
            }
        
        trust_scores = [r.trust_score for r in results]
        return self._trust_calculator.get_trust_summary(trust_scores)
    
    def get_metrics(self) -> ValidationMetrics:
        """Get validation metrics."""
        return self._metrics
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            "validation_metrics": self._metrics.to_dict(),
            "reputation_stats": self._reputation_tracker.get_stats(),
            "corroboration_stats": self._corroboration_engine.get_stats(),
            "cache_size": len(self._validation_cache),
            "top_sources": [
                r.to_dict() for r in self._reputation_tracker.get_top_sources(5)
            ]
        }
    
    def clear_cache(self):
        """Clear validation cache."""
        self._validation_cache.clear()
    
    def _update_reputation(
        self,
        source_name: str,
        corroboration: Optional[CorroborationResult]
    ):
        """Update source reputation based on corroboration results."""
        if not corroboration:
            return
        
        # If article was corroborated
        if corroboration.corroborating_articles:
            confirming_sources = [
                a.source_name for a in corroboration.corroborating_articles
            ]
            self._reputation_tracker.record_confirmation(
                source_name=source_name,
                confirming_sources=confirming_sources,
                was_first_to_report=corroboration.is_first_to_report
            )
        
        # If article has conflicts
        if corroboration.conflicting_articles:
            contradicting_sources = [
                a.source_name for a in corroboration.conflicting_articles
            ]
            self._reputation_tracker.record_contradiction(
                source_name=source_name,
                contradicting_sources=contradicting_sources
            )
    
    def _update_metrics(self, result: CrossValidationResult):
        """Update validation metrics."""
        self._metrics.articles_validated += 1
        self._metrics.claims_extracted += len(result.claims)
        
        if result.corroboration:
            self._metrics.corroborations_found += len(
                result.corroboration.corroborating_articles
            )
            self._metrics.conflicts_detected += len(
                result.corroboration.conflicting_articles
            )
        
        # Update processing time average
        self._processing_times.append(result.processing_time_ms)
        if len(self._processing_times) > 1000:
            self._processing_times = self._processing_times[-1000:]
        self._metrics.avg_processing_time_ms = sum(self._processing_times) / len(self._processing_times)
        
        # Update trust level counts
        level = result.trust_level.value
        self._metrics.by_trust_level[level] = self._metrics.by_trust_level.get(level, 0) + 1
        
        # Update average trust score
        cached_results = list(self._validation_cache.values())
        if cached_results:
            self._metrics.avg_trust_score = sum(
                r.score for r in cached_results
            ) / len(cached_results)


# Global singleton instance
_validator_instance: Optional[CrossSourceValidator] = None


def get_validator() -> CrossSourceValidator:
    """Get or create the global cross-source validator instance."""
    global _validator_instance
    
    if _validator_instance is None:
        _validator_instance = CrossSourceValidator()
    
    return _validator_instance


def reset_validator():
    """Reset the global validator instance."""
    global _validator_instance
    _validator_instance = None
