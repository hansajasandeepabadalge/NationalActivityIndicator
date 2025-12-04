"""
Layer 4: Recommendation Engine Tests

Tests for recommendation generation and action planning.
"""
import pytest
from datetime import datetime
from decimal import Decimal

from app.layer4.recommendation.engine import (
    RecommendationEngine,
    RecommendationTemplate
)
from app.layer4.schemas.risk_schemas import DetectedRisk
from app.layer4.schemas.opportunity_schemas import DetectedOpportunity


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def recommendation_engine():
    """Create recommendation engine instance"""
    return RecommendationEngine()


@pytest.fixture
def sample_risk():
    """Create a sample detected risk"""
    return DetectedRisk(
        definition_id=1,
        risk_code="RISK_SUPPLY_CHAIN",
        company_id="TEST_001",
        title="Supply Chain Disruption Risk",
        description="Significant supply chain disruption detected due to logistics constraints",
        category="supply_chain",
        severity_level="high",
        urgency=4,
        probability=Decimal("0.75"),
        impact=Decimal("0.80"),
        final_score=Decimal("7.5"),
        confidence=Decimal("0.85"),
        triggering_indicators={
            "OPS_SUPPLY_CHAIN": {"value": 45, "threshold": 50},
            "OPS_LOGISTICS_COST": {"value": 38, "threshold": 45}
        },
        detection_method="rule_based",
        reasoning="Supply chain indicator at 45 (below 50 threshold)"
    )


@pytest.fixture
def sample_opportunity():
    """Create a sample detected opportunity"""
    return DetectedOpportunity(
        opportunity_code="OPP_DEMAND_SURGE",
        company_id="TEST_001",
        title="Demand Surge Capture",
        description="High demand detected with capacity available to capture additional revenue",
        category="growth",
        potential_value=Decimal("8.0"),
        feasibility=Decimal("0.85"),
        timing_score=Decimal("0.90"),
        strategic_fit=Decimal("0.80"),
        final_score=Decimal("8.5"),
        priority_level="high",
        triggering_indicators={
            "OPS_DEMAND_LEVEL": {"value": 85, "threshold": 80}
        },
        detection_method="rule_based",
        reasoning="Strong demand with operational capacity",
        window_start=datetime.now(),
        window_end=datetime.now(),
        window_duration_days=30
    )


@pytest.fixture
def sample_cost_escalation_risk():
    """Create a cost escalation risk"""
    return DetectedRisk(
        definition_id=2,
        risk_code="RISK_COST_ESCALATION",
        company_id="TEST_002",
        title="Cost Escalation Risk",
        description="Rising operational costs detected across multiple categories",
        category="cost",
        severity_level="medium",
        urgency=3,
        probability=Decimal("0.65"),
        impact=Decimal("0.60"),
        final_score=Decimal("5.5"),
        confidence=Decimal("0.80"),
        triggering_indicators={
            "OPS_COST_PRESSURE": {"value": 75, "threshold": 70}
        },
        detection_method="rule_based",
        reasoning="Cost pressure exceeding threshold"
    )


@pytest.fixture
def sample_pricing_opportunity():
    """Create a pricing power opportunity"""
    return DetectedOpportunity(
        opportunity_code="OPP_PRICING_POWER",
        company_id="TEST_003",
        title="Premium Pricing Opportunity",
        description="Strong demand and market position enable price increases",
        category="market",
        potential_value=Decimal("6.5"),
        feasibility=Decimal("0.80"),
        timing_score=Decimal("0.75"),
        strategic_fit=Decimal("0.70"),
        final_score=Decimal("6.8"),
        priority_level="medium",
        triggering_indicators={
            "OPS_PRICING_POWER": {"value": 78, "threshold": 70}
        },
        detection_method="rule_based",
        reasoning="Strong pricing power indicators",
        window_start=datetime.now(),
        window_end=datetime.now(),
        window_duration_days=45
    )


# ==============================================================================
# Test RecommendationEngine
# ==============================================================================

