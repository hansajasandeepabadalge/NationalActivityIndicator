"""
Tests for Layer 4 Contextual Intelligence Module

Comprehensive tests for:
- Industry benchmarking and context
- Historical event matching
- Cross-industry dependency analysis
- Cascading impact modeling
- Competitive intelligence
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any

from app.layer4.context import (
    # Industry Context
    IndustryContextProvider,
    IndustryBenchmark,
    
    # Historical Context
    HistoricalContextAnalyzer,
    HistoricalEvent,
    HistoricalMatch,
    TrendContext,
    
    # Cross-Industry
    CrossIndustryAnalyzer,
    CrossIndustryInsight,
    IndustryRelationship,
    ImpactDirection,
    ImpactStrength,
    
    # Cascading Impacts
    CascadingImpactAnalyzer,
    CascadeChain,
    CascadeNode,
    PropagationModel,
    ImpactPhase,
    
    # Competitive Intelligence
    CompetitiveIntelligenceAnalyzer,
    CompetitorProfile,
    CompetitorMove,
    MarketPositionAnalysis,
    CompetitorMoveType,
    ThreatLevel,
    OpportunityLevel,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_company_indicators() -> Dict[str, float]:
    """Sample operational indicators for a company."""
    return {
        "OPS_SUPPLY_CHAIN": 0.35,  # Low - concerning
        "OPS_POWER_RELIABILITY": 0.40,  # Low - concerning
        "OPS_TRANSPORT_AVAIL": 0.30,  # Very low - critical
        "OPS_LABOR_AVAIL": 0.65,
        "OPS_DEMAND_LEVEL": 0.70,
        "OPS_PRODUCTION_CAP": 0.55,
    }


@pytest.fixture
def healthy_indicators() -> Dict[str, float]:
    """Healthy operational indicators."""
    return {
        "OPS_SUPPLY_CHAIN": 0.85,
        "OPS_POWER_RELIABILITY": 0.90,
        "OPS_TRANSPORT_AVAIL": 0.80,
        "OPS_LABOR_AVAIL": 0.75,
        "OPS_DEMAND_LEVEL": 0.70,
    }


@pytest.fixture
def industry_context_provider() -> IndustryContextProvider:
    """Create IndustryContextProvider instance."""
    return IndustryContextProvider()


@pytest.fixture
def historical_analyzer() -> HistoricalContextAnalyzer:
    """Create HistoricalContextAnalyzer instance."""
    return HistoricalContextAnalyzer()


@pytest.fixture
def cross_industry_analyzer() -> CrossIndustryAnalyzer:
    """Create CrossIndustryAnalyzer instance."""
    return CrossIndustryAnalyzer()


@pytest.fixture
def cascading_analyzer() -> CascadingImpactAnalyzer:
    """Create CascadingImpactAnalyzer instance."""
    return CascadingImpactAnalyzer()


@pytest.fixture
def competitive_analyzer() -> CompetitiveIntelligenceAnalyzer:
    """Create CompetitiveIntelligenceAnalyzer instance."""
    return CompetitiveIntelligenceAnalyzer()


# ============================================================================
# Industry Context Tests
# ============================================================================

class TestIndustryContextProvider:
    """Tests for IndustryContextProvider."""
    
    def test_get_industry_benchmark_retail(
        self, industry_context_provider: IndustryContextProvider
    ):
        """Test getting benchmarks for retail industry and supply chain indicator."""
        benchmark = industry_context_provider.get_industry_benchmark("retail", "OPS_SUPPLY_CHAIN")
        
        assert benchmark is not None
        assert benchmark.industry == "retail"
        assert benchmark.indicator_code == "OPS_SUPPLY_CHAIN"
        assert 0 <= benchmark.industry_average <= 1
        assert 0 <= benchmark.top_quartile <= 1
    
    def test_get_industry_benchmark_manufacturing(
        self, industry_context_provider: IndustryContextProvider
    ):
        """Test getting benchmarks for manufacturing industry."""
        benchmark = industry_context_provider.get_industry_benchmark("manufacturing", "OPS_POWER_RELIABILITY")
        
        assert benchmark is not None
        assert benchmark.industry == "manufacturing"
        # Manufacturing typically has higher power requirements
        assert benchmark.industry_average >= 0.7
    
    def test_get_industry_benchmark_unknown(
        self, industry_context_provider: IndustryContextProvider
    ):
        """Test getting benchmarks for unknown industry returns None."""
        benchmark = industry_context_provider.get_industry_benchmark("unknown_industry", "OPS_SUPPLY_CHAIN")
        assert benchmark is None
    
    def test_compare_to_industry(
        self, 
        industry_context_provider: IndustryContextProvider,
    ):
        """Test comparing company to industry benchmark."""
        result = industry_context_provider.compare_to_industry(
            company_id="test_company",
            industry="retail",
            indicator_code="OPS_SUPPLY_CHAIN",
            company_value=0.35,  # Below average
        )
        
        assert result.company_id == "test_company"
        assert result.industry == "retail"
        assert result.company_value == 0.35
        assert 0 <= result.percentile_rank <= 100
        assert result.position in ["top_performer", "above_average", "below_average", "needs_improvement"]
    
    def test_get_full_benchmark_comparison(
        self,
        industry_context_provider: IndustryContextProvider,
        sample_company_indicators: Dict[str, float],
    ):
        """Test full benchmark comparison analysis."""
        result = industry_context_provider.get_full_benchmark_comparison(
            company_id="test_company",
            industry="retail",
            company_indicators=sample_company_indicators,
        )
        
        assert "overall_percentile" in result
        assert "overall_position" in result
        assert "comparisons" in result
        assert "strengths" in result
        assert "weaknesses" in result
    
    def test_get_peer_comparison(
        self,
        industry_context_provider: IndustryContextProvider,
        sample_company_indicators: Dict[str, float],
    ):
        """Test peer comparison functionality."""
        result = industry_context_provider.get_peer_comparison(
            company_id="test_company",
            industry="retail",
            company_indicators=sample_company_indicators,
            num_peers=5,
        )
        
        assert "company_rank" in result
        assert "total_peers" in result
        assert "company_score" in result
        assert "peers" in result


# ============================================================================
# Historical Context Tests
# ============================================================================

class TestHistoricalContextAnalyzer:
    """Tests for HistoricalContextAnalyzer."""
    
    def test_find_similar_events(
        self,
        historical_analyzer: HistoricalContextAnalyzer,
        sample_company_indicators: Dict[str, float],
    ):
        """Test finding similar historical events."""
        matches = historical_analyzer.find_similar_events(
            current_indicators=sample_company_indicators,
            top_n=3,
            min_similarity=0.3,
        )
        
        assert isinstance(matches, list)
        # Should find some matches with low indicators
        if matches:
            assert isinstance(matches[0], HistoricalMatch)
            assert 0 <= matches[0].similarity_score <= 1
    
    def test_find_similar_events_with_category_filter(
        self,
        historical_analyzer: HistoricalContextAnalyzer,
        sample_company_indicators: Dict[str, float],
    ):
        """Test finding events filtered by category."""
        matches = historical_analyzer.find_similar_events(
            current_indicators=sample_company_indicators,
            category="supply_chain",
            top_n=5,
        )
        
        for match in matches:
            assert match.event.category == "supply_chain"
    
    def test_get_historical_context_for_indicator(
        self,
        historical_analyzer: HistoricalContextAnalyzer,
    ):
        """Test getting historical context for an indicator."""
        context = historical_analyzer.get_historical_context(
            indicator_code="OPS_SUPPLY_CHAIN",
            current_value=0.35,
            lookback_days=365,
        )
        
        assert isinstance(context, TrendContext)
        assert context.indicator_code == "OPS_SUPPLY_CHAIN"
        assert context.current_value == 0.35
        assert context.trend_vs_history in [
            "at_historic_low", "below_average", "average", "above_average", "at_historic_high"
        ]
    
    def test_predict_event_impact(
        self,
        historical_analyzer: HistoricalContextAnalyzer,
        sample_company_indicators: Dict[str, float],
    ):
        """Test predicting event impact based on history."""
        result = historical_analyzer.predict_event_impact(
            current_indicators=sample_company_indicators,
            industry="retail",
            event_category="supply_chain",
        )
        
        assert "has_historical_precedent" in result
        if result["has_historical_precedent"]:
            assert "predicted_duration_days" in result
            assert "prediction_confidence" in result
            assert "most_similar_event" in result
    
    def test_get_leading_indicator_context(
        self,
        historical_analyzer: HistoricalContextAnalyzer,
        sample_company_indicators: Dict[str, float],
    ):
        """Test leading indicator analysis."""
        result = historical_analyzer.get_leading_indicator_context(
            current_indicators=sample_company_indicators
        )
        
        assert "indicators_analyzed" in result
        assert "warnings_found" in result
        assert "warnings" in result
        assert "overall_assessment" in result


# ============================================================================
# Cross-Industry Tests
# ============================================================================

class TestCrossIndustryAnalyzer:
    """Tests for CrossIndustryAnalyzer."""
    
    def test_analyze_cross_industry_effects(
        self,
        cross_industry_analyzer: CrossIndustryAnalyzer,
    ):
        """Test analyzing cross-industry effects."""
        insights = cross_industry_analyzer.analyze_cross_industry_effects(
            source_industry="logistics",
            event_type="supply_disruption",
            severity=0.7,
        )
        
        assert isinstance(insights, list)
        if insights:
            assert isinstance(insights[0], CrossIndustryInsight)
            assert insights[0].source_industry == "logistics"
            assert insights[0].impact_direction in ImpactDirection
            assert insights[0].impact_strength in ImpactStrength
    
    def test_get_industry_dependencies(
        self,
        cross_industry_analyzer: CrossIndustryAnalyzer,
    ):
        """Test getting industry dependencies."""
        deps = cross_industry_analyzer.get_industry_dependencies(
            industry="retail",
            direction="both",
        )
        
        assert "industry" in deps
        assert deps["industry"] == "retail"
        assert "incoming_dependencies" in deps or "outgoing_dependencies" in deps
    
    def test_get_industry_dependencies_incoming_only(
        self,
        cross_industry_analyzer: CrossIndustryAnalyzer,
    ):
        """Test getting only incoming dependencies."""
        deps = cross_industry_analyzer.get_industry_dependencies(
            industry="retail",
            direction="incoming",
        )
        
        assert "incoming_dependencies" in deps
        assert "outgoing_dependencies" not in deps
    
    def test_identify_vulnerable_chains(
        self,
        cross_industry_analyzer: CrossIndustryAnalyzer,
    ):
        """Test identifying vulnerable supply chains."""
        indicators = {
            "logistics": {"OPS_TRANSPORT_AVAIL": 0.25, "OPS_SUPPLY_CHAIN": 0.30},
            "retail": {"OPS_SUPPLY_CHAIN": 0.60},
        }
        
        chains = cross_industry_analyzer.identify_vulnerable_chains(indicators)
        
        assert isinstance(chains, list)
        # Should identify logistics as vulnerable
        if chains:
            assert "source_industry" in chains[0]
    
    def test_get_early_warning_signals(
        self,
        cross_industry_analyzer: CrossIndustryAnalyzer,
    ):
        """Test getting early warning signals."""
        related_indicators = {
            "logistics": {"OPS_TRANSPORT_AVAIL": 0.25},
            "manufacturing": {"OPS_PRODUCTION_CAP": 0.60},
        }
        
        warnings = cross_industry_analyzer.get_early_warning_signals(
            target_industry="retail",
            related_industry_indicators=related_indicators,
        )
        
        assert isinstance(warnings, list)


# ============================================================================
# Cascading Impact Tests
# ============================================================================

class TestCascadingImpactAnalyzer:
    """Tests for CascadingImpactAnalyzer."""
    
    def test_analyze_cascade_port_strike(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test analyzing cascade for port strike."""
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="port_strike",
            trigger_severity=0.8,
        )
        
        assert isinstance(cascade, CascadeChain)
        assert cascade.trigger_event == "port_strike"
        assert cascade.trigger_severity == 0.8
        assert len(cascade.nodes) > 0
        assert cascade.total_depth > 0
    
    def test_analyze_cascade_fuel_shortage(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test analyzing cascade for fuel shortage."""
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="fuel_shortage",
            trigger_severity=0.7,
        )
        
        assert isinstance(cascade, CascadeChain)
        assert len(cascade.nodes) > 0
    
    def test_cascade_includes_nodes(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test that cascade contains proper node structure."""
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="power_outage",
            trigger_severity=0.9,
        )
        
        for node in cascade.nodes:
            assert isinstance(node, CascadeNode)
            assert node.node_id
            assert node.name
            assert 0 <= node.impact_magnitude <= 1
            assert node.impact_phase in ImpactPhase
    
    def test_trace_impact_path(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test tracing impact path between points."""
        path = cascading_analyzer.trace_impact_path(
            source="fuel_availability",
            target="retail_stock",
            max_hops=5,
        )
        
        # May or may not find path depending on model
        if path:
            assert isinstance(path, list)
            assert all(isinstance(n, CascadeNode) for n in path)
    
    def test_get_timeline_projection(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test getting timeline projection for cascade."""
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="port_strike",
            trigger_severity=0.8,
        )
        
        timeline = cascading_analyzer.get_timeline_projection(cascade)
        
        assert isinstance(timeline, list)
        if timeline:
            assert "phase" in timeline[0]
            assert "events" in timeline[0]
    
    def test_identify_intervention_points(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test identifying intervention points."""
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="fuel_shortage",
            trigger_severity=0.8,
        )
        
        interventions = cascading_analyzer.identify_intervention_points(cascade)
        
        assert isinstance(interventions, list)
        if interventions:
            assert "node_id" in interventions[0]
            assert "intervention_effectiveness" in interventions[0]
            assert "recommended_actions" in interventions[0]
    
    def test_estimate_total_impact(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test estimating total impact of cascade."""
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="power_outage",
            trigger_severity=0.9,
        )
        
        impact = cascading_analyzer.estimate_total_impact(cascade)
        
        assert "total_impact_score" in impact
        assert "peak_impact" in impact
        assert "severity_rating" in impact
    
    def test_estimate_total_impact_filtered_by_industry(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test estimating impact filtered by industry."""
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="port_strike",
            trigger_severity=0.7,
        )
        
        impact = cascading_analyzer.estimate_total_impact(
            cascade, industry="retail"
        )
        
        assert "industry_filter" in impact
        assert impact["industry_filter"] == "retail"


# ============================================================================
# Competitive Intelligence Tests
# ============================================================================

class TestCompetitiveIntelligenceAnalyzer:
    """Tests for CompetitiveIntelligenceAnalyzer."""
    
    def test_get_competitor_activity(
        self,
        competitive_analyzer: CompetitiveIntelligenceAnalyzer,
    ):
        """Test getting competitor activity."""
        activity = competitive_analyzer.get_competitor_activity(
            industry="retail",
            lookback_days=30,
        )
        
        assert "industry" in activity
        assert "total_moves_detected" in activity
        assert "overall_threat_level" in activity
        assert activity["industry"] == "retail"
    
    def test_analyze_market_position(
        self,
        competitive_analyzer: CompetitiveIntelligenceAnalyzer,
        sample_company_indicators: Dict[str, float],
    ):
        """Test analyzing market position."""
        analysis = competitive_analyzer.analyze_market_position(
            company_id="test_company",
            industry="retail",
            company_indicators=sample_company_indicators,
        )
        
        assert isinstance(analysis, MarketPositionAnalysis)
        assert analysis.company_id == "test_company"
        assert analysis.industry == "retail"
        assert analysis.position_category in ["leader", "challenger", "follower", "niche"]
    
    def test_assess_competitive_threat(
        self,
        competitive_analyzer: CompetitiveIntelligenceAnalyzer,
    ):
        """Test assessing competitive threats."""
        assessment = competitive_analyzer.assess_competitive_threat(
            company_id="test_company",
            industry="retail",
        )
        
        assert "overall_threat_level" in assessment
        assert "threats" in assessment
        assert "recommended_actions" in assessment
    
    def test_identify_competitive_opportunities(
        self,
        competitive_analyzer: CompetitiveIntelligenceAnalyzer,
    ):
        """Test identifying competitive opportunities."""
        opportunities = competitive_analyzer.identify_competitive_opportunities(
            company_id="test_company",
            industry="retail",
            company_strengths=["customer service", "local presence"],
        )
        
        assert "total_opportunities" in opportunities
        assert "top_opportunities" in opportunities
        assert "by_type" in opportunities
    
    def test_get_competitor_comparison(
        self,
        competitive_analyzer: CompetitiveIntelligenceAnalyzer,
    ):
        """Test competitor comparison."""
        comparison = competitive_analyzer.get_competitor_comparison(
            company_id="test_company",
            competitor_ids=["comp_retail_1", "comp_retail_2"],
        )
        
        assert "comparisons" in comparison
        if comparison.get("comparisons"):
            assert "competitor_name" in comparison["comparisons"][0]
            assert "overlap_scores" in comparison["comparisons"][0]
    
    def test_threat_level_enum_values(self):
        """Test ThreatLevel enum values."""
        assert ThreatLevel.LOW.value == "low"
        assert ThreatLevel.MODERATE.value == "moderate"
        assert ThreatLevel.HIGH.value == "high"
        assert ThreatLevel.CRITICAL.value == "critical"
    
    def test_opportunity_level_enum_values(self):
        """Test OpportunityLevel enum values."""
        assert OpportunityLevel.MARGINAL.value == "marginal"
        assert OpportunityLevel.NOTABLE.value == "notable"
        assert OpportunityLevel.SIGNIFICANT.value == "significant"
        assert OpportunityLevel.MAJOR.value == "major"
    
    def test_competitor_move_type_enum_values(self):
        """Test CompetitorMoveType enum values."""
        assert CompetitorMoveType.EXPANSION.value == "expansion"
        assert CompetitorMoveType.PRICING.value == "pricing"
        assert CompetitorMoveType.ACQUISITION.value == "acquisition"


# ============================================================================
# Integration Tests
# ============================================================================

class TestContextualIntelligenceIntegration:
    """Integration tests for contextual intelligence components."""
    
    def test_full_context_analysis_workflow(
        self,
        industry_context_provider: IndustryContextProvider,
        historical_analyzer: HistoricalContextAnalyzer,
        cross_industry_analyzer: CrossIndustryAnalyzer,
        cascading_analyzer: CascadingImpactAnalyzer,
        competitive_analyzer: CompetitiveIntelligenceAnalyzer,
        sample_company_indicators: Dict[str, float],
    ):
        """Test complete contextual analysis workflow."""
        industry = "retail"
        company_id = "test_company"
        
        # Step 1: Get industry benchmark for a key indicator
        benchmark = industry_context_provider.get_industry_benchmark(industry, "OPS_SUPPLY_CHAIN")
        assert benchmark is not None
        
        # Step 2: Get full benchmark comparison
        comparison = industry_context_provider.get_full_benchmark_comparison(
            company_id, industry, sample_company_indicators
        )
        assert "overall_position" in comparison
        
        # Step 3: Find historical parallels
        historical_matches = historical_analyzer.find_similar_events(
            sample_company_indicators, top_n=3
        )
        
        # Step 4: Check for cross-industry effects
        if comparison.get("weaknesses"):
            cross_effects = cross_industry_analyzer.get_early_warning_signals(
                target_industry=industry,
                related_industry_indicators={"logistics": sample_company_indicators}
            )
        
        # Step 5: Model potential cascade
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="supply_disruption",
            trigger_severity=0.7,
        )
        assert len(cascade.nodes) > 0
        
        # Step 6: Check competitive landscape
        threats = competitive_analyzer.assess_competitive_threat(
            company_id=company_id,
            industry=industry,
        )
        assert "overall_threat_level" in threats
    
    def test_combined_historical_and_cross_industry(
        self,
        historical_analyzer: HistoricalContextAnalyzer,
        cross_industry_analyzer: CrossIndustryAnalyzer,
        sample_company_indicators: Dict[str, float],
    ):
        """Test combining historical and cross-industry analysis."""
        # Get historical matches
        matches = historical_analyzer.find_similar_events(
            sample_company_indicators,
            category="supply_chain",
        )
        
        # For each match, analyze cross-industry effects
        if matches:
            match = matches[0]
            
            # Analyze potential cross-industry effects from historical event type
            cross_effects = cross_industry_analyzer.analyze_cross_industry_effects(
                source_industry="logistics",
                event_type=match.event.event_type,
                severity=match.event.severity == "severe" and 0.8 or 0.5,
            )
    
    def test_cascade_to_competitive_impact(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
        competitive_analyzer: CompetitiveIntelligenceAnalyzer,
    ):
        """Test linking cascade analysis to competitive impact."""
        # Analyze cascade
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="fuel_shortage",
            trigger_severity=0.8,
        )
        
        # Estimate impact
        impact = cascading_analyzer.estimate_total_impact(cascade, industry="retail")
        
        # Check competitive landscape given the impact
        if impact.get("severity_rating") in ("severe", "critical"):
            threats = competitive_analyzer.assess_competitive_threat(
                company_id="test_company",
                industry="retail",
            )
            
            # During crisis, monitor competitors more closely
            assert threats is not None


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestContextualIntelligenceEdgeCases:
    """Edge case tests for contextual intelligence."""
    
    def test_empty_indicators_comparison(
        self,
        industry_context_provider: IndustryContextProvider,
    ):
        """Test handling empty indicators in comparison."""
        result = industry_context_provider.get_full_benchmark_comparison(
            company_id="test_company",
            industry="retail",
            company_indicators={},
        )
        # Should handle gracefully - comparisons will be empty
        assert result is not None
        assert result["comparisons"] == []
    
    def test_unknown_industry_in_comparison(
        self,
        industry_context_provider: IndustryContextProvider,
    ):
        """Test handling unknown industry in comparison."""
        result = industry_context_provider.compare_to_industry(
            company_id="test_company",
            industry="unknown_industry",
            indicator_code="OPS_SUPPLY_CHAIN",
            company_value=0.5,
        )
        # Should return default result with no benchmark message
        assert result is not None
        assert "No industry benchmark data available" in result.comparison_narrative
    
    def test_historical_no_matches(
        self,
        historical_analyzer: HistoricalContextAnalyzer,
    ):
        """Test historical search with no matches."""
        # Use indicators that won't match anything
        matches = historical_analyzer.find_similar_events(
            current_indicators={"UNKNOWN_INDICATOR": 0.99},
            min_similarity=0.9,  # High threshold
        )
        # Should return empty list, not error
        assert matches == []
    
    def test_cascade_unknown_event(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test cascade with unknown event type."""
        # Should use generic template
        cascade = cascading_analyzer.analyze_cascade(
            trigger_event="unknown_event_type",
            trigger_severity=0.5,
        )
        
        assert cascade is not None
        assert len(cascade.nodes) > 0
    
    def test_competitive_no_competitors(
        self,
        competitive_analyzer: CompetitiveIntelligenceAnalyzer,
    ):
        """Test competitive analysis for industry with no tracked competitors."""
        activity = competitive_analyzer.get_competitor_activity(
            industry="unknown_industry",
            lookback_days=30,
        )
        
        # Should return empty activity, not error
        assert activity["total_moves_detected"] == 0


# ============================================================================
# Performance Tests
# ============================================================================

class TestContextualIntelligencePerformance:
    """Performance tests for contextual intelligence."""
    
    def test_cascade_analysis_performance(
        self,
        cascading_analyzer: CascadingImpactAnalyzer,
    ):
        """Test cascade analysis completes in reasonable time."""
        import time
        
        start = time.time()
        
        for _ in range(10):
            cascading_analyzer.analyze_cascade(
                trigger_event="port_strike",
                trigger_severity=0.8,
            )
        
        elapsed = time.time() - start
        
        # Should complete 10 analyses in under 1 second
        assert elapsed < 1.0, f"Cascade analysis too slow: {elapsed}s for 10 analyses"
    
    def test_cross_industry_analysis_performance(
        self,
        cross_industry_analyzer: CrossIndustryAnalyzer,
    ):
        """Test cross-industry analysis completes in reasonable time."""
        import time
        
        start = time.time()
        
        for _ in range(20):
            cross_industry_analyzer.analyze_cross_industry_effects(
                source_industry="logistics",
                event_type="supply_disruption",
                severity=0.7,
            )
        
        elapsed = time.time() - start
        
        # Should complete 20 analyses in under 1 second
        assert elapsed < 1.0, f"Cross-industry analysis too slow: {elapsed}s for 20 analyses"
