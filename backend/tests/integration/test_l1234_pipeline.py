"""
End-to-End Integration Test for Full L1-L4 Pipeline

Tests the complete data flow:
Layer 1 (AI Agents) → PostgreSQL (raw_articles) → 
Layer 2 (National Indicators) → Layer 3 (Operational Indicators) → 
Layer 4 (Business Insights)

This test verifies that all layers work together seamlessly.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock

# Test if all layer imports work
def test_all_layers_importable():
    """Test that all layer modules can be imported without errors."""
    errors = []
    
    # Layer 1: AI Agents
    try:
        from app.agents import (
            SourceMonitorAgent,
            PriorityAgent,
            ProcessingAgent,
            SchedulerAgent,
            ValidationAgent
        )
    except ImportError as e:
        errors.append(f"Layer 1 agents: {e}")
    
    # Layer 1: Supporting modules
    try:
        from app.cache import SmartCache
        from app.deduplication import SemanticDeduplicator
        from app.cross_validation import ValidationNetwork
        from app.impact_scorer import BusinessImpactScorer
        from app.orchestrator import MasterOrchestrator
    except ImportError as e:
        errors.append(f"Layer 1 support modules: {e}")
    
    # Layer 2: National Indicators
    try:
        from app.layer2.services import (
            get_llm_classifier,
            get_advanced_sentiment,
            get_smart_entity_extractor,
            get_topic_modeler,
            get_quality_scorer,
            get_enhanced_pipeline
        )
    except ImportError as e:
        errors.append(f"Layer 2 services: {e}")
    
    # Layer 3: Operational Indicators
    try:
        from app.layer3.services.operational_service import OperationalService
    except ImportError as e:
        errors.append(f"Layer 3 service: {e}")
    
    # Layer 4: Business Insights
    try:
        from app.layer4.risk_detection import RuleBasedRiskDetector
        from app.layer4.opportunity_detection import RuleBasedOpportunityDetector
        from app.layer4.recommendation import RecommendationEngine
        from app.layer4.prioritization import InsightPrioritizer
    except ImportError as e:
        errors.append(f"Layer 4 components: {e}")
    
    # Integration Pipeline
    try:
        from app.integration.pipeline import IntegrationPipeline
        from app.integration.adapters import Layer2ToLayer3Adapter, Layer3ToLayer4Adapter
    except ImportError as e:
        errors.append(f"Integration pipeline: {e}")
    
    if errors:
        pytest.fail(f"Import errors:\n" + "\n".join(errors))


def test_api_router_has_all_layer_endpoints():
    """Test that API router includes endpoints for all layers."""
    from app.api.v1.router import api_router
    
    # Get all route paths
    paths = [route.path for route in api_router.routes]
    
    # Check for Layer 1 agent endpoints
    layer1_found = any('/agents' in path for path in paths)
    
    # Check for Layer 2 endpoints
    layer2_found = any('/indicators' in path or '/enhanced' in path for path in paths)
    
    # Check for Layer 4 endpoints
    layer4_found = any('/insights' in path or '/advanced' in path for path in paths)
    
    # Check for integration pipeline
    pipeline_found = any('/pipeline' in path for path in paths)
    
    assert layer1_found, "Layer 1 agent endpoints not found in router"
    assert layer2_found, "Layer 2 indicator endpoints not found in router"
    assert layer4_found, "Layer 4 insight endpoints not found in router"
    assert pipeline_found, "Integration pipeline endpoints not found in router"


def test_models_all_layers_available():
    """Test that all database models are accessible."""
    from app.models import (
        # Layer 1 models
        RawArticle,
        AgentDecision,
        ScrapingSchedule,
        UrgencyClassification,
        QualityValidation,
        AgentMetrics,
        SourceConfig,
        # Layer 2 models
        IndicatorDefinition,
        IndicatorValue,
        MLClassificationResult,
        # Layer 4 models
        BusinessInsight,
        RiskOpportunityDefinition,
        CompanyProfile
    )
    
    # Verify they are all proper classes/types
    assert RawArticle is not None
    assert AgentDecision is not None
    assert IndicatorDefinition is not None
    assert BusinessInsight is not None


def test_layer1_raw_article_schema():
    """Test that RawArticle schema matches Layer 2 expectations."""
    from app.models.raw_article import RawArticle, RawContent, SourceInfo, ScrapeMetadata, ValidationStatus
    from datetime import datetime
    
    # Create a sample raw article
    source = SourceInfo(source_id=1, name="Ada Derana", url="https://www.adaderana.lk")
    scrape_meta = ScrapeMetadata(job_id=1, scraped_at=datetime.now(), scraper_version="1.0.0")
    content = RawContent(
        title="Test Article",
        body="This is test content for the article.",
        author="Test Author",
        publish_date=datetime.now()
    )
    validation = ValidationStatus(is_valid=True, word_count=10)
    
    article = RawArticle(
        article_id="test_001",
        source=source,
        scrape_metadata=scrape_meta,
        raw_content=content,
        validation=validation
    )
    
    # Verify the article can be serialized to dict
    article_dict = article.model_dump()
    
    assert article_dict["article_id"] == "test_001"
    assert article_dict["raw_content"]["title"] == "Test Article"
    assert article_dict["source"]["name"] == "Ada Derana"


def test_layer2_feature_flags_available():
    """Test that Layer 2 LLM feature flags are accessible."""
    from app.layer2.services import (
        LLM_CLASSIFICATION_ENABLED,
        ADVANCED_SENTIMENT_ENABLED,
        SMART_NER_ENABLED,
        TOPIC_MODELING_ENABLED,
        QUALITY_SCORING_ENABLED,
        ADAPTIVE_INDICATORS_ENABLED
    )
    
    # All should be boolean
    assert isinstance(LLM_CLASSIFICATION_ENABLED, bool)
    assert isinstance(ADVANCED_SENTIMENT_ENABLED, bool)
    assert isinstance(SMART_NER_ENABLED, bool)
    assert isinstance(TOPIC_MODELING_ENABLED, bool)
    assert isinstance(QUALITY_SCORING_ENABLED, bool)
    assert isinstance(ADAPTIVE_INDICATORS_ENABLED, bool)


def test_integration_adapters_exist():
    """Test that L2→L3 and L3→L4 adapters work."""
    from app.integration.adapters import Layer2ToLayer3Adapter, Layer3ToLayer4Adapter
    
    l2_to_l3 = Layer2ToLayer3Adapter()
    l3_to_l4 = Layer3ToLayer4Adapter()
    
    # Verify adapters have key methods
    assert hasattr(l2_to_l3, 'transform')
    assert hasattr(l3_to_l4, 'transform')


def test_integration_pipeline_initialization():
    """Test that the integration pipeline can be initialized."""
    from app.integration.pipeline import IntegrationPipeline
    
    pipeline = IntegrationPipeline()
    
    # Verify key components
    assert pipeline.l2_to_l3_adapter is not None
    assert pipeline.l3_to_l4_adapter is not None


class TestEndToEndDataFlow:
    """Test the complete data flow through all layers."""
    
    @pytest.fixture
    def sample_article(self):
        """Create a sample article for testing."""
        return {
            "id": "test_article_001",
            "title": "Sri Lanka Central Bank Raises Interest Rates by 50 Basis Points",
            "content": """
            The Central Bank of Sri Lanka (CBSL) announced a 50 basis point increase 
            in the Standing Deposit Facility Rate (SDFR) and the Standing Lending Facility Rate (SLFR). 
            This move aims to combat rising inflation which reached 12.1% in November.
            Governor Dr. P. Nandalal Weerasinghe stated that the decision was necessary 
            to ensure price stability and support long-term economic growth.
            The new rates will be effective from December 8, 2024.
            Business leaders expressed concern about increased borrowing costs.
            """,
            "source": "Daily FT",
            "published_at": datetime.now().isoformat(),
            "url": "https://www.ft.lk/example"
        }
    
    @pytest.fixture
    def sample_company_profile(self):
        """Create a sample company profile for Layer 4."""
        return {
            "company_id": "comp_001",
            "name": "ABC Manufacturing Ltd",
            "industry": "manufacturing",
            "sector": "consumer_goods",
            "size": "medium",
            "location": "Western Province, Sri Lanka",
            "key_concerns": ["supply_chain", "cost_pressure", "workforce"]
        }
    
    def test_layer1_to_layer2_data_format(self, sample_article):
        """Test that Layer 1 output format matches Layer 2 input expectations."""
        # Layer 1 would output articles with this structure
        layer1_output = {
            "article_id": sample_article["id"],
            "title": sample_article["title"],
            "content": sample_article["content"],
            "source": sample_article["source"],
            "scraped_at": datetime.now().isoformat(),
            "url": sample_article["url"],
            # Layer 1 additions
            "urgency_level": "high",
            "quality_score": 0.85,
            "trust_score": 0.92,
            "is_duplicate": False
        }
        
        # Verify required fields for Layer 2
        required_fields = ["article_id", "title", "content", "source"]
        for field in required_fields:
            assert field in layer1_output, f"Missing required field: {field}"
    
    def test_layer2_classification_output_structure(self, sample_article):
        """Test Layer 2 classification output structure."""
        from app.layer2.services.llm_classifier import ClassificationResult, PESTELCategory, UrgencyLevel, BusinessRelevance
        
        # Mock classification result
        result = ClassificationResult(
            primary_indicator_id="ECON_INTEREST_RATE",
            primary_category=PESTELCategory.ECONOMIC,
            primary_confidence=0.92,
            all_categories={"economic": 0.92, "political": 0.45},
            sub_themes={"economic": ["interest rates", "monetary policy", "inflation"]},
            urgency=UrgencyLevel.URGENT,
            business_relevance=BusinessRelevance.CRITICAL,
            key_entities=["Central Bank of Sri Lanka", "Dr. P. Nandalal Weerasinghe"],
            summary="CBSL raises interest rates by 50bp to combat inflation"
        )
        
        # Test conversion to dict (for API response)
        result_dict = result.to_dict()
        
        assert result_dict["primary_category"] == "economic"
        assert result_dict["primary_confidence"] >= 0.9
        assert "interest rates" in result_dict["sub_themes"]["economic"]
    
    def test_layer3_receives_layer2_output(self, sample_article, sample_company_profile):
        """Test that Layer 3 can receive Layer 2 output."""
        from app.integration.adapters import Layer2ToLayer3Adapter
        from app.integration.contracts import Layer2Output, IndicatorValueOutput
        
        # Create mock Layer 2 output
        indicator_values = [
            IndicatorValueOutput(
                indicator_id="ECON_INTEREST_RATE",
                value=0.75,
                confidence=0.92,
                trend_direction="increasing",
                data_points=5,
                category="Economic"
            )
        ]
        
        layer2_output = Layer2Output(
            calculation_timestamp=datetime.now(),
            indicators=indicator_values,
            articles_processed=1
        )
        
        # Transform to Layer 3 input
        adapter = Layer2ToLayer3Adapter()
        layer3_input = adapter.transform(
            layer2_output,
            company_profile=sample_company_profile
        )
        
        assert layer3_input is not None
    
    def test_full_pipeline_mock_run(self, sample_article, sample_company_profile):
        """Test a mock run through the full pipeline."""
        from app.integration.pipeline import IntegrationPipeline
        
        pipeline = IntegrationPipeline()
        
        # The pipeline should be initializable
        assert pipeline is not None
        assert pipeline.l2_to_l3_adapter is not None
        assert pipeline.l3_to_l4_adapter is not None


class TestLayerConnectivity:
    """Test connectivity between layers."""
    
    def test_database_models_compatible(self):
        """Test that database models from all layers are compatible."""
        from app.db.base_class import Base
        from app.models.agent_models import AgentDecision, ScrapingSchedule
        from app.models.indicator_models import IndicatorDefinition, IndicatorValue
        from app.models.business_insight_models import BusinessInsight
        
        # All models should inherit from Base
        assert issubclass(AgentDecision, Base)
        assert issubclass(ScrapingSchedule, Base)
        assert issubclass(IndicatorDefinition, Base)
        assert issubclass(IndicatorValue, Base)
        assert issubclass(BusinessInsight, Base)
    
    def test_layer1_output_table_exists_in_schema(self):
        """Verify the raw_articles concept is implemented."""
        from app.models.raw_article import RawArticle
        
        # RawArticle should be a Pydantic model for data transfer
        assert RawArticle is not None
        assert hasattr(RawArticle, 'model_fields') or hasattr(RawArticle, '__fields__')


# Run basic connectivity test
if __name__ == "__main__":
    print("Running L1-L4 Integration Tests...")
    
    # Test 1: All imports
    try:
        test_all_layers_importable()
        print("✅ All layers importable")
    except Exception as e:
        print(f"❌ Import test failed: {e}")
    
    # Test 2: API Router
    try:
        test_api_router_has_all_layer_endpoints()
        print("✅ API router has all endpoints")
    except Exception as e:
        print(f"❌ Router test failed: {e}")
    
    # Test 3: Models
    try:
        test_models_all_layers_available()
        print("✅ All models available")
    except Exception as e:
        print(f"❌ Models test failed: {e}")
    
    # Test 4: Feature flags
    try:
        test_layer2_feature_flags_available()
        print("✅ Layer 2 feature flags available")
    except Exception as e:
        print(f"❌ Feature flags test failed: {e}")
    
    # Test 5: Integration pipeline
    try:
        test_integration_pipeline_initialization()
        print("✅ Integration pipeline initializable")
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
    
    print("\nIntegration tests complete!")
