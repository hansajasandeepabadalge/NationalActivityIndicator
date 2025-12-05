"""Integration tests for Layer 2 pipeline - Day 6"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.layer2.nlp_processing.entity_extractor import EntityExtractor
from app.layer2.indicator_calculation.entity_based_calculator import EntityBasedIndicatorCalculator
from app.layer2.narrative.generator import NarrativeGenerator
from app.db.mongodb_entities import MongoDBEntityStorage

client = TestClient(app)


@pytest.fixture
def sample_article():
    return {
        "article_id": "TEST_001",
        "title": "Central Bank Stabilizes Exchange Rate with $500 Million Intervention",
        "content": """The Central Bank of Sri Lanka announced today a major intervention
        in currency markets, deploying USD 500 million to stabilize the exchange rate.
        The move comes after the rupee depreciated by 3.5% against the dollar last week.
        Officials in Colombo and Kandy reported strong economic activity."""
    }


class TestEntityExtraction:
    """Test entity extraction pipeline"""

    def test_entity_extractor_loads(self):
        """Test singleton pattern loads spaCy model once"""
        extractor = EntityExtractor()
        assert extractor._nlp is not None

    def test_extract_entities(self, sample_article):
        """Test entity extraction from article"""
        extractor = EntityExtractor()
        entities = extractor.extract_entities(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )

        assert entities.article_id == "TEST_001"
        assert len(entities.amounts) > 0  # Should detect $500 million
        assert len(entities.percentages) > 0  # Should detect 3.5%
        assert len(entities.locations) > 0  # Should detect Colombo, Kandy
        assert len(entities.organizations) > 0  # Should detect Central Bank

    def test_currency_extraction(self, sample_article):
        """Test currency amount parsing"""
        extractor = EntityExtractor()
        entities = extractor.extract_entities(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )

        usd_amounts = [amt for amt in entities.amounts if amt.currency == "USD"]
        assert len(usd_amounts) > 0
        assert any(amt.amount == 500_000_000 for amt in usd_amounts)


class TestIndicatorCalculation:
    """Test indicator calculation"""

    def test_currency_stability_calculation(self, sample_article):
        """Test ECO_CURRENCY_STABILITY indicator"""
        extractor = EntityExtractor()
        calculator = EntityBasedIndicatorCalculator()

        entities = extractor.extract_entities(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )

        confidence = calculator.calculate_currency_stability(entities)
        assert confidence > 0.6  # Should have high confidence
        assert confidence <= 0.9

    def test_geographic_scope_calculation(self, sample_article):
        """Test POL_GEOGRAPHIC_SCOPE indicator"""
        extractor = EntityExtractor()
        calculator = EntityBasedIndicatorCalculator()

        entities = extractor.extract_entities(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )

        confidence = calculator.calculate_geographic_scope(entities)
        assert confidence > 0.0  # Should detect locations
        assert confidence <= 0.9


class TestNarrativeGeneration:
    """Test narrative generation"""

    def test_generate_narrative(self, sample_article):
        """Test narrative generation for currency stability"""
        extractor = EntityExtractor()
        generator = NarrativeGenerator()

        entities = extractor.extract_entities(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )

        narrative = generator.generate_narrative(
            article_id=sample_article["article_id"],
            indicator_id="ECO_CURRENCY_STABILITY",
            confidence=0.75,
            entities=entities,
            trend="rising"
        )

        assert narrative.article_id == "TEST_001"
        assert narrative.indicator_id == "ECO_CURRENCY_STABILITY"
        assert narrative.emoji in ["📈", "📉", "➡️", "⚠️", "🔥"]
        assert len(narrative.headline) > 0
        assert len(narrative.summary) > 50  # At least 2 sentences


class TestMongoDBStorage:
    """Test MongoDB integration"""

    def test_store_and_retrieve_entities(self, sample_article):
        """Test entity storage and retrieval"""
        mongo = MongoDBEntityStorage()
        extractor = EntityExtractor()

        entities = extractor.extract_entities(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )

        # Store
        success = mongo.store_entities(entities)
        assert success is True

        # Retrieve
        retrieved = mongo.get_entities("TEST_001")
        assert retrieved is not None
        assert retrieved.article_id == "TEST_001"

    def test_store_narrative(self, sample_article):
        """Test narrative storage"""
        mongo = MongoDBEntityStorage()
        extractor = EntityExtractor()
        generator = NarrativeGenerator()

        entities = extractor.extract_entities(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )

        narrative = generator.generate_narrative(
            article_id="TEST_001",
            indicator_id="ECO_CURRENCY_STABILITY",
            confidence=0.75,
            entities=entities
        )

        success = mongo.store_narrative(narrative)
        assert success is True


class TestAPIEndpoints:
    """Test REST API endpoints"""

    def test_list_indicators(self):
        """Test GET /api/v1/indicators"""
        response = client.get("/api/v1/indicators")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert any(ind["indicator_id"] == "ECO_CURRENCY_STABILITY" for ind in data)

    def test_get_indicator_details(self):
        """Test GET /api/v1/indicators/{id}"""
        response = client.get("/api/v1/indicators/ECO_CURRENCY_STABILITY")
        assert response.status_code in [200, 404]  # 404 if no data yet

    def test_get_indicator_history(self):
        """Test GET /api/v1/indicators/{id}/history"""
        response = client.get("/api/v1/indicators/ECO_CURRENCY_STABILITY/history?days=30")
        assert response.status_code in [200, 404]

    def test_get_trends(self):
        """Test GET /api/v1/indicators/trends"""
        response = client.get("/api/v1/indicators/trends/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_detect_anomalies(self):
        """Test GET /api/v1/indicators/anomalies"""
        response = client.get("/api/v1/indicators/anomalies/?threshold=2.0")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_alerts(self):
        """Test GET /api/v1/indicators/alerts"""
        response = client.get("/api/v1/indicators/alerts/?hours=24")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_composite_metrics(self):
        """Test GET /api/v1/indicators/composite"""
        response = client.get("/api/v1/indicators/composite/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2  # Economic Health, National Stability


class TestFullPipeline:
    """Test complete end-to-end pipeline"""

    def test_full_pipeline(self, sample_article):
        """Test: Article → Entities → Indicators → Narrative → API"""
        # Step 1: Extract entities
        extractor = EntityExtractor()
        entities = extractor.extract_entities(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )
        assert entities is not None

        # Step 2: Calculate indicators
        calculator = EntityBasedIndicatorCalculator()
        indicators = calculator.calculate_all_indicators(entities)
        assert len(indicators) >= 2

        # Step 3: Generate narratives
        generator = NarrativeGenerator()
        narratives = []
        for ind_id, confidence in indicators.items():
            if confidence > 0.3:
                narrative = generator.generate_narrative(
                    article_id=sample_article["article_id"],
                    indicator_id=ind_id,
                    confidence=confidence,
                    entities=entities
                )
                narratives.append(narrative)
        assert len(narratives) > 0

        # Step 4: Store in MongoDB
        mongo = MongoDBEntityStorage()
        mongo.store_entities(entities)
        for narrative in narratives:
            mongo.store_narrative(narrative)

        # Step 5: Verify API access
        response = client.get("/api/v1/indicators")
        assert response.status_code == 200
