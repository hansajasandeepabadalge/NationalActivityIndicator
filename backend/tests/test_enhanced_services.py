"""
Tests for Layer 2 LLM Enhancement Services

Tests cover:
- LLM Classifier with fallback
- Advanced Sentiment Analyzer
- Smart Entity Extractor
- Topic Modeler
- Quality Scorer
- Enhanced Pipeline

Note: These tests use mocked LLM responses to avoid API calls during testing.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Import services
from app.layer2.services.llm_classifier import (
    LLMClassifier,
    ClassificationResult,
    PESTELCategory,
    UrgencyLevel,
    BusinessRelevance,
    create_llm_classifier
)
from app.layer2.services.advanced_sentiment import (
    AdvancedSentimentAnalyzer,
    AdvancedSentimentResult,
    SentimentLevel,
    create_advanced_sentiment_analyzer
)
from app.layer2.services.smart_entity_extractor import (
    SmartEntityExtractor,
    SmartEntityResult,
    Entity,
    EntityType,
    create_smart_entity_extractor
)
from app.layer2.services.topic_modeler import (
    TopicModeler,
    TopicCluster,
    TopicMatch,
    create_topic_modeler
)
from app.layer2.services.quality_scorer import (
    QualityScorer,
    QualityScore,
    QualityBand,
    create_quality_scorer
)
from app.layer2.services.enhanced_pipeline import (
    EnhancedPipeline,
    EnhancedProcessingResult,
    PipelineConfig,
    create_enhanced_pipeline
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_article():
    """Sample article for testing."""
    return {
        "text": """The Federal Reserve announced a 0.25% interest rate hike today, 
        citing concerns about persistent inflation in the economy. Fed Chair Jerome Powell 
        stated that further increases may be necessary if inflation remains above the 2% target.
        The decision was made unanimously by the Federal Open Market Committee. 
        Market analysts expect this to impact housing prices and consumer spending.""",
        "title": "Fed Raises Interest Rates Amid Inflation Concerns",
        "source": "Reuters",
        "article_id": "test_001"
    }


@pytest.fixture
def short_article():
    """Short article for edge case testing."""
    return {
        "text": "Markets up today.",
        "title": "Brief Update",
        "source": "News",
        "article_id": "test_short"
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM classification response."""
    return {
        "categories": [
            {"category": "economic", "confidence": 0.92, "sub_themes": ["monetary policy", "inflation"], "reasoning": "Article focuses on Fed interest rate decision"},
            {"category": "political", "confidence": 0.3, "sub_themes": ["policy"], "reasoning": "Government institution involved"}
        ],
        "primary_category": "economic",
        "urgency": "important",
        "business_relevance": "critical",
        "key_entities": ["Federal Reserve", "Jerome Powell", "FOMC"],
        "summary": "Fed raises interest rates by 0.25% due to inflation concerns."
    }


# ============================================================================
# LLM Classifier Tests
# ============================================================================

class TestLLMClassifier:
    """Tests for LLMClassifier."""
    
    def test_classifier_creation(self):
        """Test classifier can be created."""
        classifier = create_llm_classifier(cache_enabled=False)
        assert classifier is not None
        assert isinstance(classifier, LLMClassifier)
    
    @pytest.mark.asyncio
    async def test_rule_based_fallback(self, sample_article):
        """Test rule-based classification fallback."""
        classifier = LLMClassifier()
        
        # Test the internal rule-based method
        result = classifier._rule_based_classify(sample_article["text"])
        
        assert isinstance(result, ClassificationResult)
        assert result.primary_category in PESTELCategory
        assert 0 <= result.primary_confidence <= 1
        assert result.classification_source == "rule_fallback"
    
    def test_category_mapping(self):
        """Test PESTEL category to indicator mapping."""
        from app.layer2.services.llm_classifier import CATEGORY_TO_INDICATORS
        
        # Verify all categories have indicators
        for category in PESTELCategory:
            assert category in CATEGORY_TO_INDICATORS
            assert len(CATEGORY_TO_INDICATORS[category]) > 0
    
    def test_classification_result_to_dict(self):
        """Test ClassificationResult serialization."""
        result = ClassificationResult(
            primary_indicator_id="ECO_INFLATION",
            primary_category=PESTELCategory.ECONOMIC,
            primary_confidence=0.85,
            urgency=UrgencyLevel.IMPORTANT,
            business_relevance=BusinessRelevance.HIGH
        )
        
        result_dict = result.to_dict()
        assert result_dict["primary_indicator_id"] == "ECO_INFLATION"
        assert result_dict["primary_category"] == "economic"
        assert result_dict["urgency"] == "important"
    
    def test_classification_result_legacy_format(self):
        """Test backward-compatible legacy format."""
        result = ClassificationResult(
            primary_indicator_id="ECO_INFLATION",
            primary_category=PESTELCategory.ECONOMIC,
            primary_confidence=0.85
        )
        
        legacy = result.to_legacy_format()
        assert "indicator_id" in legacy
        assert "category" in legacy
        assert "confidence" in legacy


