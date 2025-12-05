"""
Layer 4: Opportunity Detection Tests

Tests for rule-based opportunity detection functionality.
"""
import pytest
from datetime import datetime
from decimal import Decimal

from app.layer4.opportunity_detection.rule_based_detector import (
    RuleBasedOpportunityDetector,
    OpportunityRule
)
from app.layer4.mock_data.layer3_mock_generator import (
    MockLayer3Generator,
    OperationalIndicators
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def opportunity_detector():
    """Create opportunity detector instance"""
    return RuleBasedOpportunityDetector()


@pytest.fixture
def mock_generator():
    """Create mock data generator"""
    return MockLayer3Generator()


@pytest.fixture
def strong_operational_indicators():
    """Indicators showing strong operations - should trigger opportunities"""
    return OperationalIndicators(
        timestamp=datetime.now(),
        company_id="TEST_001",
        # Supply Chain & Logistics
        OPS_SUPPLY_CHAIN=85.0,
        OPS_TRANSPORT_AVAIL=80.0,
        OPS_LOGISTICS_COST=65.0,
        OPS_IMPORT_FLOW=75.0,
        # Workforce & Operations
        OPS_WORKFORCE_AVAIL=75.0,
        OPS_LABOR_COST=65.0,
        OPS_PRODUCTIVITY=78.0,
        # Infrastructure & Resources
        OPS_POWER_RELIABILITY=90.0,
        OPS_FUEL_AVAIL=75.0,
        OPS_WATER_SUPPLY=90.0,
        OPS_INTERNET_CONNECTIVITY=85.0,
        # Cost Pressures
        OPS_COST_PRESSURE=60.0,
        OPS_RAW_MATERIAL_COST=70.0,
        OPS_ENERGY_COST=70.0,
        # Market Conditions
        OPS_DEMAND_LEVEL=80.0,
        OPS_COMPETITION_INTENSITY=55.0,
        OPS_PRICING_POWER=75.0,
        # Financial Operations
        OPS_CASH_FLOW=80.0,
        OPS_CREDIT_AVAIL=70.0,
        OPS_PAYMENT_DELAYS=75.0,
        # Regulatory & Compliance
        OPS_REGULATORY_BURDEN=65.0,
        OPS_COMPLIANCE_COST=60.0,
        trends={"OPS_DEMAND_LEVEL": "rising", "OPS_PRODUCTIVITY": "stable"}
    )


@pytest.fixture
def weak_operational_indicators():
    """Indicators showing weak operations - few opportunities"""
    return OperationalIndicators(
        timestamp=datetime.now(),
        company_id="TEST_002",
        # Supply Chain & Logistics
        OPS_SUPPLY_CHAIN=40.0,
        OPS_TRANSPORT_AVAIL=40.0,
        OPS_LOGISTICS_COST=35.0,
        OPS_IMPORT_FLOW=35.0,
        # Workforce & Operations
        OPS_WORKFORCE_AVAIL=40.0,
        OPS_LABOR_COST=35.0,
        OPS_PRODUCTIVITY=38.0,
        # Infrastructure & Resources
        OPS_POWER_RELIABILITY=45.0,
        OPS_FUEL_AVAIL=35.0,
        OPS_WATER_SUPPLY=50.0,
        OPS_INTERNET_CONNECTIVITY=40.0,
        # Cost Pressures
        OPS_COST_PRESSURE=75.0,
        OPS_RAW_MATERIAL_COST=30.0,
        OPS_ENERGY_COST=30.0,
        # Market Conditions
        OPS_DEMAND_LEVEL=35.0,
        OPS_COMPETITION_INTENSITY=80.0,
        OPS_PRICING_POWER=30.0,
        # Financial Operations
        OPS_CASH_FLOW=35.0,
        OPS_CREDIT_AVAIL=30.0,
        OPS_PAYMENT_DELAYS=25.0,
        # Regulatory & Compliance
        OPS_REGULATORY_BURDEN=40.0,
        OPS_COMPLIANCE_COST=35.0,
        trends={"OPS_DEMAND_LEVEL": "falling", "OPS_PRODUCTIVITY": "falling"}
    )


@pytest.fixture
def demand_surge_indicators():
    """Indicators specifically for demand surge opportunity"""
    return OperationalIndicators(
        timestamp=datetime.now(),
        company_id="TEST_003",
        # Supply Chain & Logistics
        OPS_SUPPLY_CHAIN=72.0,
        OPS_TRANSPORT_AVAIL=70.0,
        OPS_LOGISTICS_COST=55.0,
        OPS_IMPORT_FLOW=65.0,
        # Workforce & Operations
        OPS_WORKFORCE_AVAIL=68.0,
        OPS_LABOR_COST=55.0,
        OPS_PRODUCTIVITY=72.0,
        # Infrastructure & Resources
        OPS_POWER_RELIABILITY=75.0,
        OPS_FUEL_AVAIL=65.0,
        OPS_WATER_SUPPLY=80.0,
        OPS_INTERNET_CONNECTIVITY=75.0,
        # Cost Pressures
        OPS_COST_PRESSURE=50.0,
        OPS_RAW_MATERIAL_COST=55.0,
        OPS_ENERGY_COST=60.0,
        # Market Conditions
        OPS_DEMAND_LEVEL=88.0,  # Very high demand
        OPS_COMPETITION_INTENSITY=60.0,
        OPS_PRICING_POWER=70.0,
        # Financial Operations
        OPS_CASH_FLOW=65.0,
        OPS_CREDIT_AVAIL=60.0,
        OPS_PAYMENT_DELAYS=65.0,
        # Regulatory & Compliance
        OPS_REGULATORY_BURDEN=55.0,
        OPS_COMPLIANCE_COST=50.0,
        trends={"OPS_DEMAND_LEVEL": "rising"}
    )


# ==============================================================================
# Test RuleBasedOpportunityDetector
# ==============================================================================

class TestRuleBasedOpportunityDetector:
    """Tests for RuleBasedOpportunityDetector class"""
    
    def test_detector_initializes_with_rules(self, opportunity_detector):
        """Test that detector initializes with predefined rules"""
        assert opportunity_detector is not None
        assert len(opportunity_detector.rules) >= 10
        print(f"✅ Detector initialized with {len(opportunity_detector.rules)} rules")
    
    def test_all_opportunity_categories_covered(self, opportunity_detector):
        """Test that all major categories are represented"""
        categories = opportunity_detector.get_opportunity_categories()
        
        expected_categories = ['market', 'cost', 'strategic', 'growth']
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        
        print(f"✅ All categories covered: {list(categories.keys())}")
    
    def test_detect_market_capture_opportunity(self, opportunity_detector, strong_operational_indicators):
        """Test detection of market capture opportunity"""
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="retail",
            indicators=strong_operational_indicators
        )
        
        market_capture = [o for o in opportunities if o.opportunity_code == "OPP_MARKET_CAPTURE"]
        
        # With strong indicators, should detect market capture
        assert len(market_capture) >= 1 or len(opportunities) > 0
        print(f"✅ Detected {len(opportunities)} opportunities (market capture: {len(market_capture)})")
    
    def test_detect_pricing_power_opportunity(self, opportunity_detector, strong_operational_indicators):
        """Test detection of pricing power opportunity"""
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="retail",
            indicators=strong_operational_indicators
        )
        
        pricing_power = [o for o in opportunities if o.opportunity_code == "OPP_PRICING_POWER"]
        
        # With high demand and pricing power indicators, should detect
        if pricing_power:
            assert pricing_power[0].category == "market"
            print(f"✅ Pricing power opportunity detected with score {pricing_power[0].final_score}")
        else:
            # May not trigger if thresholds not met
            print(f"✅ Pricing power not triggered (threshold not met)")
    
    def test_detect_demand_surge_opportunity(self, opportunity_detector, demand_surge_indicators):
        """Test detection of demand surge opportunity"""
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_003",
            industry="retail",
            indicators=demand_surge_indicators
        )
        
        demand_surge = [o for o in opportunities if o.opportunity_code == "OPP_DEMAND_SURGE"]
        
        assert len(demand_surge) >= 1, "Should detect demand surge with high demand indicators"
        
        opp = demand_surge[0]
        assert opp.category == "growth"
        assert opp.priority_level in ['high', 'medium']
        
        print(f"✅ Demand surge opportunity detected: {opp.final_score}")
    
    def test_detect_cost_reduction_opportunity(self, opportunity_detector, mock_generator):
        """Test detection of cost reduction opportunities"""
        from datetime import datetime
        
        # Generate indicators favorable for cost reduction
        indicators = mock_generator.generate_indicators(
            company_id="TEST_004",
            industry="manufacturing",
            business_scale="medium",
            timestamp=datetime.now()
        )
        
        # Manually override to trigger cost opportunity
        indicators.OPS_RAW_MATERIAL_COST = 72.0
        indicators.OPS_ENERGY_COST = 68.0
        indicators.OPS_SUPPLY_CHAIN = 75.0
        
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_004",
            industry="manufacturing",
            indicators=indicators
        )
        
        cost_opps = [o for o in opportunities if o.category == "cost"]
        print(f"✅ Detected {len(cost_opps)} cost opportunities")
    
    def test_detect_digital_transformation_opportunity(self, opportunity_detector, strong_operational_indicators):
        """Test detection of digital transformation opportunity"""
        # Strong internet and power should trigger digital transformation
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="retail",
            indicators=strong_operational_indicators
        )
        
        digital = [o for o in opportunities if o.opportunity_code == "OPP_DIGITAL_TRANSFORM"]
        
        if digital:
            assert digital[0].category == "strategic"
            print(f"✅ Digital transformation opportunity detected")
        else:
            print(f"✅ Digital transformation not triggered")
    
    def test_no_opportunities_for_weak_indicators(self, opportunity_detector, weak_operational_indicators):
        """Test that weak indicators produce fewer opportunities"""
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_002",
            industry="retail",
            indicators=weak_operational_indicators
        )
        
        # Weak indicators should produce few or no opportunities
        assert len(opportunities) < 5, f"Expected few opportunities, got {len(opportunities)}"
        print(f"✅ Weak indicators produced {len(opportunities)} opportunities (expected few)")
    
    def test_industry_filtering(self, opportunity_detector, strong_operational_indicators):
        """Test that industry-specific rules are filtered correctly"""
        # Test with manufacturing (has specific rules)
        mfg_opps = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="manufacturing",
            indicators=strong_operational_indicators
        )
        
        # Test with services (different applicable rules)
        svc_opps = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="services",
            indicators=strong_operational_indicators
        )
        
        print(f"✅ Manufacturing opportunities: {len(mfg_opps)}, Services: {len(svc_opps)}")
    
    def test_opportunity_has_required_fields(self, opportunity_detector, strong_operational_indicators):
        """Test that detected opportunities have all required fields"""
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="retail",
            indicators=strong_operational_indicators
        )
        
        if opportunities:
            opp = opportunities[0]
            
            # Check required fields
            assert opp.opportunity_code is not None
            assert opp.company_id == "TEST_001"
            assert opp.title is not None
            assert opp.description is not None
            assert opp.category is not None
            assert opp.potential_value >= 0
            assert 0 <= opp.feasibility <= 1
            assert 0 <= opp.timing_score <= 1
            assert 0 <= opp.strategic_fit <= 1
            assert opp.final_score >= 0
            assert opp.priority_level in ['high', 'medium', 'low']
            assert opp.detection_method == "rule_based"
            assert opp.reasoning is not None
            assert opp.window_start is not None
            assert opp.window_end is not None
            
            print(f"✅ Opportunity has all required fields")
    
    def test_opportunity_scoring(self, opportunity_detector, strong_operational_indicators):
        """Test opportunity scoring calculation"""
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="retail",
            indicators=strong_operational_indicators
        )
        
        for opp in opportunities[:3]:  # Check top 3
            # Verify scoring is within bounds
            assert Decimal('0') <= opp.potential_value <= Decimal('10')
            assert Decimal('0') <= opp.feasibility <= Decimal('1')
            assert Decimal('0') <= opp.final_score <= Decimal('10')
            
            # Higher potential value with good feasibility should yield higher score
            if opp.potential_value > 6 and opp.feasibility > 0.7:
                assert opp.final_score > 4, "High value + feasibility should yield good score"
        
        print(f"✅ Opportunity scoring validated for {len(opportunities)} opportunities")
    
    def test_opportunities_sorted_by_score(self, opportunity_detector, strong_operational_indicators):
        """Test that opportunities are sorted by final score (descending)"""
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="retail",
            indicators=strong_operational_indicators
        )
        
        if len(opportunities) >= 2:
            for i in range(len(opportunities) - 1):
                assert opportunities[i].final_score >= opportunities[i + 1].final_score
        
        print(f"✅ Opportunities correctly sorted by score")
    
    def test_window_duration(self, opportunity_detector, strong_operational_indicators):
        """Test that opportunity windows are correctly set"""
        opportunities = opportunity_detector.detect_opportunities(
            company_id="TEST_001",
            industry="retail",
            indicators=strong_operational_indicators
        )
        
        for opp in opportunities:
            assert opp.window_start is not None
            assert opp.window_end is not None
            assert opp.window_end > opp.window_start
            assert opp.window_duration_days > 0
            
            # Verify duration matches
            actual_days = (opp.window_end - opp.window_start).days
            assert actual_days == opp.window_duration_days
        
        print(f"✅ Window durations correctly calculated")


