"""Pytest configuration and fixtures for Layer2 tests"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Async Event Loop
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def db_session():
    """Create database session for tests"""
    from app.db.session import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def mock_db_session():
    """Mock database session for unit tests"""
    mock = MagicMock()
    mock.query.return_value.filter.return_value.first.return_value = None
    mock.query.return_value.all.return_value = []
    mock.add = MagicMock()
    mock.commit = MagicMock()
    mock.rollback = MagicMock()
    mock.close = MagicMock()
    return mock


# ============================================================================
# Redis Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def mock_redis():
    """Mock Redis client for unit tests"""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.setex.return_value = True
    mock.delete.return_value = 1
    mock.keys.return_value = []
    mock.ping.return_value = True
    return mock


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_article():
    """Sample article for testing"""
    return {
        "article_id": "TEST_001",
        "title": "Economic Growth Surges as Inflation Stabilizes",
        "content": """The economy showed remarkable growth of 4.5% this quarter,
        exceeding analyst expectations. The Central Bank maintained interest rates
        at 6.5%, signaling confidence in the recovery. Consumer spending rose by
        3.2% while unemployment dropped to 5.1%. The stock market reached new highs
        with the main index gaining 8% this month.""",
        "source": "test_source",
        "category": "Economic",
        "published_at": datetime.now()
    }


@pytest.fixture
def sample_articles():
    """Multiple sample articles for batch testing"""
    return [
        {
            "article_id": f"TEST_{i:03d}",
            "title": f"Test Article {i}",
            "content": f"This is test content for article {i}. " * 50,
            "source": "test_source",
            "category": ["Economic", "Political", "Social"][i % 3],
            "published_at": datetime.now() - timedelta(days=i)
        }
        for i in range(10)
    ]


@pytest.fixture
def sample_indicator_values():
    """Sample indicator values for trend testing"""
    base_time = datetime.now()
    return [
        {
            "indicator_id": "ECO_GDP_GROWTH",
            "value": 50.0 + i * 2,  # Upward trend
            "timestamp": base_time - timedelta(hours=i),
            "confidence": 0.85
        }
        for i in range(24)
    ]


@pytest.fixture
def sample_entities():
    """Sample extracted entities"""
    return {
        "article_id": "TEST_001",
        "organizations": ["Central Bank", "Treasury", "IMF"],
        "locations": ["Colombo", "Kandy", "Sri Lanka"],
        "amounts": [
            {"value": 500000000, "currency": "USD", "context": "intervention"},
            {"value": 4.5, "unit": "percent", "context": "growth"}
        ],
        "percentages": [4.5, 3.2, 5.1, 6.5, 8.0],
        "dates": [datetime.now()]
    }


# ============================================================================
# Component Fixtures
# ============================================================================

@pytest.fixture
def sentiment_analyzer():
    """Create SentimentAnalyzer instance"""
    from app.layer2.nlp.sentiment_analyzer import SentimentAnalyzer
    return SentimentAnalyzer(use_transformers=False)  # Fast mode for tests


@pytest.fixture
def dependency_mapper():
    """Create DependencyMapper instance"""
    from app.layer2.analysis.dependency_mapper import DependencyMapper
    return DependencyMapper()


@pytest.fixture
def alert_manager(mock_db_session, mock_redis):
    """Create AlertManager with mocked dependencies"""
    from app.layer2.alerting.alert_manager import AlertManager
    manager = AlertManager(db_session=mock_db_session)
    return manager


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def test_client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async HTTP client for async tests"""
    from httpx import AsyncClient
    from app.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# Marker Helpers
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