# ============================================================================
# Advanced Sentiment Tests
# ============================================================================

class TestAdvancedSentiment:
    """Tests for AdvancedSentimentAnalyzer."""
    
    def test_analyzer_creation(self):
        """Test analyzer can be created."""
        analyzer = create_advanced_sentiment_analyzer(cache_enabled=False)
        assert analyzer is not None
        assert isinstance(analyzer, AdvancedSentimentAnalyzer)
    
    def test_quick_sentiment_check(self, sample_article):
        """Test quick keyword-based sentiment check."""
        analyzer = AdvancedSentimentAnalyzer()
        
        # Positive text
        positive_result = analyzer._quick_sentiment_check("Growth and success in the economy")
        assert positive_result is None or positive_result >= 0
        
        # Negative text
        negative_result = analyzer._quick_sentiment_check("Crisis and decline in the market")
        assert negative_result is None or negative_result <= 0
        
        # Neutral text
        neutral_result = analyzer._quick_sentiment_check("The meeting was held yesterday")
        assert neutral_result is None or abs(neutral_result) < 0.2
    
    def test_keyword_based_analysis(self, sample_article):
        """Test keyword-based sentiment fallback."""
        analyzer = AdvancedSentimentAnalyzer()
        
        result = analyzer._keyword_based_analysis(sample_article["text"])
        
        assert isinstance(result, AdvancedSentimentResult)
        assert -1 <= result.overall_score <= 1
        assert result.overall_level in SentimentLevel
    
    def test_sentiment_result_to_dict(self):
        """Test AdvancedSentimentResult serialization."""
        result = AdvancedSentimentResult(
            overall_score=0.3,
            overall_level=SentimentLevel.POSITIVE,
            overall_confidence=0.8,
            business_confidence_score=0.4,
            business_confidence_level=SentimentLevel.POSITIVE
        )
        
        result_dict = result.to_dict()
        assert "overall" in result_dict
        assert "dimensions" in result_dict
        assert result_dict["overall"]["score"] == 0.3
    
    def test_composite_score_calculation(self):
        """Test weighted composite score."""
        result = AdvancedSentimentResult(
            overall_score=0.5,
            overall_level=SentimentLevel.POSITIVE,
            overall_confidence=0.8,
            business_confidence_score=0.6,
            public_mood_score=0.3,
            economic_outlook_score=0.4
        )
        
        composite = result.get_composite_score()
        assert -1 <= composite <= 1


# ============================================================================
# Smart Entity Extractor Tests
# ============================================================================

class TestSmartEntityExtractor:
    """Tests for SmartEntityExtractor."""
    
    def test_extractor_creation(self):
        """Test extractor can be created."""
        extractor = create_smart_entity_extractor(cache_enabled=False)
        assert extractor is not None
        assert isinstance(extractor, SmartEntityExtractor)
    
    def test_regex_based_extraction(self, sample_article):
        """Test regex-based entity extraction fallback."""
        extractor = SmartEntityExtractor()
        
        result = extractor._regex_based_extraction(sample_article["text"])
        
        assert isinstance(result, SmartEntityResult)
        assert result.entity_count >= 0
    
    def test_master_entity_table(self):
        """Test master entity table lookup."""
        from app.layer2.services.smart_entity_extractor import get_master_entity_table
        
        table = get_master_entity_table()
        
        # Test known entities
        assert table.lookup("Federal Reserve") is None  # Not in default table
        assert table.lookup("IMF") == "ORG_IMF"
        assert table.lookup("GDP") == "ECON_GDP"
    
    def test_entity_to_dict(self):
        """Test Entity serialization."""
        entity = Entity(
            text="Federal Reserve",
            normalized="Federal Reserve",
            entity_type=EntityType.ORGANIZATION,
            role="subject",
            importance=0.9
        )
        
        entity_dict = entity.to_dict()
        assert entity_dict["text"] == "Federal Reserve"
        assert entity_dict["type"] == "organization"


