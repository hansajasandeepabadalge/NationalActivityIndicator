"""
Tests for Layer 4: Prioritization Engine

Tests the InsightPrioritizer which combines risks and opportunities
into a unified, ranked priority list.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from typing import List

from app.layer4.prioritization import InsightPrioritizer
from app.layer4.schemas.risk_schemas import DetectedRisk
from app.layer4.schemas.opportunity_schemas import DetectedOpportunity
from app.layer4.schemas.insight_schemas import InsightPriority, TopPriorities


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def prioritizer():
    """Create a fresh InsightPrioritizer instance."""
    return InsightPrioritizer()


@pytest.fixture
def sample_risks() -> List[DetectedRisk]:
    """Create sample detected risks for testing."""
    return [
        DetectedRisk(
            risk_code="RISK_POWER_001",
            company_id="COMP001",
            title="Power Supply Reliability Risk",
            description="Power reliability has dropped below 70%",
            category="infrastructure",
            probability=Decimal("0.75"),
            impact=Decimal("8.0"),
            urgency=4,  # High urgency
            confidence=Decimal("0.85"),
            final_score=Decimal("7.2"),
            severity_level="high",
            triggering_indicators={"OPS_POWER_RELIABILITY": 0.65},
            detection_method="rule_based",
        ),
        DetectedRisk(
            risk_code="RISK_LOGISTICS_001",
            company_id="COMP001",
            title="Logistics Efficiency Degradation",
            description="Transportation efficiency below threshold",
            category="operational",
            probability=Decimal("0.60"),
            impact=Decimal("6.5"),
            urgency=3,  # Medium urgency
            confidence=Decimal("0.80"),
            final_score=Decimal("5.8"),
            severity_level="medium",
            triggering_indicators={"OPS_LOGISTICS_EFFICIENCY": 0.55},
            detection_method="rule_based",
        ),
        DetectedRisk(
            risk_code="RISK_CRITICAL_001",
            company_id="COMP001",
            title="Critical Cash Flow Risk",
            description="Severe working capital strain detected",
            category="financial",
            probability=Decimal("0.80"),
            impact=Decimal("9.5"),
            urgency=5,  # Critical urgency
            confidence=Decimal("0.90"),
            final_score=Decimal("8.5"),
            severity_level="critical",
            triggering_indicators={"OPS_CASH_FLOW": 0.30},
            detection_method="rule_based",
        ),
    ]


@pytest.fixture
def sample_opportunities() -> List[DetectedOpportunity]:
    """Create sample detected opportunities for testing."""
    return [
        DetectedOpportunity(
            opportunity_code="OPP_ENERGY_001",
            company_id="COMP001",
            title="Energy Efficiency Optimization",
            description="High energy costs present efficiency opportunity",
            category="cost_reduction",
            potential_value=Decimal("7.5"),
            feasibility=Decimal("0.75"),
            timing_score=Decimal("0.80"),
            strategic_fit=Decimal("0.85"),
            final_score=Decimal("7.2"),
            priority_level="high",
            triggering_indicators={"OPS_INPUT_COST": 0.80},
            detection_method="gap_analysis",
        ),
        DetectedOpportunity(
            opportunity_code="OPP_MARKET_001",
            company_id="COMP001",
            title="Market Expansion Opportunity",
            description="Strong market demand suggests expansion",
            category="market_expansion",
            potential_value=Decimal("8.0"),
            feasibility=Decimal("0.65"),
            timing_score=Decimal("0.70"),
            strategic_fit=Decimal("0.80"),
            final_score=Decimal("6.8"),
            priority_level="high",
            triggering_indicators={"OPS_MARKET_DEMAND": 0.70},
            detection_method="gap_analysis",
        ),
    ]


@pytest.fixture
def company_profile():
    """Create a sample company profile."""
    return {
        "company_id": "COMP001",
        "industry": "manufacturing",
        "risk_appetite": "moderate",
        "strategic_priorities": ["cost_reduction", "operational_efficiency"],
    }


# ==============================================================================
# Prioritizer Initialization Tests
# ==============================================================================

class TestPrioritizerInitialization:
    """Test prioritizer initialization."""
    
    def test_prioritizer_creates_with_defaults(self):
        """Test prioritizer initializes with default values."""
        prioritizer = InsightPrioritizer()
        
        assert prioritizer.urgency_weight == 0.30
        assert prioritizer.actionability_weight == 0.25
        assert prioritizer.severity_weight == 0.25
        assert prioritizer.strategic_weight == 0.15
        assert prioritizer.time_sensitivity_weight == 0.05
    
    def test_prioritizer_with_company_profile(self, company_profile):
        """Test prioritizer initializes with company profile."""
        prioritizer = InsightPrioritizer(company_profile=company_profile)
        
        assert prioritizer.company_profile == company_profile
    
    def test_prioritizer_has_category_actionability(self, prioritizer):
        """Test prioritizer has category actionability scores."""
        assert "operational" in prioritizer.category_actionability
        assert "infrastructure" in prioritizer.category_actionability
        assert "cost_reduction" in prioritizer.category_actionability
        
        # Check values are between 0 and 1
        for score in prioritizer.category_actionability.values():
            assert 0 <= score <= 1
    
    def test_prioritizer_has_strategic_importance(self, prioritizer):
        """Test prioritizer has strategic importance scores."""
        assert "operational" in prioritizer.category_strategic_importance
        assert "financial" in prioritizer.category_strategic_importance
        assert "market_expansion" in prioritizer.category_strategic_importance


# ==============================================================================
# Basic Prioritization Tests
# ==============================================================================

class TestBasicPrioritization:
    """Test basic prioritization functionality."""
    
    def test_prioritize_returns_top_priorities(self, prioritizer, sample_risks, sample_opportunities):
        """Test prioritize returns TopPriorities object."""
        result = prioritizer.prioritize(sample_risks, sample_opportunities)
        
        assert isinstance(result, TopPriorities)
        assert result.company_id == "COMP001"
        assert result.total_risks == 3
        assert result.total_opportunities == 2
        assert result.total_active_insights == 5
    
    def test_prioritize_ranks_by_priority_score(self, prioritizer, sample_risks, sample_opportunities):
        """Test insights are ranked by priority score."""
        priorities = prioritizer.prioritize_all(sample_risks, sample_opportunities)
        
        # Verify descending order by priority_score
        scores = [float(p.priority_score) for p in priorities]
        assert scores == sorted(scores, reverse=True)
    
    def test_prioritize_assigns_ranks(self, prioritizer, sample_risks, sample_opportunities):
        """Test each insight gets a unique rank."""
        priorities = prioritizer.prioritize_all(sample_risks, sample_opportunities)
        
        ranks = [p.priority_rank for p in priorities]
        expected_ranks = list(range(1, len(priorities) + 1))
        assert sorted(ranks) == expected_ranks
    
    def test_prioritize_respects_top_n(self, prioritizer, sample_risks, sample_opportunities):
        """Test prioritize returns only top_n items."""
        result = prioritizer.prioritize(sample_risks, sample_opportunities, top_n=3)
        
        assert len(result.priorities) == 3
    
    def test_prioritize_with_empty_lists(self, prioritizer):
        """Test prioritize handles empty lists."""
        result = prioritizer.prioritize([], [])
        
        assert result.total_active_insights == 0
        assert result.priorities == []


# ==============================================================================
# Priority Score Calculation Tests
# ==============================================================================

class TestPriorityScoreCalculation:
    """Test priority score calculations."""
    
    def test_critical_severity_gets_higher_score(self, prioritizer, sample_risks):
        """Test critical severity risks get boosted scores."""
        # Get the critical risk (RISK_CRITICAL_001)
        result = prioritizer.prioritize(sample_risks, [])
        
        # Critical risk should be ranked first
        top_priority = result.priorities[0]
        assert top_priority.severity_level == "critical"
    
    def test_high_urgency_increases_score(self, prioritizer):
        """Test higher urgency leads to higher priority score."""
        high_urgency_risk = DetectedRisk(
            risk_code="HIGH_URG",
            company_id="COMP001",
            title="High Urgency Risk",
            description="Very urgent issue",
            category="operational",
            probability=Decimal("0.70"),
            impact=Decimal("7.0"),
            urgency=5,  # Maximum urgency
            confidence=Decimal("0.80"),
            final_score=Decimal("6.0"),
            severity_level="high",
            triggering_indicators={},
            detection_method="rule_based",
        )
        
        low_urgency_risk = DetectedRisk(
            risk_code="LOW_URG",
            company_id="COMP001",
            title="Low Urgency Risk",
            description="Less urgent issue",
            category="operational",
            probability=Decimal("0.70"),
            impact=Decimal("7.0"),
            urgency=1,  # Minimum urgency
            confidence=Decimal("0.80"),
            final_score=Decimal("6.0"),
            severity_level="high",
            triggering_indicators={},
            detection_method="rule_based",
        )
        
        result = prioritizer.prioritize([high_urgency_risk, low_urgency_risk], [])
        
        # High urgency should rank higher
        assert result.priorities[0].title == "High Urgency Risk"
    
    def test_actionability_affects_score(self, prioritizer):
        """Test actionability score is calculated based on category."""
        operational_risk = DetectedRisk(
            risk_code="OP_RISK",
            company_id="COMP001",
            title="Operational Risk",
            description="Operational issue",
            category="operational",  # High actionability (0.90)
            probability=Decimal("0.70"),
            impact=Decimal("7.0"),
            urgency=3,
            confidence=Decimal("0.80"),
            final_score=Decimal("6.0"),
            severity_level="medium",
            triggering_indicators={},
            detection_method="rule_based",
        )
        
        result = prioritizer.prioritize([operational_risk], [])
        
        # Check actionability score is set
        assert float(result.priorities[0].actionability_score) == 0.90
    
    def test_strategic_importance_affects_score(self, prioritizer):
        """Test strategic importance is calculated based on category."""
        financial_risk = DetectedRisk(
            risk_code="FIN_RISK",
            company_id="COMP001",
            title="Financial Risk",
            description="Financial issue",
            category="financial",  # High strategic importance (0.95)
            probability=Decimal("0.70"),
            impact=Decimal("7.0"),
            urgency=3,
            confidence=Decimal("0.80"),
            final_score=Decimal("6.0"),
            severity_level="medium",
            triggering_indicators={},
            detection_method="rule_based",
        )
        
        result = prioritizer.prioritize([financial_risk], [])
        
        # Check strategic importance is set
        assert float(result.priorities[0].strategic_importance) == 0.95


# ==============================================================================
# Urgent Items Tests
# ==============================================================================

class TestUrgentItems:
    """Test urgent item marking and filtering."""
    
    def test_critical_marked_requires_immediate_action(self, prioritizer, sample_risks):
        """Test critical severity items marked as requiring immediate action."""
        result = prioritizer.prioritize(sample_risks, [])
        
        # Find the critical risk
        critical_priorities = [p for p in result.priorities if p.severity_level == "critical"]
        
        assert len(critical_priorities) > 0
        for p in critical_priorities:
            assert p.requires_immediate_action is True
    
    def test_top_3_high_severity_marked_urgent(self, prioritizer, sample_risks, sample_opportunities):
        """Test top 3 high/critical severity items marked as urgent."""
        result = prioritizer.prioritize(sample_risks, sample_opportunities)
        
        # Get urgent items
        urgent = [p for p in result.priorities if p.is_urgent]
        
        # Should have at least some urgent items
        assert len(urgent) > 0
    
    def test_get_urgent_items_method(self, prioritizer, sample_risks, sample_opportunities):
        """Test get_urgent_items returns only urgent items."""
        urgent_items = prioritizer.get_urgent_items(sample_risks, sample_opportunities)
        
        # All returned items should be urgent or require immediate action
        for item in urgent_items:
            assert item.is_urgent or item.requires_immediate_action


# ==============================================================================
# Wrapper Methods Tests
# ==============================================================================

class TestWrapperMethods:
    """Test convenience wrapper methods."""
    
    def test_prioritize_all_returns_list(self, prioritizer, sample_risks, sample_opportunities):
        """Test prioritize_all returns a list of InsightPriority."""
        result = prioritizer.prioritize_all(sample_risks, sample_opportunities)
        
        assert isinstance(result, list)
        assert all(isinstance(p, InsightPriority) for p in result)
        assert len(result) == 5  # 3 risks + 2 opportunities
    
    def test_get_top_priorities_returns_top_priorities(self, prioritizer, sample_risks, sample_opportunities):
        """Test get_top_priorities returns TopPriorities object."""
        result = prioritizer.get_top_priorities(sample_risks, sample_opportunities, limit=3)
        
        assert isinstance(result, TopPriorities)
        assert len(result.priorities) == 3
    
    def test_get_top_priorities_with_company_profile(self, prioritizer, sample_risks, sample_opportunities, company_profile):
        """Test get_top_priorities accepts company profile."""
        result = prioritizer.get_top_priorities(
            sample_risks, 
            sample_opportunities, 
            company_profile=company_profile,
            limit=5
        )
        
        assert result.total_active_insights == 5
    
    def test_prioritize_risks_only(self, prioritizer, sample_risks):
        """Test prioritize_risks_only returns only risk priorities."""
        result = prioritizer.prioritize_risks_only(sample_risks, top_n=2)
        
        assert len(result) == 2
        for p in result:
            assert p.insight_type == "risk"
    
    def test_prioritize_opportunities_only(self, prioritizer, sample_opportunities):
        """Test prioritize_opportunities_only returns only opportunity priorities."""
        result = prioritizer.prioritize_opportunities_only(sample_opportunities, top_n=2)
        
        assert len(result) == 2
        for p in result:
            assert p.insight_type == "opportunity"


# ==============================================================================
# Filtering Methods Tests
# ==============================================================================

class TestFilteringMethods:
    """Test category and severity filtering."""
    
    def test_get_by_category(self, prioritizer, sample_risks, sample_opportunities):
        """Test filtering priorities by category."""
        result = prioritizer.get_by_category(
            sample_risks, 
            sample_opportunities, 
            category="infrastructure"
        )
        
        assert all(p.category == "infrastructure" for p in result)
    
    def test_get_by_severity(self, prioritizer, sample_risks, sample_opportunities):
        """Test filtering priorities by severity."""
        result = prioritizer.get_by_severity(
            sample_risks, 
            sample_opportunities, 
            severity="high"
        )
        
        assert all(p.severity_level == "high" for p in result)


# ==============================================================================
# Priority Summary Tests
# ==============================================================================

class TestPrioritySummary:
    """Test priority summary calculation."""
    
    def test_calculate_priority_summary(self, prioritizer, sample_risks, sample_opportunities):
        """Test priority summary calculation."""
        summary = prioritizer.calculate_priority_summary(sample_risks, sample_opportunities)
        
        assert summary["total_insights"] == 5
        assert summary["total_risks"] == 3
        assert summary["total_opportunities"] == 2
        assert "by_severity" in summary
        assert "by_category" in summary
    
    def test_summary_includes_top_priority(self, prioritizer, sample_risks, sample_opportunities):
        """Test summary includes top priority."""
        summary = prioritizer.calculate_priority_summary(sample_risks, sample_opportunities)
        
        assert summary["top_priority"] is not None
    
    def test_summary_counts_urgent_items(self, prioritizer, sample_risks, sample_opportunities):
        """Test summary counts urgent items."""
        summary = prioritizer.calculate_priority_summary(sample_risks, sample_opportunities)
        
        assert "urgent_items" in summary
        assert "requires_immediate_action" in summary


# ==============================================================================
# Company Profile Adjustment Tests
# ==============================================================================

class TestCompanyProfileAdjustments:
    """Test company profile adjustments to scoring."""
    
    def test_conservative_risk_appetite_boosts_risks(self):
        """Test conservative companies prioritize risks higher."""
        conservative_profile = {
            "industry": "manufacturing",
            "risk_appetite": "conservative",
            "strategic_priorities": [],
        }
        
        prioritizer = InsightPrioritizer(company_profile=conservative_profile)
        
        risk = DetectedRisk(
            risk_code="TEST_RISK",
            company_id="COMP001",
            title="Test Risk",
            description="Test",
            category="operational",
            probability=Decimal("0.70"),
            impact=Decimal("7.0"),
            urgency=3,
            confidence=Decimal("0.80"),
            final_score=Decimal("6.0"),
            severity_level="medium",
            triggering_indicators={},
            detection_method="rule_based",
        )
        
        result = prioritizer.prioritize([risk], [])
        
        # Result should exist
        assert len(result.priorities) == 1
    
    def test_strategic_priorities_boost_matching_categories(self):
        """Test strategic priorities boost matching categories."""
        cost_focused_profile = {
            "industry": "manufacturing",
            "risk_appetite": "moderate",
            "strategic_priorities": ["cost_reduction"],
        }
        
        prioritizer = InsightPrioritizer(company_profile=cost_focused_profile)
        
        cost_opp = DetectedOpportunity(
            opportunity_code="COST_OPP",
            company_id="COMP001",
            title="Cost Reduction Opportunity",
            description="Test",
            category="cost_reduction",
            potential_value=Decimal("7.0"),
            feasibility=Decimal("0.70"),
            timing_score=Decimal("0.70"),
            strategic_fit=Decimal("0.80"),
            final_score=Decimal("6.5"),
            priority_level="high",
            triggering_indicators={},
            detection_method="gap_analysis",
        )
        
        other_opp = DetectedOpportunity(
            opportunity_code="OTHER_OPP",
            company_id="COMP001",
            title="Market Opportunity",
            description="Test",
            category="market_expansion",
            potential_value=Decimal("7.0"),
            feasibility=Decimal("0.70"),
            timing_score=Decimal("0.70"),
            strategic_fit=Decimal("0.80"),
            final_score=Decimal("6.5"),
            priority_level="high",
            triggering_indicators={},
            detection_method="gap_analysis",
        )
        
        result = prioritizer.prioritize([], [cost_opp, other_opp])
        
        # Cost reduction should be prioritized due to strategic alignment
        assert result.priorities[0].category == "cost_reduction"


# ==============================================================================
# Edge Case Tests
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_risk(self, prioritizer):
        """Test with single risk."""
        risk = DetectedRisk(
            risk_code="SINGLE",
            company_id="COMP001",
            title="Single Risk",
            description="Only one",
            category="operational",
            probability=Decimal("0.70"),
            impact=Decimal("7.0"),
            urgency=3,
            confidence=Decimal("0.80"),
            final_score=Decimal("6.0"),
            severity_level="medium",
            triggering_indicators={},
            detection_method="rule_based",
        )
        
        result = prioritizer.prioritize([risk], [])
        
        assert len(result.priorities) == 1
        assert result.priorities[0].priority_rank == 1
    
    def test_single_opportunity(self, prioritizer):
        """Test with single opportunity."""
        opp = DetectedOpportunity(
            opportunity_code="SINGLE",
            company_id="COMP001",
            title="Single Opportunity",
            description="Only one",
            category="cost_reduction",
            potential_value=Decimal("7.0"),
            feasibility=Decimal("0.70"),
            timing_score=Decimal("0.70"),
            strategic_fit=Decimal("0.80"),
            final_score=Decimal("6.5"),
            priority_level="high",
            triggering_indicators={},
            detection_method="gap_analysis",
        )
        
        result = prioritizer.prioritize([], [opp])
        
        assert len(result.priorities) == 1
        assert result.priorities[0].insight_type == "opportunity"
    
    def test_unknown_category_uses_default(self, prioritizer):
        """Test unknown category uses default actionability."""
        risk = DetectedRisk(
            risk_code="UNKNOWN_CAT",
            company_id="COMP001",
            title="Unknown Category Risk",
            description="Test",
            category="unknown_category",  # Not in category_actionability
            probability=Decimal("0.70"),
            impact=Decimal("7.0"),
            urgency=3,
            confidence=Decimal("0.80"),
            final_score=Decimal("6.0"),
            severity_level="medium",
            triggering_indicators={},
            detection_method="rule_based",
        )
        
        result = prioritizer.prioritize([risk], [])
        
        # Should not fail, uses default
        assert len(result.priorities) == 1
    
    def test_configurable_weights(self):
        """Test weights can be configured."""
        prioritizer = InsightPrioritizer()
        
        # Modify weights
        prioritizer.urgency_weight = 0.50
        prioritizer.actionability_weight = 0.20
        prioritizer.severity_weight = 0.20
        prioritizer.strategic_weight = 0.10
        
        risk = DetectedRisk(
            risk_code="CONFIG_TEST",
            company_id="COMP001",
            title="Config Test Risk",
            description="Test",
            category="operational",
            probability=Decimal("0.70"),
            impact=Decimal("7.0"),
            urgency=5,  # High urgency
            confidence=Decimal("0.80"),
            final_score=Decimal("6.0"),
            severity_level="medium",
            triggering_indicators={},
            detection_method="rule_based",
        )
        
        result = prioritizer.prioritize([risk], [])
        
        # Should work with modified weights
        assert len(result.priorities) == 1
