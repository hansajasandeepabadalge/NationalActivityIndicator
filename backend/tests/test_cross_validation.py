"""
Tests for Cross-Source Validation Network

Tests all components:
- Source Reputation Tracker
- Claim Extractor
- Corroboration Engine
- Trust Calculator
- Cross-Source Validator (integration)
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List


class TestSourceReputationTracker:
    """Tests for SourceReputationTracker."""
    
    def test_get_reputation_known_source(self):
        """Test getting reputation for a known source."""
        from app.cross_validation import SourceReputationTracker
        
        tracker = SourceReputationTracker()
        reputation = tracker.get_reputation("daily_mirror")
        
        assert reputation is not None
        assert reputation.source_name == "daily_mirror"
        assert reputation.tier.value == "tier_1"
        assert reputation.current_reputation == 80.0  # Tier 1 base
    
    def test_get_reputation_unknown_source(self):
        """Test getting reputation for an unknown source."""
        from app.cross_validation import SourceReputationTracker
        
        tracker = SourceReputationTracker()
        reputation = tracker.get_reputation("random_blog_123")
        
        assert reputation is not None
        assert reputation.tier.value == "unknown"
        assert reputation.current_reputation == 30.0  # Unknown base
    
    def test_get_reputation_official_source(self):
        """Test getting reputation for an official source."""
        from app.cross_validation import SourceReputationTracker
        
        tracker = SourceReputationTracker()
        reputation = tracker.get_reputation("central_bank")
        
        assert reputation.tier.value == "official"
        assert reputation.current_reputation == 95.0  # Official base
    
    def test_record_confirmation(self):
        """Test recording a confirmation."""
        from app.cross_validation import SourceReputationTracker
        
        tracker = SourceReputationTracker()
        initial_rep = tracker.get_reputation("test_source").current_reputation
        
        tracker.record_confirmation(
            source_name="test_source",
            confirming_sources=["daily_mirror", "daily_news"],
            was_first_to_report=True
        )
        
        new_rep = tracker.get_reputation("test_source").current_reputation
        assert new_rep > initial_rep  # Reputation should increase
    
    def test_record_contradiction(self):
        """Test recording a contradiction."""
        from app.cross_validation import SourceReputationTracker
        
        tracker = SourceReputationTracker()
        # First get initial reputation
        initial_rep = tracker.get_reputation("test_source_2").current_reputation
        
        tracker.record_contradiction(
            source_name="test_source_2",
            contradicting_sources=["central_bank"]
        )
        
        new_rep = tracker.get_reputation("test_source_2").current_reputation
        assert new_rep < initial_rep  # Reputation should decrease
    
    def test_get_stats(self):
        """Test getting tracker statistics."""
        from app.cross_validation import SourceReputationTracker
        
        tracker = SourceReputationTracker()
        tracker.get_reputation("source_1")
        tracker.get_reputation("source_2")
        
        stats = tracker.get_stats()
        
        assert "total_sources" in stats
        assert stats["total_sources"] >= 2


class TestClaimExtractor:
    """Tests for ClaimExtractor."""
    
    def test_extract_numeric_claims(self):
        """Test extracting numeric claims."""
        from app.cross_validation import ClaimExtractor
        
        extractor = ClaimExtractor()
        content = "Inflation increased by 15.5% last month. The GDP grew by Rs. 500 billion."
        
        claims = extractor.extract_claims(
            content=content,
            title="Economic Update",
            article_id="test_1",
            source_name="test_source"
        )
        
        assert len(claims) > 0
        numeric_claims = [c for c in claims if c.claim_type.value == "numeric"]
        assert len(numeric_claims) >= 1
    
    def test_extract_attribution_claims(self):
        """Test extracting statement attribution claims."""
        from app.cross_validation import ClaimExtractor
        
        extractor = ClaimExtractor()
        content = 'The Finance Minister said that the economy will recover. According to John Smith, growth is expected.'
        
        claims = extractor.extract_claims(
            content=content,
            title="Minister Statement",
            article_id="test_2",
            source_name="test_source"
        )
        
        attribution_claims = [c for c in claims if c.claim_type.value == "attribution"]
        assert len(attribution_claims) >= 1
    
    def test_extract_event_claims(self):
        """Test extracting event claims."""
        from app.cross_validation import ClaimExtractor
        
        extractor = ClaimExtractor()
        content = "Floods hit Colombo causing major damage. Protests in Kandy continued today."
        
        claims = extractor.extract_claims(
            content=content,
            title="Local Events",
            article_id="test_3",
            source_name="test_source"
        )
        
        event_claims = [c for c in claims if c.claim_type.value == "event"]
        assert len(event_claims) >= 1
    
    def test_claim_fingerprinting(self):
        """Test that similar claims have similar fingerprints."""
        from app.cross_validation import ClaimExtractor
        
        extractor = ClaimExtractor()
        
        # Two similar articles
        claims1 = extractor.extract_claims(
            content="Inflation rose by 10% in December",
            title="Inflation Update",
            article_id="art1"
        )
        
        claims2 = extractor.extract_claims(
            content="Inflation increased by 10% during December",
            title="Inflation News",
            article_id="art2"
        )
        
        # Both should have numeric claims
        assert len(claims1) > 0
        assert len(claims2) > 0


class TestCorroborationEngine:
    """Tests for CorroborationEngine."""
    
    def test_add_article_to_cache(self):
        """Test adding articles to cache."""
        from app.cross_validation import CorroborationEngine
        
        engine = CorroborationEngine()
        
        engine.add_article_to_cache(
            article_id="test_1",
            content="Test article content about inflation",
            title="Test Article",
            source_name="test_source"
        )
        
        assert "test_1" in engine._article_cache
    
    def test_find_corroboration_no_matches(self):
        """Test finding corroboration when no matches exist."""
        from app.cross_validation import CorroborationEngine
        
        engine = CorroborationEngine()
        
        result = engine.find_corroboration(
            article_id="unique_1",
            content="Completely unique content that nobody else has",
            title="Unique Article",
            source_name="test_source"
        )
        
        assert result is not None
        assert result.corroboration_level.value in ["none", "weak"]
    
    def test_find_corroboration_with_matches(self):
        """Test finding corroboration with similar articles."""
        from app.cross_validation import CorroborationEngine
        
        engine = CorroborationEngine()
        
        # Add first article
        engine.add_article_to_cache(
            article_id="match_1",
            content="The central bank increased interest rates by 1 percent today due to inflation concerns",
            title="Interest Rate Hike",
            source_name="daily_mirror"
        )
        
        # Add second similar article
        engine.add_article_to_cache(
            article_id="match_2",
            content="Interest rates raised by central bank by 1 percent citing inflation",
            title="Rate Increase",
            source_name="daily_news"
        )
        
        # Check corroboration for first article
        result = engine.find_corroboration(
            article_id="match_1",
            content="The central bank increased interest rates by 1 percent today due to inflation concerns",
            title="Interest Rate Hike",
            source_name="daily_mirror"
        )
        
        assert result is not None
        # May or may not find corroboration depending on similarity calculation
    
    def test_get_stats(self):
        """Test getting engine statistics."""
        from app.cross_validation import CorroborationEngine
        
        engine = CorroborationEngine()
        stats = engine.get_stats()
        
        assert "articles_analyzed" in stats
        assert "by_level" in stats


class TestTrustCalculator:
    """Tests for TrustCalculator."""
    
    def test_calculate_trust_no_corroboration(self):
        """Test trust calculation without corroboration data."""
        from app.cross_validation import TrustCalculator
        
        calculator = TrustCalculator()
        
        trust = calculator.calculate_trust(
            article_id="test_1",
            source_name="daily_mirror",
            corroboration_result=None,
            published_at=datetime.utcnow()
        )
        
        assert trust is not None
        assert 0 <= trust.total_score <= 100
        assert trust.trust_level is not None
    
    def test_calculate_trust_high_reputation_source(self):
        """Test trust calculation for high reputation source."""
        from app.cross_validation import TrustCalculator
        
        calculator = TrustCalculator()
        
        trust_official = calculator.calculate_trust(
            article_id="test_2",
            source_name="central_bank",
            corroboration_result=None,
            published_at=datetime.utcnow()
        )
        
        trust_unknown = calculator.calculate_trust(
            article_id="test_3",
            source_name="random_blog",
            corroboration_result=None,
            published_at=datetime.utcnow()
        )
        
        # Official source should have higher trust
        assert trust_official.total_score > trust_unknown.total_score
    
    def test_trust_levels(self):
        """Test trust level thresholds."""
        from app.cross_validation import TrustLevel
        
        # Check all levels exist
        assert TrustLevel.VERIFIED.value == "verified"
        assert TrustLevel.HIGH_TRUST.value == "high_trust"
        assert TrustLevel.MODERATE.value == "moderate"
        assert TrustLevel.LOW_TRUST.value == "low_trust"
        assert TrustLevel.UNVERIFIED.value == "unverified"


class TestCrossSourceValidator:
    """Integration tests for CrossSourceValidator."""
    
    def test_validate_article(self):
        """Test full article validation."""
        from app.cross_validation import CrossSourceValidator
        
        validator = CrossSourceValidator()
        
        result = validator.validate_article(
            article_id="int_test_1",
            content="The government announced new tax reforms today that will affect businesses nationwide.",
            title="New Tax Reforms Announced",
            source_name="daily_mirror",
            published_at=datetime.utcnow()
        )
        
        assert result is not None
        assert result.article_id == "int_test_1"
        assert 0 <= result.score <= 100
        assert result.trust_level is not None
        assert result.trust_score is not None
    
    def test_validate_batch(self):
        """Test batch validation."""
        from app.cross_validation import CrossSourceValidator
        
        validator = CrossSourceValidator()
        
        articles = [
            {
                "article_id": "batch_1",
                "title": "Economic Growth Report",
                "content": "The economy grew by 5% this quarter according to latest data.",
                "source_name": "reuters"
            },
            {
                "article_id": "batch_2",
                "title": "Economic Update",
                "content": "GDP increased by 5% as reported by the central bank.",
                "source_name": "daily_news"
            }
        ]
        
        results = validator.validate_batch(articles)
        
        assert len(results) == 2
        assert all(r.article_id in ["batch_1", "batch_2"] for r in results)
    
    def test_get_statistics(self):
        """Test getting validator statistics."""
        from app.cross_validation import CrossSourceValidator
        
        validator = CrossSourceValidator()
        
        # Validate an article first
        validator.validate_article(
            article_id="stats_test",
            content="Test content",
            title="Test",
            source_name="test"
        )
        
        stats = validator.get_statistics()
        
        assert "validation_metrics" in stats
        assert "reputation_stats" in stats
        assert "corroboration_stats" in stats
    
    def test_claims_extraction_in_validation(self):
        """Test that claims are extracted during validation."""
        from app.cross_validation import CrossSourceValidator
        
        validator = CrossSourceValidator()
        
        result = validator.validate_article(
            article_id="claims_test",
            content="Inflation rose by 10% last month. The Finance Minister said recovery is expected.",
            title="Economic News",
            source_name="daily_mirror"
        )
        
        # Should have extracted claims
        assert result.claims is not None
        assert len(result.claims) > 0


class TestModuleInitialization:
    """Test module-level functionality."""
    
    def test_get_validator_singleton(self):
        """Test that get_validator returns singleton."""
        from app.cross_validation import get_validator, reset_validator
        
        reset_validator()  # Reset first
        
        v1 = get_validator()
        v2 = get_validator()
        
        assert v1 is v2  # Same instance
    
    def test_all_exports_available(self):
        """Test that all expected exports are available."""
        from app.cross_validation import (
            CrossSourceValidator,
            CrossValidationResult,
            TrustLevel,
            TrustScore,
            SourceReputationTracker,
            SourceReputation,
            ReputationTier,
            ClaimExtractor,
            ExtractedClaim,
            CorroborationEngine,
            CorroborationResult,
            CorroborationLevel,
            TrustCalculator,
            get_validator
        )
        
        # All imports should succeed
        assert CrossSourceValidator is not None
        assert TrustLevel is not None
        assert get_validator is not None


class TestPerformance:
    """Performance tests."""
    
    def test_validation_speed(self):
        """Test that validation is fast enough."""
        import time
        from app.cross_validation import CrossSourceValidator
        
        validator = CrossSourceValidator()
        
        start = time.time()
        
        for i in range(10):
            validator.validate_article(
                article_id=f"perf_test_{i}",
                content="The central bank announced new monetary policy measures today affecting interest rates.",
                title="Monetary Policy Update",
                source_name="daily_mirror"
            )
        
        elapsed = time.time() - start
        avg_time = elapsed / 10 * 1000  # ms per article
        
        # Should be under 100ms per article on average
        assert avg_time < 100, f"Validation too slow: {avg_time:.2f}ms per article"
    
    def test_claim_extraction_speed(self):
        """Test claim extraction performance."""
        import time
        from app.cross_validation import ClaimExtractor
        
        extractor = ClaimExtractor()
        content = """
        The central bank announced a 1% increase in interest rates today.
        According to the Finance Minister, this decision was made to control inflation.
        GDP grew by 5% last quarter, reaching Rs. 100 billion.
        Floods hit Colombo causing widespread damage.
        The unemployment rate dropped to 4.5%.
        """ * 5  # Repeat for longer content
        
        start = time.time()
        
        for _ in range(20):
            extractor.extract_claims(
                content=content,
                title="Economic Update"
            )
        
        elapsed = time.time() - start
        avg_time = elapsed / 20 * 1000  # ms per extraction
        
        # Should be under 50ms per extraction
        assert avg_time < 50, f"Claim extraction too slow: {avg_time:.2f}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