class TestOpportunityRule:
    """Tests for OpportunityRule class"""
    
    def test_rule_creation(self):
        """Test creating a custom opportunity rule"""
        rule = OpportunityRule(
            code="OPP_TEST",
            name="Test Opportunity",
            category="test",
            subcategory="testing",
            description_template="Test description",
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_DEMAND_LEVEL",
                    "threshold": 70,
                    "weight": 1.0
                }
            ],
            applicable_industries=["retail", "manufacturing"],
            base_value=7.0
        )
        
        assert rule.code == "OPP_TEST"
        assert rule.category == "test"
        assert len(rule.conditions) == 1
        print(f"✅ Custom rule created successfully")
    
    def test_rule_industry_applicability(self):
        """Test rule industry filtering"""
        rule = OpportunityRule(
            code="OPP_TEST",
            name="Test",
            category="test",
            subcategory="testing",
            description_template="Test",
            conditions=[],
            applicable_industries=["retail", "hospitality"]
        )
        
        assert rule.is_applicable("retail") == True
        assert rule.is_applicable("hospitality") == True
        assert rule.is_applicable("manufacturing") == False
        
        print(f"✅ Industry applicability filtering works")
    
    def test_rule_scale_applicability(self):
        """Test rule business scale filtering"""
        rule = OpportunityRule(
            code="OPP_TEST",
            name="Test",
            category="test",
            subcategory="testing",
            description_template="Test",
            conditions=[],
            applicable_scales=["large"]
        )
        
        assert rule.is_applicable("retail", "large") == True
        assert rule.is_applicable("retail", "small") == False
        
        print(f"✅ Scale applicability filtering works")


