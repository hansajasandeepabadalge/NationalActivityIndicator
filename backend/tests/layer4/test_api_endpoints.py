"""
Layer 4: API Endpoint Tests

Tests for the insights API endpoints including risks, opportunities,
recommendations, and action plans.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from decimal import Decimal

# We need to set up a test client
# First, let's import what we need


class TestRiskEndpoints:
    """Test risk detection API endpoints"""
    
    def test_detect_risks_endpoint_exists(self):
        """Test that detect risks endpoint is defined"""
        from app.api.v1.endpoints.insights import detect_risks
        
        # Verify the function exists and is callable
        assert callable(detect_risks)
    
    def test_list_risks_returns_list(self):
        """Test that list risks endpoint returns mock data"""
        from app.api.v1.endpoints.insights import _get_mock_risks
        
        risks = _get_mock_risks()
        
        assert isinstance(risks, list)
        assert len(risks) > 0
        
        # Check first risk structure
        risk = risks[0]
        assert hasattr(risk, 'insight_id')
        assert hasattr(risk, 'company_id')
        assert hasattr(risk, 'title')
        assert hasattr(risk, 'category')
        assert hasattr(risk, 'score_breakdown')
    
    def test_list_risks_with_company_filter(self):
        """Test risk filtering by company ID"""
        from app.api.v1.endpoints.insights import _get_mock_risks
        
        risks = _get_mock_risks(company_id="COMP001")
        
        for risk in risks:
            assert risk.company_id == "COMP001"
    
    def test_list_risks_with_category_filter(self):
        """Test risk filtering by category"""
        from app.api.v1.endpoints.insights import _get_mock_risks
        
        risks = _get_mock_risks(category="infrastructure")
        
        for risk in risks:
            assert risk.category == "infrastructure"
    
    def test_list_risks_with_severity_filter(self):
        """Test risk filtering by severity"""
        from app.api.v1.endpoints.insights import _get_mock_risks
        
        risks = _get_mock_risks(severity="high")
        
        for risk in risks:
            assert risk.score_breakdown.severity == "high"
    
    def test_risk_score_breakdown_fields(self):
        """Test that risk score breakdown has all required fields"""
        from app.api.v1.endpoints.insights import _get_mock_risks
        
        risks = _get_mock_risks()
        risk = risks[0]
        breakdown = risk.score_breakdown
        
        assert hasattr(breakdown, 'probability')
        assert hasattr(breakdown, 'impact')
        assert hasattr(breakdown, 'urgency')
        assert hasattr(breakdown, 'confidence')
        assert hasattr(breakdown, 'final_score')
        assert hasattr(breakdown, 'severity')
        
        # Validate value ranges
        assert 0 <= float(breakdown.probability) <= 1
        assert 0 <= float(breakdown.impact) <= 10
        assert 1 <= breakdown.urgency <= 5
        assert 0 <= float(breakdown.confidence) <= 1
        assert breakdown.severity in ['critical', 'high', 'medium', 'low']


class TestOpportunityEndpoints:
    """Test opportunity detection API endpoints"""
    
    def test_detect_opportunities_endpoint_exists(self):
        """Test that detect opportunities endpoint is defined"""
        from app.api.v1.endpoints.insights import detect_opportunities
        
        # Verify the function exists and is callable
        assert callable(detect_opportunities)
    
    def test_list_opportunities_returns_list(self):
        """Test that list opportunities returns mock data"""
        from app.api.v1.endpoints.insights import _get_mock_opportunities
        
        opportunities = _get_mock_opportunities()
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        # Check first opportunity structure
        opp = opportunities[0]
        assert hasattr(opp, 'insight_id')
        assert hasattr(opp, 'company_id')
        assert hasattr(opp, 'title')
        assert hasattr(opp, 'category')
        assert hasattr(opp, 'score_breakdown')
    
    def test_list_opportunities_with_company_filter(self):
        """Test opportunity filtering by company ID"""
        from app.api.v1.endpoints.insights import _get_mock_opportunities
        
        opportunities = _get_mock_opportunities(company_id="COMP001")
        
        for opp in opportunities:
            assert opp.company_id == "COMP001"
    
    def test_list_opportunities_with_category_filter(self):
        """Test opportunity filtering by category"""
        from app.api.v1.endpoints.insights import _get_mock_opportunities
        
        opportunities = _get_mock_opportunities(category="cost_reduction")
        
        for opp in opportunities:
            assert opp.category == "cost_reduction"
    
    def test_opportunity_score_breakdown_fields(self):
        """Test that opportunity score breakdown has all required fields"""
        from app.api.v1.endpoints.insights import _get_mock_opportunities
        
        opportunities = _get_mock_opportunities()
        opp = opportunities[0]
        breakdown = opp.score_breakdown
        
        assert hasattr(breakdown, 'potential_value')
        assert hasattr(breakdown, 'feasibility')
        assert hasattr(breakdown, 'timing_score')
        assert hasattr(breakdown, 'strategic_fit')
        assert hasattr(breakdown, 'final_score')
        assert hasattr(breakdown, 'priority')
        
        # Validate value ranges
        assert 0 <= float(breakdown.potential_value) <= 10
        assert 0 <= float(breakdown.feasibility) <= 1
        assert 0 <= float(breakdown.timing_score) <= 1
        assert 0 <= float(breakdown.strategic_fit) <= 1
        assert breakdown.priority in ['high', 'medium', 'low']


class TestRecommendationEndpoints:
    """Test recommendation API endpoints"""
    
    def test_list_recommendations_returns_list(self):
        """Test that list recommendations returns mock data"""
        from app.api.v1.endpoints.insights import _get_mock_recommendations
        
        recommendations = _get_mock_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check first recommendation structure
        rec = recommendations[0]
        assert hasattr(rec, 'recommendation_id')
        assert hasattr(rec, 'insight_id')
        assert hasattr(rec, 'action_title')
        assert hasattr(rec, 'category')
        assert hasattr(rec, 'priority')
        assert hasattr(rec, 'status')
    
    def test_list_recommendations_with_insight_filter(self):
        """Test recommendation filtering by insight ID"""
        from app.api.v1.endpoints.insights import _get_mock_recommendations
        
        recommendations = _get_mock_recommendations(insight_id=1)
        
        for rec in recommendations:
            assert rec.insight_id == 1
    
    def test_list_recommendations_with_status_filter(self):
        """Test recommendation filtering by status"""
        from app.api.v1.endpoints.insights import _get_mock_recommendations
        
        recommendations = _get_mock_recommendations(status="pending")
        
        for rec in recommendations:
            assert rec.status == "pending"
    
    def test_recommendation_fields(self):
        """Test that recommendation has all required fields"""
        from app.api.v1.endpoints.insights import _get_mock_recommendations
        
        recommendations = _get_mock_recommendations()
        rec = recommendations[0]
        
        assert hasattr(rec, 'action_description')
        assert hasattr(rec, 'responsible_role')
        assert hasattr(rec, 'estimated_effort')
        assert hasattr(rec, 'estimated_timeframe')
        assert hasattr(rec, 'expected_benefit')
        assert hasattr(rec, 'created_at')
        
        # Validate category values
        assert rec.category in ['immediate', 'short_term', 'medium_term', 'long_term']
        
        # Validate priority is positive
        assert rec.priority >= 1


class TestConversionFunctions:
    """Test helper conversion functions"""
    
    def test_risk_with_score_to_detected_risk(self):
        """Test conversion from RiskWithScore to DetectedRisk"""
        from app.api.v1.endpoints.insights import (
            _get_mock_risks,
            _risk_with_score_to_detected_risk
        )
        
        risks = _get_mock_risks()
        risk = risks[0]
        
        detected = _risk_with_score_to_detected_risk(risk)
        
        assert detected.company_id == risk.company_id
        assert detected.title == risk.title
        assert detected.description == risk.description
        assert detected.category == risk.category
        assert float(detected.probability) == float(risk.score_breakdown.probability)
        assert float(detected.impact) == float(risk.score_breakdown.impact)
        assert detected.severity_level == risk.score_breakdown.severity
    
    def test_opportunity_with_score_to_detected(self):
        """Test conversion from OpportunityWithScore to DetectedOpportunity"""
        from app.api.v1.endpoints.insights import (
            _get_mock_opportunities,
            _opportunity_with_score_to_detected
        )
        
        opportunities = _get_mock_opportunities()
        opp = opportunities[0]
        
        detected = _opportunity_with_score_to_detected(opp)
        
        assert detected.company_id == opp.company_id
        assert detected.title == opp.title
        assert detected.description == opp.description
        assert detected.category == opp.category
        assert float(detected.potential_value) == float(opp.score_breakdown.potential_value)
        assert float(detected.feasibility) == float(opp.score_breakdown.feasibility)
        assert detected.priority_level == opp.score_breakdown.priority


class TestMockLayerData:
    """Test mock Layer 3 data generation"""
    
    def test_mock_layer3_data_structure(self):
        """Test that mock Layer 3 data has correct structure"""
        from app.api.v1.endpoints.insights import _get_mock_layer3_data
        
        data = _get_mock_layer3_data()
        
        assert 'company_id' in data
        assert 'timestamp' in data
        assert 'operational_indicators' in data
        
        indicators = data['operational_indicators']
        
        # Check for expected indicators
        expected_indicators = [
            'OPS_POWER_RELIABILITY',
            'OPS_WATER_SUPPLY',
            'OPS_LOGISTICS_EFFICIENCY',
            'OPS_WORKFORCE_AVAILABILITY',
            'OPS_SUPPLIER_RELIABILITY',
        ]
        
        for indicator in expected_indicators:
            assert indicator in indicators
    
    def test_mock_layer3_data_values_in_range(self):
        """Test that mock Layer 3 data values are in valid range"""
        from app.api.v1.endpoints.insights import _get_mock_layer3_data
        
        data = _get_mock_layer3_data()
        indicators = data['operational_indicators']
        
        for indicator, value in indicators.items():
            assert 0 <= value <= 1, f"{indicator} value {value} out of range"


class TestDashboardEndpoint:
    """Test dashboard endpoint"""
    
    def test_dashboard_returns_summary(self):
        """Test that dashboard returns correct structure"""
        from app.api.v1.endpoints.insights import get_insights_dashboard
        
        import asyncio
        result = asyncio.run(get_insights_dashboard(company_id="COMP001"))
        
        assert 'company_id' in result
        assert 'generated_at' in result
        assert 'summary' in result
        assert 'top_risks' in result
        assert 'top_opportunities' in result
    
    def test_dashboard_summary_fields(self):
        """Test dashboard summary has expected fields"""
        from app.api.v1.endpoints.insights import get_insights_dashboard
        
        import asyncio
        result = asyncio.run(get_insights_dashboard(company_id="COMP001"))
        
        summary = result['summary']
        
        assert 'total_active_risks' in summary
        assert 'critical_risks' in summary
        assert 'high_risks' in summary
        assert 'total_opportunities' in summary
        assert 'high_priority_opportunities' in summary


class TestFullAnalysisEndpoint:
    """Test full analysis endpoint"""
    
    def test_full_analysis_endpoint_exists(self):
        """Test that full analysis endpoint is defined"""
        from app.api.v1.endpoints.insights import run_full_analysis
        
        # Verify the function exists and is callable
        assert callable(run_full_analysis)


class TestEndpointIntegration:
    """Integration tests for endpoint workflows"""
    
    def test_risk_detection_to_recommendation_workflow(self):
        """Test the complete workflow from risk detection to recommendations"""
        from app.api.v1.endpoints.insights import (
            _get_mock_risks,
            _risk_with_score_to_detected_risk,
            recommendation_engine
        )
        
        # Get a risk
        risks = _get_mock_risks()
        assert len(risks) > 0
        
        risk = risks[0]
        detected_risk = _risk_with_score_to_detected_risk(risk)
        
        # Generate recommendations
        rec_creates = recommendation_engine.generate_recommendations(detected_risk)
        
        # Should get recommendations
        assert len(rec_creates) > 0
        
        # Create action plan
        action_plan = recommendation_engine.create_action_plan(detected_risk, rec_creates)
        
        assert action_plan is not None
        assert len(action_plan.action_items) > 0
        
        # Generate narrative
        narrative = recommendation_engine.generate_narrative(detected_risk, rec_creates)
        
        assert narrative is not None
        assert narrative.headline is not None
        assert narrative.summary is not None
    
    def test_opportunity_detection_to_recommendation_workflow(self):
        """Test the complete workflow from opportunity detection to recommendations"""
        from app.api.v1.endpoints.insights import (
            _get_mock_opportunities,
            _opportunity_with_score_to_detected,
            recommendation_engine
        )
        
        # Get an opportunity
        opportunities = _get_mock_opportunities()
        assert len(opportunities) > 0
        
        opp = opportunities[0]
        detected_opp = _opportunity_with_score_to_detected(opp)
        
        # Generate recommendations
        rec_creates = recommendation_engine.generate_recommendations(detected_opp)
        
        # Should get recommendations (generic since no exact template match)
        assert len(rec_creates) > 0
        
        # Create action plan
        action_plan = recommendation_engine.create_action_plan(detected_opp, rec_creates)
        
        assert action_plan is not None
        assert len(action_plan.action_items) > 0
        
        # Generate narrative
        narrative = recommendation_engine.generate_narrative(detected_opp, rec_creates)
        
        assert narrative is not None
        assert narrative.headline is not None


# ==============================================================================
# Prioritization Endpoint Tests
# ==============================================================================

class TestPrioritizationEndpoints:
    """Test prioritization API endpoints"""
    
    def test_get_all_priorities_endpoint_exists(self):
        """Test that get_all_priorities endpoint is defined"""
        from app.api.v1.endpoints.insights import get_all_priorities
        
        assert callable(get_all_priorities)
    
    def test_get_top_priorities_endpoint_exists(self):
        """Test that get_top_priorities endpoint is defined"""
        from app.api.v1.endpoints.insights import get_top_priorities
        
        assert callable(get_top_priorities)
    
    def test_get_urgent_priorities_endpoint_exists(self):
        """Test that get_urgent_priorities endpoint is defined"""
        from app.api.v1.endpoints.insights import get_urgent_priorities
        
        assert callable(get_urgent_priorities)
    
    def test_get_priorities_by_category_endpoint_exists(self):
        """Test that get_priorities_by_category endpoint is defined"""
        from app.api.v1.endpoints.insights import get_priorities_by_category
        
        assert callable(get_priorities_by_category)
    
    def test_recalculate_priorities_endpoint_exists(self):
        """Test that recalculate_priorities endpoint is defined"""
        from app.api.v1.endpoints.insights import recalculate_priorities
        
        assert callable(recalculate_priorities)
    
    def test_mock_detected_risks_returns_list(self):
        """Test that mock detected risks helper returns data"""
        from app.api.v1.endpoints.insights import _get_mock_detected_risks
        
        risks = _get_mock_detected_risks("COMP001")
        
        assert isinstance(risks, list)
        assert len(risks) > 0
        
        # Check first risk structure
        risk = risks[0]
        assert hasattr(risk, 'risk_code')
        assert hasattr(risk, 'company_id')
        assert hasattr(risk, 'title')
        assert hasattr(risk, 'category')
        assert hasattr(risk, 'final_score')
    
    def test_mock_detected_opportunities_returns_list(self):
        """Test that mock detected opportunities helper returns data"""
        from app.api.v1.endpoints.insights import _get_mock_detected_opportunities
        
        opportunities = _get_mock_detected_opportunities("COMP001")
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        # Check first opportunity structure
        opp = opportunities[0]
        assert hasattr(opp, 'opportunity_code')
        assert hasattr(opp, 'company_id')
        assert hasattr(opp, 'title')
        assert hasattr(opp, 'category')
        assert hasattr(opp, 'final_score')
    
    def test_mock_company_profile_returns_dict(self):
        """Test that mock company profile helper returns data"""
        from app.api.v1.endpoints.insights import _get_mock_company_profile
        
        profile = _get_mock_company_profile("COMP001")
        
        assert isinstance(profile, dict)
        assert profile["company_id"] == "COMP001"
        assert "industry" in profile
        assert "strategic_priorities" in profile
    
    def test_insight_prioritizer_is_initialized(self):
        """Test that insight prioritizer is initialized in the module"""
        from app.api.v1.endpoints.insights import insight_prioritizer
        
        assert insight_prioritizer is not None
        assert hasattr(insight_prioritizer, 'prioritize')
        assert hasattr(insight_prioritizer, 'prioritize_all')
        assert hasattr(insight_prioritizer, 'get_top_priorities')


class TestPrioritizationWorkflow:
    """Test prioritization workflow integration"""
    
    def test_prioritization_integration(self):
        """Test complete prioritization workflow"""
        from app.api.v1.endpoints.insights import (
            _get_mock_detected_risks,
            _get_mock_detected_opportunities,
            _get_mock_company_profile,
            insight_prioritizer,
        )
        
        # Get test data
        risks = _get_mock_detected_risks("COMP001")
        opportunities = _get_mock_detected_opportunities("COMP001")
        company_profile = _get_mock_company_profile("COMP001")
        
        # Prioritize all
        all_priorities = insight_prioritizer.prioritize_all(
            risks=risks,
            opportunities=opportunities,
            company_profile=company_profile,
        )
        
        assert len(all_priorities) == len(risks) + len(opportunities)
        
        # Check priority structure
        for priority in all_priorities:
            assert hasattr(priority, 'insight_id')
            assert hasattr(priority, 'priority_rank')
            assert hasattr(priority, 'priority_score')
            assert hasattr(priority, 'actionability_score')
    
    def test_top_priorities_returns_limited_results(self):
        """Test top priorities returns correct number of results"""
        from app.api.v1.endpoints.insights import (
            _get_mock_detected_risks,
            _get_mock_detected_opportunities,
            _get_mock_company_profile,
            insight_prioritizer,
        )
        
        risks = _get_mock_detected_risks("COMP001")
        opportunities = _get_mock_detected_opportunities("COMP001")
        company_profile = _get_mock_company_profile("COMP001")
        
        top_priorities = insight_prioritizer.get_top_priorities(
            risks=risks,
            opportunities=opportunities,
            company_profile=company_profile,
            limit=3,
        )
        
        assert len(top_priorities.priorities) == 3
        assert top_priorities.total_active_insights == len(risks) + len(opportunities)
    
    def test_priorities_are_ranked_by_score(self):
        """Test that priorities are ranked by priority score"""
        from app.api.v1.endpoints.insights import (
            _get_mock_detected_risks,
            _get_mock_detected_opportunities,
            insight_prioritizer,
        )
        
        risks = _get_mock_detected_risks("COMP001")
        opportunities = _get_mock_detected_opportunities("COMP001")
        
        all_priorities = insight_prioritizer.prioritize_all(risks, opportunities)
        
        # Check descending order
        scores = [float(p.priority_score) for p in all_priorities]
        assert scores == sorted(scores, reverse=True)
    
    def test_both_risks_and_opportunities_in_priorities(self):
        """Test that both risks and opportunities appear in priorities"""
        from app.api.v1.endpoints.insights import (
            _get_mock_detected_risks,
            _get_mock_detected_opportunities,
            insight_prioritizer,
        )
        
        risks = _get_mock_detected_risks("COMP001")
        opportunities = _get_mock_detected_opportunities("COMP001")
        
        all_priorities = insight_prioritizer.prioritize_all(risks, opportunities)
        
        insight_types = set(p.insight_type for p in all_priorities)
        assert "risk" in insight_types
        assert "opportunity" in insight_types


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