class TestRecommendationEngine:
    """Tests for RecommendationEngine class"""
    
    def test_engine_initializes_with_templates(self, recommendation_engine):
        """Test that engine initializes with templates"""
        assert recommendation_engine is not None
        assert recommendation_engine.get_templates_count() >= 10
        print(f"✅ Engine initialized with {recommendation_engine.get_templates_count()} templates")
    
    def test_generate_recommendations_for_risk(self, recommendation_engine, sample_risk):
        """Test generating recommendations for a risk"""
        recommendations = recommendation_engine.generate_recommendations(sample_risk)
        
        assert len(recommendations) > 0
        
        # Check categories are present
        categories = set(r.category for r in recommendations)
        assert "immediate" in categories
        assert "short_term" in categories
        
        print(f"✅ Generated {len(recommendations)} recommendations for risk")
        for rec in recommendations[:3]:
            print(f"   - [{rec.category}] {rec.action_title[:50]}...")
    
    def test_generate_recommendations_for_opportunity(self, recommendation_engine, sample_opportunity):
        """Test generating recommendations for an opportunity"""
        recommendations = recommendation_engine.generate_recommendations(sample_opportunity)
        
        assert len(recommendations) > 0
        
        # Check categories
        categories = set(r.category for r in recommendations)
        assert "immediate" in categories or "short_term" in categories
        
        print(f"✅ Generated {len(recommendations)} recommendations for opportunity")
    
    def test_recommendations_have_required_fields(self, recommendation_engine, sample_risk):
        """Test that recommendations have all required fields"""
        recommendations = recommendation_engine.generate_recommendations(sample_risk)
        
        for rec in recommendations:
            assert rec.category in ["immediate", "short_term", "medium_term", "long_term"]
            assert rec.priority >= 1
            assert rec.action_title is not None
            assert rec.action_description is not None
            assert rec.responsible_role is not None
            assert rec.estimated_effort is not None
            assert rec.estimated_timeframe is not None
        
        print(f"✅ All recommendations have required fields")
    
    def test_recommendations_are_prioritized(self, recommendation_engine, sample_risk):
        """Test that recommendations are properly prioritized"""
        recommendations = recommendation_engine.generate_recommendations(sample_risk)
        
        priorities = [r.priority for r in recommendations]
        
        # Priorities should be sequential
        assert priorities == list(range(1, len(priorities) + 1))
        
        # Immediate actions should come first
        immediate_priorities = [r.priority for r in recommendations if r.category == "immediate"]
        if immediate_priorities and any(r.category == "short_term" for r in recommendations):
            short_term_priorities = [r.priority for r in recommendations if r.category == "short_term"]
            assert max(immediate_priorities) < min(short_term_priorities)
        
        print(f"✅ Recommendations properly prioritized")
    
    def test_generate_recommendations_for_cost_risk(self, recommendation_engine, sample_cost_escalation_risk):
        """Test recommendations for cost escalation risk"""
        recommendations = recommendation_engine.generate_recommendations(sample_cost_escalation_risk)
        
        assert len(recommendations) > 0
        
        # Should include cost-related actions
        action_texts = " ".join(r.action_description.lower() for r in recommendations)
        assert "cost" in action_texts or "spending" in action_texts or "budget" in action_texts
        
        print(f"✅ Generated cost-specific recommendations")
    
    def test_generate_recommendations_for_pricing_opportunity(self, recommendation_engine, sample_pricing_opportunity):
        """Test recommendations for pricing opportunity"""
        recommendations = recommendation_engine.generate_recommendations(sample_pricing_opportunity)
        
        assert len(recommendations) > 0
        
        # Should include pricing-related actions
        action_texts = " ".join(r.action_description.lower() for r in recommendations)
        assert "price" in action_texts or "pricing" in action_texts or "value" in action_texts
        
        print(f"✅ Generated pricing-specific recommendations")
    
    def test_generic_template_fallback(self, recommendation_engine):
        """Test that unknown risk codes get generic recommendations"""
        unknown_risk = DetectedRisk(
            definition_id=99,
            risk_code="RISK_UNKNOWN_TYPE",
            company_id="TEST",
            title="Unknown Risk",
            description="Some unknown risk type",
            category="other",
            severity_level="medium",
            urgency=3,
            probability=Decimal("0.5"),
            impact=Decimal("0.5"),
            final_score=Decimal("5.0"),
            confidence=Decimal("0.7"),
            triggering_indicators={},
            detection_method="rule_based",
            reasoning="Unknown pattern"
        )
        
        recommendations = recommendation_engine.generate_recommendations(unknown_risk)
        
        # Should still generate generic recommendations
        assert len(recommendations) > 0
        
        print(f"✅ Generic recommendations generated for unknown risk type")