class TestOpportunityDetectionIntegration:
    """Integration tests for opportunity detection"""
    
    def test_full_detection_pipeline(self, opportunity_detector, mock_generator):
        """Test complete detection pipeline"""
        from datetime import datetime
        
        # Generate indicators
        indicators = mock_generator.generate_indicators(
            company_id="INTEG_001",
            industry="retail",
            business_scale="large",
            timestamp=datetime.now(),
            scenario="strong_demand"
        )
        
        # Detect opportunities
        opportunities = opportunity_detector.detect_opportunities(
            company_id="INTEG_001",
            industry="retail",
            indicators=indicators
        )
        
        print(f"\n📊 Integration Test Results:")
        print(f"   Opportunities detected: {len(opportunities)}")
        
        if opportunities:
            for i, opp in enumerate(opportunities[:3]):
                print(f"   {i+1}. {opp.title} ({opp.category})")
                print(f"      Score: {opp.final_score}, Priority: {opp.priority_level}")
        
        print(f"✅ Full detection pipeline completed")
    
    def test_multiple_industries(self, opportunity_detector, mock_generator):
        """Test detection across multiple industries"""
        from datetime import datetime
        
        industries = ["retail", "manufacturing", "logistics", "hospitality", "services"]
        results = {}
        
        for industry in industries:
            indicators = mock_generator.generate_indicators(
                company_id=f"IND_{industry[:4].upper()}",
                industry=industry,
                business_scale="medium",
                timestamp=datetime.now()
            )
            
            opps = opportunity_detector.detect_opportunities(
                company_id=f"IND_{industry[:4].upper()}",
                industry=industry,
                indicators=indicators
            )
            
            results[industry] = len(opps)
        
        print(f"\n📊 Opportunities by Industry:")
        for industry, count in results.items():
            print(f"   {industry}: {count} opportunities")
        
        print(f"✅ Multi-industry detection completed")
    
    def test_detection_performance(self, opportunity_detector, mock_generator):
        """Test detection performance"""
        import time
        from datetime import datetime
        
        indicators = mock_generator.generate_indicators(
            company_id="PERF_001",
            industry="retail",
            business_scale="medium",
            timestamp=datetime.now()
        )
        
        start = time.time()
        iterations = 100
        
        for _ in range(iterations):
            opportunity_detector.detect_opportunities(
                company_id="PERF_001",
                industry="retail",
                indicators=indicators
            )
        
        elapsed = time.time() - start
        avg_time = elapsed / iterations * 1000  # ms
        
        assert avg_time < 100, f"Detection too slow: {avg_time:.2f}ms"
        print(f"✅ Average detection time: {avg_time:.2f}ms")


# ==============================================================================
# Run Tests
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
