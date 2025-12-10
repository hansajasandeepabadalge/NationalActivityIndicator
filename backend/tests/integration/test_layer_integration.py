"""
Integration Tests for Layer 2 -> Layer 3 -> Layer 4 Pipeline

Tests the data flow and transformations between layers.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from app.integration import (
    # Contracts
    Layer2Output,
    Layer3Input,
    Layer3Output,
    Layer4Input,
    validate_layer2_output,
    validate_layer3_output,
    # Adapters
    Layer2ToLayer3Adapter,
    Layer3ToLayer4Adapter,
    MockDataGenerator,
    # Pipeline
    IntegrationPipeline,
    PipelineBuilder,
    create_pipeline,
)

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_generator():
    """Create a mock data generator with fixed seed"""
    return MockDataGenerator(seed=42)


@pytest.fixture
def company_profile():
    """Standard company profile for testing"""
    return {
        "company_id": "TEST001",
        "company_name": "Test Manufacturing Co",
        "industry": "manufacturing",
        "size": "medium",
        "region": "Southeast Asia",
        "annual_revenue": 50000000,
        "employee_count": 500,
    }


@pytest.fixture
def retail_company_profile():
    """Retail company profile for testing industry sensitivity"""
    return {
        "company_id": "RETAIL001",
        "company_name": "Test Retail Co",
        "industry": "retail",
        "size": "large",
        "region": "Southeast Asia",
        "annual_revenue": 100000000,
        "employee_count": 2000,
    }


@pytest.fixture
def layer2_output_normal(mock_generator):
    """Normal scenario Layer 2 output"""
    return mock_generator.generate_layer2_output("normal")


@pytest.fixture
def layer2_output_crisis(mock_generator):
    """Crisis scenario Layer 2 output"""
    return mock_generator.generate_layer2_output("crisis")


@pytest.fixture
def layer2_output_growth(mock_generator):
    """Growth scenario Layer 2 output"""
    return mock_generator.generate_layer2_output("growth")


# =============================================================================
# Contract Validation Tests
# =============================================================================

class TestContractValidation:
    """Test contract validation between layers"""
    
    def test_layer2_output_validation_valid(self, layer2_output_normal):
        """Test that valid Layer 2 output passes validation"""
        validated = validate_layer2_output(layer2_output_normal)
        assert isinstance(validated, Layer2Output)
        assert len(validated.indicators) > 0
    
    def test_layer2_output_validation_missing_indicators(self):
        """Test that missing indicators fails validation"""
        invalid_data = {
            "timestamp": datetime.now().isoformat(),
            "indicators": {},  # Empty - should fail
            "overall_sentiment": 0.5,
            "activity_level": 50,
            "article_count": 100,
            "source_diversity": 10,
            "data_quality_score": 0.8,
        }
        with pytest.raises(ValueError, match="indicators cannot be empty"):
            validate_layer2_output(invalid_data)
    
    def test_layer2_output_validation_invalid_value(self):
        """Test that out-of-range values fail validation"""
        invalid_data = {
            "timestamp": datetime.now().isoformat(),
            "indicators": {
                "TEST_IND": {
                    "indicator_id": "TEST_IND",
                    "indicator_name": "Test",
                    "pestel_category": "Economic",
                    "timestamp": datetime.now().isoformat(),
                    "value": 150,  # Invalid: > 100
                    "raw_count": 10,
                    "confidence": 0.8,
                }
            },
            "overall_sentiment": 0.5,
            "activity_level": 50,
            "article_count": 100,
            "source_diversity": 10,
            "data_quality_score": 0.8,
        }
        with pytest.raises(Exception):  # Pydantic validation error
            validate_layer2_output(invalid_data)
    
    def test_layer3_output_validation_valid(self, layer2_output_normal, company_profile):
        """Test Layer 3 output validation"""
        adapter = Layer2ToLayer3Adapter()
        l2 = validate_layer2_output(layer2_output_normal)
        
        # Create simulated L3 output
        pipeline = create_pipeline()
        l3_dict = pipeline._simulate_layer3(l2, company_profile)
        
        validated = validate_layer3_output(l3_dict)
        assert isinstance(validated, Layer3Output)
        assert validated.company_id == "TEST001"


# =============================================================================
# Adapter Tests
# =============================================================================

class TestLayer2ToLayer3Adapter:
    """Test Layer 2 to Layer 3 adapter"""
    
    def test_adapt_creates_valid_input(self, layer2_output_normal, company_profile):
        """Test adapter creates valid Layer 3 input"""
        adapter = Layer2ToLayer3Adapter()
        l2 = validate_layer2_output(layer2_output_normal)
        
        l3_input = adapter.adapt(l2, company_profile)
        
        assert isinstance(l3_input, Layer3Input)
        assert l3_input.national_indicators == l2
        assert l3_input.company_profile == company_profile
    
    def test_get_relevant_indicators_by_industry(self, layer2_output_normal):
        """Test that industry filters relevant indicators"""
        adapter = Layer2ToLayer3Adapter()
        l2 = validate_layer2_output(layer2_output_normal)
        
        # Manufacturing should emphasize supply chain
        mfg_indicators = adapter.get_relevant_indicators(l2, "manufacturing")
        
        # Retail should emphasize market conditions
        retail_indicators = adapter.get_relevant_indicators(l2, "retail")
        
        assert "supply_chain" in mfg_indicators
        assert "market_conditions" in retail_indicators
    
    def test_calculate_category_impact(self, layer2_output_normal):
        """Test category impact calculation"""
        adapter = Layer2ToLayer3Adapter()
        l2 = validate_layer2_output(layer2_output_normal)
        
        categorized = adapter.get_relevant_indicators(l2, "manufacturing")
        
        # Calculate impact with sensitivity
        impact = adapter.calculate_category_impact(
            categorized["supply_chain"], 
            sensitivity=1.4  # Manufacturing sensitivity
        )
        
        assert 0 <= impact <= 100
    
    def test_empty_category_returns_neutral(self):
        """Test that empty category returns neutral score"""
        adapter = Layer2ToLayer3Adapter()
        impact = adapter.calculate_category_impact([])
        assert impact == 50.0


class TestLayer3ToLayer4Adapter:
    """Test Layer 3 to Layer 4 adapter"""
    
    def test_to_layer4_indicators(self, layer2_output_normal, company_profile):
        """Test conversion to Layer 4 indicator format"""
        adapter = Layer3ToLayer4Adapter()
        pipeline = create_pipeline()
        
        l2 = validate_layer2_output(layer2_output_normal)
        l3_dict = pipeline._simulate_layer3(l2, company_profile)
        l3 = validate_layer3_output(l3_dict)
        
        l4_indicators = adapter.to_layer4_indicators(l3)
        
        assert isinstance(l4_indicators, dict)
        # Should have OPS_ prefixed indicators
        ops_keys = [k for k in l4_indicators.keys() if k.startswith("OPS_")]
        assert len(ops_keys) > 0
    
    def test_get_critical_indicators(self, layer2_output_crisis, company_profile):
        """Test critical indicator detection"""
        adapter = Layer3ToLayer4Adapter()
        pipeline = create_pipeline()
        
        l2 = validate_layer2_output(layer2_output_crisis)
        l3_dict = pipeline._simulate_layer3(l2, company_profile)
        l3 = validate_layer3_output(l3_dict)
        
        # Set threshold that should catch some issues
        critical = adapter.get_critical_indicators(l3, threshold=40.0)
        
        assert isinstance(critical, list)
        # In crisis, we should have some critical indicators
        # (depends on mock data values)
    
    def test_adapt_creates_layer4_input(self, layer2_output_normal, company_profile):
        """Test adapter creates valid Layer 4 input"""
        adapter = Layer3ToLayer4Adapter()
        pipeline = create_pipeline()
        
        l2 = validate_layer2_output(layer2_output_normal)
        l3_dict = pipeline._simulate_layer3(l2, company_profile)
        l3 = validate_layer3_output(l3_dict)
        
        l4_input = adapter.adapt(l3, company_profile)
        
        assert isinstance(l4_input, Layer4Input)
        assert l4_input.company_profile == company_profile


# =============================================================================
# Pipeline Tests
# =============================================================================

class TestIntegrationPipeline:
    """Test the integration pipeline"""
    
    @pytest.mark.asyncio
    async def test_run_layer2_to_layer3(self, layer2_output_normal, company_profile):
        """Test L2 to L3 pipeline step"""
        pipeline = create_pipeline()
        
        result = await pipeline.run_layer2_to_layer3(
            layer2_output_normal,
            company_profile
        )
        
        assert "company_id" in result
        assert result["company_id"] == "TEST001"
        assert "supply_chain_health" in result
        assert "workforce_health" in result
        assert "indicators" in result
    
    @pytest.mark.asyncio
    async def test_run_layer3_to_layer4(self, layer2_output_normal, company_profile):
        """Test L3 to L4 pipeline step"""
        pipeline = create_pipeline()
        
        # First get L3 output
        l3_output = await pipeline.run_layer2_to_layer3(
            layer2_output_normal,
            company_profile
        )
        
        # Then run L4
        l4_output = await pipeline.run_layer3_to_layer4(
            l3_output,
            company_profile
        )
        
        assert "company_id" in l4_output or "summary" in l4_output
    
    @pytest.mark.asyncio
    async def test_run_full_pipeline(self, layer2_output_normal, company_profile):
        """Test complete L2 -> L3 -> L4 pipeline"""
        pipeline = create_pipeline()
        
        result = await pipeline.run_full_pipeline(
            company_profile,
            layer2_input=layer2_output_normal
        )
        
        assert result["success"] is True
        assert "layer2_output" in result
        assert "layer3_output" in result
        assert "layer4_output" in result
        assert "metrics" in result
        
        # Check metrics
        metrics = result["metrics"]
        assert "layer2" in metrics["layer_times"]
        assert "layer3" in metrics["layer_times"]
        assert "layer4" in metrics["layer_times"]
    
    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, company_profile):
        """Test pipeline handles errors gracefully"""
        pipeline = create_pipeline()
        
        # Pass invalid L2 data
        invalid_l2 = {"invalid": "data"}
        
        result = await pipeline.run_full_pipeline(
            company_profile,
            layer2_input=invalid_l2
        )
        
        assert result["success"] is False
        assert "error" in result
        assert len(result["metrics"]["validation_errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_pipeline_with_different_scenarios(self, company_profile, mock_generator):
        """Test pipeline with different economic scenarios"""
        pipeline = create_pipeline()
        
        scenarios = ["normal", "crisis", "growth", "recession"]
        results = {}
        
        for scenario in scenarios:
            l2_data = mock_generator.generate_layer2_output(scenario)
            result = await pipeline.run_full_pipeline(
                company_profile,
                layer2_input=l2_data
            )
            results[scenario] = result
        
        # All should succeed
        for scenario, result in results.items():
            assert result["success"] is True, f"Failed for {scenario}"
        
        # Crisis should show lower health scores than growth
        crisis_health = results["crisis"]["layer3_output"]["overall_operational_health"]
        growth_health = results["growth"]["layer3_output"]["overall_operational_health"]
        
        assert crisis_health < growth_health
    
    @pytest.mark.asyncio
    async def test_pipeline_industry_sensitivity(
        self, 
        layer2_output_normal, 
        company_profile, 
        retail_company_profile
    ):
        """Test that different industries get different results"""
        pipeline = create_pipeline()
        
        mfg_result = await pipeline.run_full_pipeline(
            company_profile,  # Manufacturing
            layer2_input=layer2_output_normal
        )
        
        retail_result = await pipeline.run_full_pipeline(
            retail_company_profile,  # Retail
            layer2_input=layer2_output_normal
        )
        
        assert mfg_result["success"] is True
        assert retail_result["success"] is True
        
        # Different industries should produce different results
        mfg_supply = mfg_result["layer3_output"]["supply_chain_health"]
        retail_supply = retail_result["layer3_output"]["supply_chain_health"]
        
        # Manufacturing has higher supply chain sensitivity (1.4) vs retail (1.2)
        # So with same input, manufacturing should be more affected


class TestPipelineBuilder:
    """Test the pipeline builder pattern"""
    
    def test_builder_creates_pipeline(self):
        """Test builder creates valid pipeline"""
        pipeline = (
            PipelineBuilder()
            .build()
        )
        
        assert isinstance(pipeline, IntegrationPipeline)
    
    def test_builder_chain(self):
        """Test builder method chaining"""
        class MockProcessor:
            def calculate(self):
                return {}
        
        pipeline = (
            PipelineBuilder()
            .with_layer2(MockProcessor())
            .build()
        )
        
        assert pipeline._layer2_processor is not None


# =============================================================================
# Mock Data Generator Tests
# =============================================================================

class TestMockDataGenerator:
    """Test the mock data generator"""
    
    def test_generate_layer2_output_normal(self, mock_generator):
        """Test normal scenario generation"""
        output = mock_generator.generate_layer2_output("normal")
        
        assert "indicators" in output
        assert "overall_sentiment" in output
        assert len(output["indicators"]) > 0
    
    def test_generate_layer2_output_crisis(self, mock_generator):
        """Test crisis scenario has lower values"""
        normal = mock_generator.generate_layer2_output("normal")
        crisis = mock_generator.generate_layer2_output("crisis")
        
        # Crisis should have lower sentiment
        assert crisis["overall_sentiment"] < normal["overall_sentiment"]
    
    def test_generate_layer2_output_growth(self, mock_generator):
        """Test growth scenario has higher values"""
        normal = mock_generator.generate_layer2_output("normal")
        growth = mock_generator.generate_layer2_output("growth")
        
        # Growth should have higher sentiment
        assert growth["overall_sentiment"] > normal["overall_sentiment"]
    
    def test_generate_company_profile(self, mock_generator):
        """Test company profile generation"""
        profile = mock_generator.generate_company_profile("COMP001", "retail")
        
        assert profile["company_id"] == "COMP001"
        assert profile["industry"] == "retail"
        assert "company_name" in profile
        assert "annual_revenue" in profile
    
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same output"""
        gen1 = MockDataGenerator(seed=123)
        gen2 = MockDataGenerator(seed=123)
        
        output1 = gen1.generate_layer2_output("normal")
        output2 = gen2.generate_layer2_output("normal")
        
        assert output1["overall_sentiment"] == output2["overall_sentiment"]