class TestActionPlan:
    """Tests for action plan generation"""
    
    def test_create_action_plan_for_risk(self, recommendation_engine, sample_risk):
        """Test creating an action plan for a risk"""
        recommendations = recommendation_engine.generate_recommendations(sample_risk)
        action_plan = recommendation_engine.create_action_plan(sample_risk, recommendations)
        
        assert action_plan is not None
        assert len(action_plan.action_items) == len(recommendations)
        assert "Risk Mitigation" in action_plan.plan_title
        
        print(f"✅ Created action plan with {len(action_plan.action_items)} steps")
    
    def test_create_action_plan_for_opportunity(self, recommendation_engine, sample_opportunity):
        """Test creating an action plan for an opportunity"""
        recommendations = recommendation_engine.generate_recommendations(sample_opportunity)
        action_plan = recommendation_engine.create_action_plan(sample_opportunity, recommendations)
        
        assert action_plan is not None
        assert "Opportunity Capture" in action_plan.plan_title
        
        print(f"✅ Created opportunity action plan")
    
    def test_action_plan_has_steps(self, recommendation_engine, sample_risk):
        """Test that action plan has properly structured steps"""
        recommendations = recommendation_engine.generate_recommendations(sample_risk)
        action_plan = recommendation_engine.create_action_plan(sample_risk, recommendations)
        
        for step in action_plan.action_items:
            assert step.step_number > 0
            assert step.action is not None
            assert step.category in ["immediate", "short_term", "medium_term", "long_term"]
            assert step.timeframe is not None
            assert step.responsible is not None
            assert step.success_metric is not None
        
        print(f"✅ All action plan steps have required fields")
    
    def test_action_plan_has_dependencies(self, recommendation_engine, sample_risk):
        """Test that action plan steps have dependencies"""
        recommendations = recommendation_engine.generate_recommendations(sample_risk)
        action_plan = recommendation_engine.create_action_plan(sample_risk, recommendations)
        
        # Non-immediate steps should have dependencies
        non_immediate = [s for s in action_plan.action_items if s.category != "immediate"]
        
        # At least some should have dependencies
        has_dependencies = any(s.dependencies for s in non_immediate)
        assert has_dependencies or len(non_immediate) == 0
        
        print(f"✅ Action plan has proper dependencies")