# ============================================================================
# Topic Modeler Tests
# ============================================================================

class TestTopicModeler:
    """Tests for TopicModeler."""
    
    def test_modeler_creation(self):
        """Test topic modeler can be created."""
        modeler = create_topic_modeler()
        assert modeler is not None
        assert isinstance(modeler, TopicModeler)
    
    def test_topic_id_generation(self):
        """Test topic ID generation."""
        modeler = TopicModeler()
        
        id1 = modeler._generate_topic_id("Some article text about economics")
        id2 = modeler._generate_topic_id("Some article text about economics")
        id3 = modeler._generate_topic_id("Different article text")
        
        # Same text should produce same ID
        assert id1 == id2
        # Different text should produce different ID
        assert id1 != id3
    
    def test_topic_cluster_to_dict(self):
        """Test TopicCluster serialization."""
        from app.layer2.services.topic_modeler import TopicStatus, TopicCategory
        
        cluster = TopicCluster(
            topic_id="topic_abc123",
            name="Economic Policy",
            description="Topics about economic policy",
            category=TopicCategory.ECONOMY,
            article_count=5,
            status=TopicStatus.TRENDING
        )
        
        cluster_dict = cluster.to_dict()
        assert cluster_dict["topic_id"] == "topic_abc123"
        assert cluster_dict["name"] == "Economic Policy"
        assert cluster_dict["status"] == "trending"


# ============================================================================
# Quality Scorer Tests
# ============================================================================

class TestQualityScorer:
    """Tests for QualityScorer."""
    
    def test_scorer_creation(self):
        """Test quality scorer can be created."""
        scorer = create_quality_scorer()
        assert scorer is not None
        assert isinstance(scorer, QualityScorer)
    
    def test_score_with_complete_data(self):
        """Test scoring with complete processing results."""
        scorer = QualityScorer()
        
        quality = scorer.score(
            classification_result={
                "primary_confidence": 0.9,
                "all_categories": {"economic": 0.9, "political": 0.3},
                "sub_themes": {"economic": ["monetary policy"]},
                "classification_source": "llm"
            },
            sentiment_result={
                "overall": {"confidence": 0.85},
                "dimensions": {"business_confidence": {}, "public_mood": {}, "economic_outlook": {}},
                "drivers": {"positive": [{"factor": "growth"}], "negative": []},
                "analysis_source": "llm"
            },
            entity_result={
                "entity_count": 10,
                "entities_by_type": {"organization": [], "person": [], "location": []},
                "relationship_count": 5,
                "extraction_source": "llm"
            },
            article_metadata={
                "title": "Test Article",
                "text": "This is test content with sufficient length for processing and analysis purposes.",
                "source": "TestSource",
                "published_at": "2024-01-01T00:00:00"
            }
        )
        
        assert isinstance(quality, QualityScore)
        assert 0 <= quality.overall_score <= 100
        assert quality.quality_band in QualityBand
    
    def test_score_with_minimal_data(self):
        """Test scoring with minimal data."""
        scorer = QualityScorer()
        
        quality = scorer.score(
            classification_result=None,
            sentiment_result=None,
            entity_result=None,
            article_metadata=None
        )
        
        assert isinstance(quality, QualityScore)
        # Should have low score with missing data
        assert quality.overall_score < 50
    
    def test_quality_bands(self):
        """Test quality band thresholds."""
        from app.layer2.services.quality_scorer import score_to_band
        
        assert score_to_band(95) == QualityBand.EXCELLENT
        assert score_to_band(80) == QualityBand.GOOD
        assert score_to_band(60) == QualityBand.FAIR
        assert score_to_band(30) == QualityBand.POOR
        assert score_to_band(10) == QualityBand.UNRELIABLE
    
    def test_quality_score_is_acceptable(self):
        """Test quality threshold checking."""
        scorer = QualityScorer(min_acceptable_score=50.0)
        
        quality_high = QualityScore(
            overall_score=75,
            quality_band=QualityBand.GOOD
        )
        assert quality_high.is_acceptable(50.0)
        
        quality_low = QualityScore(
            overall_score=30,
            quality_band=QualityBand.POOR
        )
        assert not quality_low.is_acceptable(50.0)


# ============================================================================
# Enhanced Pipeline Tests
# ============================================================================

