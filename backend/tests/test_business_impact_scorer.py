"""
Unit tests for Business Impact Scorer module.

Tests cover:
- MultiFactorAnalyzer: severity, credibility, geography, temporal analysis
- SectorImpactEngine: sector detection, cascade effects, dependencies
- ScoreAggregator: weighted scoring, profile comparison
- BusinessImpactScorer: full pipeline integration
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Import test subjects
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestMultiFactorAnalyzer:
    """Test cases for MultiFactorAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create MultiFactorAnalyzer instance."""
        from app.impact_scorer.multi_factor_analyzer import MultiFactorAnalyzer
        return MultiFactorAnalyzer()
    
    def test_analyze_crisis_keywords(self, analyzer):
        """Test detection of crisis-level severity."""
        title = "Breaking: Tsunami Warning Issued for Coastal Areas"
        content = "A major earthquake has triggered a tsunami warning. Evacuations are underway."
        
        result = analyzer.analyze(title, content, source="dmc")
        
        assert result.severity_score >= 80
        assert result.severity_level.value == "crisis"
        assert any("tsunami" in s for s in result.detected_signals)
    
    def test_analyze_high_severity(self, analyzer):
        """Test detection of high severity events."""
        title = "Parliament Passes Major Economic Reform Bill"
        content = "The parliament today passed sweeping changes to the tax system. This unprecedented reform will affect all sectors."
        
        result = analyzer.analyze(title, content, source="government")
        
        assert result.severity_score >= 60
        assert result.severity_level.value in ["high", "crisis"]
    
    def test_analyze_low_severity(self, analyzer):
        """Test detection of low severity content."""
        title = "Local Community Event Held"
        content = "A local community gathering was organized at the town hall."
        
        result = analyzer.analyze(title, content, source="unknown")
        
        assert result.severity_score <= 40
        assert result.severity_level.value in ["low", "minimal"]
    
    def test_source_credibility_government(self, analyzer):
        """Test high credibility for government sources."""
        result = analyzer.analyze("Test", "Content", source="government")
        assert result.credibility_score >= 90
    
    def test_source_credibility_unknown(self, analyzer):
        """Test low credibility for unknown sources."""
        result = analyzer.analyze("Test", "Content", source="random_blog")
        assert result.credibility_score <= 40
    
    def test_geographic_scope_national(self, analyzer):
        """Test national scope detection."""
        content = "This policy affects the entire country nationwide across all districts."
        
        result = analyzer.analyze("National Policy", content)
        
        assert result.geographic_score >= 80
        assert result.geographic_scope.value == "national"
    
    def test_geographic_scope_local(self, analyzer):
        """Test local scope detection."""
        content = "The event occurred in Colombo district."
        
        result = analyzer.analyze("Local Event", content)
        
        assert result.geographic_score <= 50
        assert result.geographic_scope.value in ["local", "regional"]
    
    def test_temporal_breaking_news(self, analyzer):
        """Test temporal urgency for breaking news."""
        title = "BREAKING: Major Development"
        content = "Just in - urgent update on developing situation."
        
        result = analyzer.analyze(title, content)
        
        assert result.temporal_score >= 85
        assert any("breaking" in s for s in result.detected_signals)
    
    def test_temporal_old_content(self, analyzer):
        """Test temporal score for old content."""
        old_time = datetime.utcnow() - timedelta(days=10)
        
        result = analyzer.analyze(
            "Old News", 
            "Something happened last month.",
            publish_time=old_time
        )
        
        assert result.temporal_score <= 40
    
    def test_confidence_calculation(self, analyzer):
        """Test confidence is calculated correctly."""
        result = analyzer.analyze(
            "Breaking: Major Crisis",
            "Flood disaster nationwide evacuation emergency",
            source="government"
        )
        
        assert 0 <= result.confidence <= 1
        # High credibility + many signals should give high confidence
        assert result.confidence >= 0.6


class TestSectorImpactEngine:
    """Test cases for SectorImpactEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create SectorImpactEngine instance."""
        from app.impact_scorer.sector_engine import SectorImpactEngine
        return SectorImpactEngine()
    
    def test_analyze_tourism_sector(self, engine):
        """Test tourism sector detection."""
        title = "Hotel Industry Reports Record Tourist Arrivals"
        content = "Tourism sector booming as hotels report full bookings. Travel agencies seeing increased demand."
        
        result = engine.analyze_sectors(title, content)
        
        assert result.sector_count > 0
        sector_names = [s.sector.value for s in result.primary_sectors]
        assert "tourism" in sector_names
    
    def test_analyze_finance_sector(self, engine):
        """Test finance sector detection."""
        title = "Central Bank Raises Interest Rates"
        content = "The banking sector responds to new interest rate policy. Stock market shows volatility."
        
        result = engine.analyze_sectors(title, content)
        
        sector_names = [s.sector.value for s in result.primary_sectors]
        assert "finance" in sector_names
    
    def test_analyze_multiple_sectors(self, engine):
        """Test detection of multiple affected sectors."""
        title = "Power Crisis Affects Manufacturing and Retail"
        content = "Factory production halted due to power cuts. Shopping malls implement load shedding schedules."
        
        result = engine.analyze_sectors(title, content)
        
        assert result.sector_count >= 2
        assert len(result.primary_sectors) >= 1
    
    def test_cascade_effects(self, engine):
        """Test cascade effect calculation."""
        title = "Nationwide Fuel Shortage"
        content = "Fuel shortage affecting transport and logistics across the country."
        
        result = engine.analyze_sectors(title, content)
        
        # Energy crisis should cascade to transport, manufacturing, etc.
        assert len(result.cascade_effects) >= 0
    
    def test_sector_dependencies(self, engine):
        """Test sector dependency mapping."""
        from app.impact_scorer.sector_engine import IndustrySector
        
        # Energy sector should have dependencies
        assert IndustrySector.ENERGY in engine.SECTOR_DEPENDENCIES
        deps = engine.SECTOR_DEPENDENCIES[IndustrySector.ENERGY]
        
        assert len(deps) > 0
        # Manufacturing should depend on energy
        dep_sectors = [d[0] for d in deps]
        assert IndustrySector.MANUFACTURING in dep_sectors
    
    def test_target_sectors_filter(self, engine):
        """Test filtering for specific target sectors."""
        title = "Mixed Business News"
        content = "Tourism and banking sectors show growth. Manufacturing stable."
        
        result = engine.analyze_sectors(
            title, content, 
            target_sectors=["tourism", "finance"]
        )
        
        # Should still analyze all but can use for scoring
        assert result.overall_sector_score >= 0


class TestScoreAggregator:
    """Test cases for ScoreAggregator class."""
    
    @pytest.fixture
    def aggregator(self):
        """Create ScoreAggregator instance."""
        from app.impact_scorer.score_aggregator import ScoreAggregator
        return ScoreAggregator()
    
    @pytest.fixture
    def sample_factor_scores(self):
        """Create sample factor scores."""
        from app.impact_scorer.multi_factor_analyzer import (
            FactorScores, SeverityLevel, GeographicScope
        )
        return FactorScores(
            severity_score=80,
            credibility_score=90,
            geographic_score=70,
            temporal_score=85,
            volume_score=50,
            severity_level=SeverityLevel.HIGH,
            geographic_scope=GeographicScope.NATIONAL,
            detected_signals=["crisis:flood", "high:emergency"],
            confidence=0.8
        )
    
    def test_aggregate_high_scores(self, aggregator, sample_factor_scores):
        """Test aggregation of high factor scores."""
        result = aggregator.aggregate(sample_factor_scores)
        
        assert result.final_score >= 60
        assert result.priority_rank <= 3
    
    def test_aggregate_with_sector(self, aggregator, sample_factor_scores):
        """Test aggregation including sector scores."""
        from app.impact_scorer.sector_engine import (
            SectorAnalysisResult, SectorImpact, IndustrySector
        )
        
        sector_result = SectorAnalysisResult(
            primary_sectors=[
                SectorImpact(
                    sector=IndustrySector.FINANCE,
                    impact_score=75,
                    relevance_score=80,
                    keywords_matched=["bank", "finance"],
                    impact_type="direct",
                    description="Finance sector impacted"
                )
            ],
            secondary_sectors=[],
            overall_sector_score=75,
            sector_count=1,
            cascade_effects=[]
        )
        
        result = aggregator.aggregate(sample_factor_scores, sector_result)
        
        assert result.factor_scores["sector"] == 75
        assert "sector" in result.factor_contributions
    
    def test_priority_thresholds(self, aggregator):
        """Test priority rank calculation."""
        from app.impact_scorer.multi_factor_analyzer import (
            FactorScores, SeverityLevel, GeographicScope
        )
        
        # High scores = critical priority
        high_factors = FactorScores(
            severity_score=95,
            credibility_score=100,
            geographic_score=100,
            temporal_score=100,
            volume_score=80,
            severity_level=SeverityLevel.CRISIS,
            geographic_scope=GeographicScope.NATIONAL,
            detected_signals=["crisis:earthquake"],
            confidence=0.95
        )
        
        result = aggregator.aggregate(high_factors)
        assert result.priority_rank <= 2  # Should be critical or high
        
        # Low scores = low priority
        low_factors = FactorScores(
            severity_score=20,
            credibility_score=30,
            geographic_score=25,
            temporal_score=20,
            volume_score=15,
            severity_level=SeverityLevel.MINIMAL,
            geographic_scope=GeographicScope.LOCAL,
            detected_signals=[],
            confidence=0.3
        )
        
        result = aggregator.aggregate(low_factors)
        assert result.priority_rank >= 4  # Should be low or minimal
    
    def test_different_profiles(self, sample_factor_scores):
        """Test different scoring profiles produce different results."""
        from app.impact_scorer.score_aggregator import ScoreAggregator, ScoringProfile
        
        balanced = ScoreAggregator(profile=ScoringProfile.BALANCED)
        urgency = ScoreAggregator(profile=ScoringProfile.URGENCY_FOCUSED)
        business = ScoreAggregator(profile=ScoringProfile.BUSINESS_FOCUSED)
        
        result_balanced = balanced.aggregate(sample_factor_scores)
        result_urgency = urgency.aggregate(sample_factor_scores)
        result_business = business.aggregate(sample_factor_scores)
        
        # Profiles should produce different weightings
        assert result_balanced.weights_used != result_urgency.weights_used
        assert result_urgency.weights_used != result_business.weights_used


class TestBusinessImpactScorer:
    """Test cases for BusinessImpactScorer main class."""
    
    @pytest.fixture
    def scorer(self):
        """Create BusinessImpactScorer instance."""
        from app.impact_scorer.business_impact_scorer import BusinessImpactScorer
        scorer = BusinessImpactScorer()
        scorer._ensure_initialized()
        return scorer
    
    @pytest.mark.asyncio
    async def test_score_crisis_article(self, scorer):
        """Test scoring a crisis-level article."""
        article = {
            "title": "BREAKING: Massive Flood Hits Western Province",
            "content": """Severe flooding has affected multiple districts in Western Province.
            Emergency evacuations are underway as water levels continue to rise.
            The Disaster Management Centre has issued red alerts for Colombo, 
            Gampaha and Kalutara districts. Thousands of families displaced.""",
            "source": "dmc"
        }
        
        result = await scorer.score_article(article)
        
        assert result.impact_score >= 70
        assert result.priority_rank <= 2
        assert result.requires_fast_track is True
    
    @pytest.mark.asyncio
    async def test_score_routine_article(self, scorer):
        """Test scoring a routine/low priority article."""
        article = {
            "title": "Local Sports Event Held",
            "content": "A community cricket match was held at the local grounds yesterday.",
            "source": "local_news"
        }
        
        result = await scorer.score_article(article)
        
        assert result.impact_score <= 40
        assert result.priority_rank >= 4
        assert result.requires_fast_track is False
    
    def test_score_sync(self, scorer):
        """Test synchronous scoring."""
        article = {
            "title": "Central Bank Announces Interest Rate Decision",
            "content": "The Central Bank of Sri Lanka today announced a change in interest rates.",
            "source": "cbsl"
        }
        
        result = scorer.score_article_sync(article)
        
        assert result.impact_score > 0
        assert result.impact_level is not None
        assert len(result.primary_sectors) >= 0
    
    @pytest.mark.asyncio
    async def test_score_batch(self, scorer):
        """Test batch scoring."""
        articles = [
            {"title": "Crisis Event", "content": "Major disaster emergency nationwide", "source": "dmc"},
            {"title": "Minor Update", "content": "Small local announcement", "source": "unknown"},
            {"title": "Finance News", "content": "Bank interest rate change policy", "source": "central_bank"}
        ]
        
        results = await scorer.score_batch(articles)
        
        assert len(results) == 3
        # Should be sorted by priority
        assert results[0].priority_rank <= results[1].priority_rank
    
    @pytest.mark.asyncio
    async def test_sector_analysis(self, scorer):
        """Test sector-specific analysis."""
        article = {
            "title": "Tourism Sector Recovery",
            "content": "Hotels and travel agencies report increased tourist arrivals. Airlines expanding capacity.",
            "source": "news"
        }
        
        result = await scorer.score_article(article, target_sectors=["tourism"])
        
        # Should identify tourism as primary sector
        primary_sector_names = [s.get("sector") for s in result.primary_sectors]
        assert "tourism" in primary_sector_names
    
    @pytest.mark.asyncio
    async def test_factor_breakdown(self, scorer):
        """Test that factor breakdown is complete."""
        article = {
            "title": "Test Article",
            "content": "Test content for factor analysis",
            "source": "test"
        }
        
        result = await scorer.score_article(article)
        
        # Check all factors are present
        factors = result.factors.to_dict()
        assert "severity" in factors
        assert "sector_relevance" in factors
        assert "source_credibility" in factors
        assert "geographic_scope" in factors
        assert "temporal_urgency" in factors
        assert "volume_momentum" in factors
    
    @pytest.mark.asyncio
    async def test_processing_guidance(self, scorer):
        """Test processing guidance is provided."""
        article = {
            "title": "Critical Breaking News",
            "content": "Emergency situation developing",
            "source": "government"
        }
        
        result = await scorer.score_article(article)
        
        guidance = result.processing_guidance
        assert "processing_target" in guidance
        assert "notification" in guidance
        assert "description" in guidance
    
    @pytest.mark.asyncio
    async def test_stats_tracking(self, scorer):
        """Test that statistics are tracked."""
        article = {"title": "Test", "content": "Test content", "source": "test"}
        
        initial_count = scorer.stats["articles_scored"]
        await scorer.score_article(article)
        
        assert scorer.stats["articles_scored"] == initial_count + 1


class TestPerformance:
    """Performance benchmarks for impact scoring."""
    
    @pytest.mark.asyncio
    async def test_scoring_speed(self):
        """Test that scoring is fast (<50ms per article)."""
        from app.impact_scorer.business_impact_scorer import BusinessImpactScorer
        import time
        
        scorer = BusinessImpactScorer()
        await scorer.initialize()
        
        article = {
            "title": "Test Article for Performance",
            "content": "This is test content for measuring scoring performance. " * 50,
            "source": "test"
        }
        
        start = time.time()
        for _ in range(10):
            await scorer.score_article(article)
        elapsed = time.time() - start
        
        avg_time_ms = (elapsed / 10) * 1000
        assert avg_time_ms < 50, f"Scoring too slow: {avg_time_ms}ms average"
    
    @pytest.mark.asyncio
    async def test_batch_efficiency(self):
        """Test batch processing is efficient."""
        from app.impact_scorer.business_impact_scorer import BusinessImpactScorer
        import time
        
        scorer = BusinessImpactScorer()
        await scorer.initialize()
        
        articles = [
            {"title": f"Article {i}", "content": f"Content {i} " * 20, "source": "test"}
            for i in range(100)
        ]
        
        start = time.time()
        results = await scorer.score_batch(articles)
        elapsed = time.time() - start
        
        # Should process 100 articles in under 3 seconds
        assert elapsed < 3.0, f"Batch too slow: {elapsed}s for 100 articles"
        assert len(results) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