class TestNarrativeContent:
    """Tests for narrative content generation"""
    
    def test_generate_narrative_for_risk(self, recommendation_engine, sample_risk):
        """Test generating narrative for a risk"""
        recommendations = recommendation_engine.generate_recommendations(sample_risk)
        narrative = recommendation_engine.generate_narrative(sample_risk, recommendations)
        
        assert narrative is not None
        assert narrative.insight_type == "risk"
        assert narrative.emoji in ["🔴", "🟠", "🟡", "🟢", "⚠️"]
        assert narrative.headline is not None
        assert narrative.summary is not None
        assert narrative.situation is not None
        assert narrative.why_it_matters is not None
        assert narrative.what_to_do is not None
        assert narrative.urgency_indicator in ["NOW", "TODAY", "THIS WEEK", "THIS MONTH"]
        
        print(f"✅ Generated risk narrative: {narrative.headline}")
    
    def test_generate_narrative_for_opportunity(self, recommendation_engine, sample_opportunity):
        """Test generating narrative for an opportunity"""
        recommendations = recommendation_engine.generate_recommendations(sample_opportunity)
        narrative = recommendation_engine.generate_narrative(sample_opportunity, recommendations)
        
        assert narrative is not None
        assert narrative.insight_type == "opportunity"
        assert narrative.emoji in ["🎯", "💡"]
        assert "Opportunity" in narrative.headline
        
        print(f"✅ Generated opportunity narrative: {narrative.headline}")
    
    def test_narrative_emoji_by_severity(self, recommendation_engine):
        """Test that emoji changes based on severity"""
        severities = ["critical", "high", "medium", "low"]
        urgency_map = {"critical": 5, "high": 4, "medium": 3, "low": 2}
        emojis = []
        
        for severity in severities:
            risk = DetectedRisk(
                risk_code="TEST",
                company_id="TEST",
                title="Test",
                description="Test",
                category="test",
                severity_level=severity,
                urgency=urgency_map[severity],
                probability=Decimal("0.5"),
                impact=Decimal("0.5"),
                final_score=Decimal("5.0"),
                confidence=Decimal("0.7"),
                triggering_indicators={},
                detection_method="rule_based",
                reasoning="Test"
            )
            recs = recommendation_engine.generate_recommendations(risk)
            narrative = recommendation_engine.generate_narrative(risk, recs)
            emojis.append(narrative.emoji)
        
        # Should have different emojis for different severities
        assert len(set(emojis)) > 1
        
        print(f"✅ Severity-based emojis: {dict(zip(severities, emojis))}")
    
    def test_narrative_urgency_by_severity(self, recommendation_engine):
        """Test that urgency indicator changes by severity"""
        risk_critical = DetectedRisk(
            risk_code="TEST",
            company_id="TEST",
            title="Test",
            description="Test",
            category="test",
            severity_level="critical",
            urgency=5,
            probability=Decimal("0.9"),
            impact=Decimal("0.9"),
            final_score=Decimal("9.0"),
            confidence=Decimal("0.95"),
            triggering_indicators={},
            detection_method="rule_based",
            reasoning="Test"
        )
        
        risk_low = DetectedRisk(
            risk_code="TEST",
            company_id="TEST",
            title="Test",
            description="Test",
            category="test",
            severity_level="low",
            urgency=2,
            probability=Decimal("0.3"),
            impact=Decimal("0.3"),
            final_score=Decimal("3.0"),
            confidence=Decimal("0.6"),
            triggering_indicators={},
            detection_method="rule_based",
            reasoning="Test"
        )
        
        recs_critical = recommendation_engine.generate_recommendations(risk_critical)
        recs_low = recommendation_engine.generate_recommendations(risk_low)
        
        narrative_critical = recommendation_engine.generate_narrative(risk_critical, recs_critical)
        narrative_low = recommendation_engine.generate_narrative(risk_low, recs_low)
        
        assert narrative_critical.urgency_indicator == "NOW"
        assert narrative_low.urgency_indicator == "THIS MONTH"
        
        print(f"✅ Urgency indicators: critical={narrative_critical.urgency_indicator}, low={narrative_low.urgency_indicator}")


class TestRecommendationIntegration:
    """Integration tests for recommendation system"""
    
    def test_full_recommendation_pipeline(self, recommendation_engine, sample_risk):
        """Test complete recommendation pipeline"""
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(sample_risk)
        assert len(recommendations) > 0
        
        # Create action plan
        action_plan = recommendation_engine.create_action_plan(sample_risk, recommendations)
        assert action_plan is not None
        
        # Generate narrative
        narrative = recommendation_engine.generate_narrative(sample_risk, recommendations)
        assert narrative is not None
        
        print(f"\n📊 Full Pipeline Results:")
        print(f"   Risk: {sample_risk.title}")
        print(f"   Recommendations: {len(recommendations)}")
        print(f"   Action Steps: {len(action_plan.action_items)}")
        print(f"   Narrative: {narrative.headline}")
        print(f"   Urgency: {narrative.urgency_indicator}")
        print(f"✅ Full pipeline completed")
    
    def test_multiple_insight_types(self, recommendation_engine, sample_risk, sample_opportunity):
        """Test recommendations for multiple insight types"""
        risk_recs = recommendation_engine.generate_recommendations(sample_risk)
        opp_recs = recommendation_engine.generate_recommendations(sample_opportunity)
        
        # Both should generate recommendations
        assert len(risk_recs) > 0
        assert len(opp_recs) > 0
        
        # Content should be different
        risk_actions = set(r.action_title for r in risk_recs)
        opp_actions = set(r.action_title for r in opp_recs)
        
        assert risk_actions != opp_actions
        
        print(f"✅ Different recommendations for risk vs opportunity")


# ==============================================================================
# Run Tests
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