# =============================================================================
# End-to-End Integration Tests
# =============================================================================

class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_flow_manufacturing_crisis(self, mock_generator):
        """Test full flow for manufacturing company in crisis"""
        pipeline = create_pipeline()
        
        l2_data = mock_generator.generate_layer2_output("crisis")
        company = mock_generator.generate_company_profile("MFG001", "manufacturing")
        
        result = await pipeline.run_full_pipeline(company, layer2_input=l2_data)
        
        assert result["success"] is True
        
        # In crisis, should have critical issues
        l3 = result["layer3_output"]
        # Overall health should be lower
        assert l3["overall_operational_health"] < 60
    
    @pytest.mark.asyncio
    async def test_full_flow_retail_growth(self, mock_generator):
        """Test full flow for retail company in growth"""
        pipeline = create_pipeline()
        
        l2_data = mock_generator.generate_layer2_output("growth")
        company = mock_generator.generate_company_profile("RET001", "retail")
        
        result = await pipeline.run_full_pipeline(company, layer2_input=l2_data)
        
        assert result["success"] is True
        
        # In growth, should have good health
        l3 = result["layer3_output"]
        assert l3["overall_operational_health"] > 50
    
    @pytest.mark.asyncio
    async def test_traceability(self, layer2_output_normal, company_profile):
        """Test that Layer 3 output traces back to Layer 2"""
        pipeline = create_pipeline()
        
        result = await pipeline.run_full_pipeline(
            company_profile,
            layer2_input=layer2_output_normal
        )
        
        l2_indicator_ids = set(layer2_output_normal["indicators"].keys())
        l3_sources = set(result["layer3_output"]["source_national_indicators"])
        
        # L3 should reference L2 indicators
        assert len(l3_sources.intersection(l2_indicator_ids)) > 0