class TestEnhancedPipeline:
    """Tests for EnhancedPipeline."""
    
    def test_pipeline_creation(self):
        """Test pipeline can be created."""
        pipeline = create_enhanced_pipeline()
        assert pipeline is not None
        assert isinstance(pipeline, EnhancedPipeline)
    
    def test_pipeline_config(self):
        """Test pipeline configuration."""
        config = PipelineConfig(
            enable_llm_classification=True,
            enable_advanced_sentiment=True,
            parallel_processing=True,
            max_concurrency=10
        )
        
        pipeline = EnhancedPipeline(config=config)
        assert pipeline.config.enable_llm_classification
        assert pipeline.config.max_concurrency == 10
    
    def test_processing_result_to_dict(self):
        """Test EnhancedProcessingResult serialization."""
        result = EnhancedProcessingResult(
            article_id="test_123",
            success=True,
            stages_completed=["classification", "sentiment"],
            processing_time_ms=150.5
        )
        
        result_dict = result.to_dict()
        assert result_dict["article_id"] == "test_123"
        assert result_dict["success"]
        assert result_dict["stages_completed"] == ["classification", "sentiment"]
    
    def test_processing_result_summary(self):
        """Test EnhancedProcessingResult summary."""
        result = EnhancedProcessingResult(
            article_id="test_123",
            success=True,
            stages_completed=["classification", "sentiment", "entities"],
            fallbacks_used=["sentiment"],
            processing_time_ms=150.5
        )
        
        summary = result.get_summary()
        assert summary["article_id"] == "test_123"
        assert summary["success"]
        assert summary["stages_completed"] == 3
        assert summary["fallbacks_used"] == 1


# ============================================================================
# Integration Tests (with mocked LLM)
# ============================================================================

class TestIntegration:
    """Integration tests with mocked LLM responses."""
    
    @pytest.mark.asyncio
    async def test_classifier_with_fallback(self, sample_article):
        """Test classifier falls back gracefully when LLM fails."""
        classifier = LLMClassifier()
        
        # Without LLM configured, should use fallback
        result = await classifier.classify(
            text=sample_article["text"],
            title=sample_article["title"]
        )
        
        assert isinstance(result, ClassificationResult)
        assert result.classification_source in ["llm", "rule_fallback", "hybrid_fallback"]
    
    @pytest.mark.asyncio
    async def test_sentiment_with_fallback(self, sample_article):
        """Test sentiment analyzer falls back gracefully."""
        analyzer = AdvancedSentimentAnalyzer()
        
        result = await analyzer.analyze(
            text=sample_article["text"],
            title=sample_article["title"]
        )
        
        assert isinstance(result, AdvancedSentimentResult)
        assert result.analysis_source in ["llm", "basic_fallback", "keyword_fallback", "quick_check"]
    
    @pytest.mark.asyncio
    async def test_entity_extraction_with_fallback(self, sample_article):
        """Test entity extractor falls back gracefully."""
        extractor = SmartEntityExtractor()
        
        result = await extractor.extract(
            text=sample_article["text"],
            title=sample_article["title"]
        )
        
        assert isinstance(result, SmartEntityResult)
        assert result.extraction_source in ["llm", "basic_fallback", "regex_fallback", "skipped"]


# ============================================================================
# Feature Flag Tests
# ============================================================================

class TestFeatureFlags:
    """Tests for feature flag system."""
    
    def test_feature_flags_import(self):
        """Test feature flags are accessible."""
        from app.layer2.services import (
            LLM_CLASSIFICATION_ENABLED,
            ADVANCED_SENTIMENT_ENABLED,
            SMART_NER_ENABLED,
            TOPIC_MODELING_ENABLED,
            QUALITY_SCORING_ENABLED
        )
        
        # Flags should be boolean
        assert isinstance(LLM_CLASSIFICATION_ENABLED, bool)
        assert isinstance(ADVANCED_SENTIMENT_ENABLED, bool)
        assert isinstance(SMART_NER_ENABLED, bool)
        assert isinstance(TOPIC_MODELING_ENABLED, bool)
        assert isinstance(QUALITY_SCORING_ENABLED, bool)
    
    def test_singleton_getters(self):
        """Test singleton getter functions."""
        from app.layer2.services import (
            get_llm_classifier,
            get_advanced_sentiment,
            get_smart_entity_extractor,
            get_quality_scorer,
            reset_singletons
        )
        
        # Reset to ensure clean state
        reset_singletons()
        
        # Get instances
        classifier1 = get_llm_classifier()
        classifier2 = get_llm_classifier()
        
        # Should be same instance
        assert classifier1 is classifier2
        
        # Reset for other tests
        reset_singletons()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
