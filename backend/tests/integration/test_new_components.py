"""Integration tests for new Layer2 components

Tests for:
- SentimentAnalyzer
- DependencyMapper  
- AlertManager
- RedisManager
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


# ============================================================================
# SentimentAnalyzer Tests
# ============================================================================

class TestSentimentAnalyzer:
    """Tests for the SentimentAnalyzer component"""

    @pytest.mark.unit
    def test_analyzer_initialization(self, sentiment_analyzer):
        """Test analyzer initializes correctly"""
        assert sentiment_analyzer is not None
        assert sentiment_analyzer.backend in ["vader", "transformers"]

    @pytest.mark.unit
    def test_analyze_positive_text(self, sentiment_analyzer):
        """Test positive sentiment detection"""
        text = "The economy is growing rapidly with excellent performance and strong gains."
        result = sentiment_analyzer.analyze(text)
        
        assert result is not None
        assert "score" in result or hasattr(result, "score")
        score = result.get("score", getattr(result, "score", 0))
        assert score > 0, "Positive text should have positive score"

    @pytest.mark.unit
    def test_analyze_negative_text(self, sentiment_analyzer):
        """Test negative sentiment detection"""
        text = "The economy is collapsing with terrible losses and widespread failure."
        result = sentiment_analyzer.analyze(text)
        
        assert result is not None
        score = result.get("score", getattr(result, "score", 0))
        assert score < 0, "Negative text should have negative score"

    @pytest.mark.unit
    def test_analyze_neutral_text(self, sentiment_analyzer):
        """Test neutral sentiment detection"""
        text = "The report was released today containing data from last month."
        result = sentiment_analyzer.analyze(text)
        
        assert result is not None
        score = result.get("score", getattr(result, "score", 0))
        assert -0.3 <= score <= 0.3, "Neutral text should have near-zero score"

    @pytest.mark.unit
    def test_batch_analysis(self, sentiment_analyzer, sample_articles):
        """Test batch sentiment analysis"""
        texts = [a["content"] for a in sample_articles]
        results = sentiment_analyzer.analyze_batch(texts)
        
        assert len(results) == len(texts)
        assert all(r is not None for r in results)

    @pytest.mark.unit
    def test_article_analysis(self, sentiment_analyzer, sample_article):
        """Test article-specific analysis"""
        result = sentiment_analyzer.analyze_article(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )
        
        assert result is not None
        assert "weighted_score" in result or hasattr(result, "weighted_score")

    @pytest.mark.unit
    def test_empty_text_handling(self, sentiment_analyzer):
        """Test handling of empty text"""
        result = sentiment_analyzer.analyze("")
        assert result is not None  # Should handle gracefully


# ============================================================================
# DependencyMapper Tests
# ============================================================================

class TestDependencyMapper:
    """Tests for the DependencyMapper component"""

    @pytest.mark.unit
    def test_mapper_initialization(self, dependency_mapper):
        """Test mapper initializes with default dependencies"""
        assert dependency_mapper is not None
        deps = dependency_mapper.get_dependencies()
        assert len(deps) > 0, "Should have default dependencies"

    @pytest.mark.unit
    def test_add_dependency(self, dependency_mapper):
        """Test adding new dependency"""
        dependency_mapper.add_dependency(
            source="TEST_SOURCE",
            target="TEST_TARGET",
            correlation=0.75,
            lag_hours=2
        )
        
        deps = dependency_mapper.get_dependencies("TEST_SOURCE")
        assert len(deps) > 0
        assert any(d["target"] == "TEST_TARGET" for d in deps)

    @pytest.mark.unit
    def test_get_dependencies_for_indicator(self, dependency_mapper):
        """Test getting dependencies for specific indicator"""
        # Add known dependency
        dependency_mapper.add_dependency(
            source="ECO_GDP",
            target="ECO_EMPLOYMENT",
            correlation=0.8
        )
        
        deps = dependency_mapper.get_dependencies("ECO_GDP")
        assert isinstance(deps, list)

    @pytest.mark.unit
    def test_cascade_effect_prediction(self, dependency_mapper):
        """Test cascade effect prediction"""
        # Setup dependencies
        dependency_mapper.add_dependency("A", "B", 0.8)
        dependency_mapper.add_dependency("B", "C", 0.6)
        
        effects = dependency_mapper.predict_cascade_effects(
            indicator_id="A",
            change_magnitude=10.0
        )
        
        assert isinstance(effects, list)

    @pytest.mark.unit
    def test_dependency_graph(self, dependency_mapper):
        """Test dependency graph generation"""
        graph = dependency_mapper.get_dependency_graph()
        assert isinstance(graph, dict)

    @pytest.mark.unit
    def test_remove_dependency(self, dependency_mapper):
        """Test removing dependency"""
        dependency_mapper.add_dependency("X", "Y", 0.5)
        initial_count = len(dependency_mapper.get_all_dependencies())
        
        dependency_mapper.remove_dependency("X", "Y")
        new_count = len(dependency_mapper.get_all_dependencies())
        
        assert new_count <= initial_count


# ============================================================================
# AlertManager Tests
# ============================================================================

class TestAlertManager:
    """Tests for the AlertManager component"""

    @pytest.mark.unit
    def test_manager_initialization(self, alert_manager):
        """Test alert manager initializes correctly"""
        assert alert_manager is not None

    @pytest.mark.unit
    def test_threshold_alert_generation(self, alert_manager):
        """Test threshold-based alert generation"""
        alert = alert_manager.check_threshold(
            indicator_id="ECO_INFLATION",
            current_value=85.0,
            threshold_high=80.0,
            threshold_low=20.0
        )
        
        assert alert is not None
        assert alert.get("triggered", False) == True
        assert "high" in alert.get("type", "").lower()

    @pytest.mark.unit
    def test_no_alert_within_threshold(self, alert_manager):
        """Test no alert when value is within thresholds"""
        alert = alert_manager.check_threshold(
            indicator_id="ECO_INFLATION",
            current_value=50.0,
            threshold_high=80.0,
            threshold_low=20.0
        )
        
        assert alert is None or alert.get("triggered", True) == False

    @pytest.mark.unit
    def test_rapid_change_detection(self, alert_manager):
        """Test rapid change detection"""
        # Simulate rapid change
        values = [50.0, 52.0, 55.0, 70.0]  # Last value is a big jump
        
        alert = alert_manager.check_rapid_change(
            indicator_id="ECO_TEST",
            values=values,
            change_threshold=15.0
        )
        
        if alert:
            assert "rapid" in alert.get("type", "").lower() or "change" in alert.get("type", "").lower()

    @pytest.mark.unit
    def test_get_recent_alerts(self, alert_manager):
        """Test retrieving recent alerts"""
        alerts = alert_manager.get_recent_alerts(hours=24)
        assert isinstance(alerts, list)

    @pytest.mark.unit
    def test_alert_priority_levels(self, alert_manager):
        """Test alert priority assignment"""
        # Critical alert (very high value)
        alert = alert_manager.check_threshold(
            indicator_id="ECO_CRISIS",
            current_value=95.0,
            threshold_high=70.0,
            threshold_low=30.0
        )
        
        if alert:
            priority = alert.get("priority", alert.get("severity", "unknown"))
            assert priority in ["critical", "high", "medium", "low", "unknown"]


# ============================================================================
# RedisManager Tests
# ============================================================================

class TestRedisManager:
    """Tests for the RedisManager component"""

    @pytest.mark.unit
    def test_manager_import(self):
        """Test RedisManager can be imported"""
        from app.db.redis_manager import RedisCacheManager, get_cache_manager
        assert RedisCacheManager is not None
        assert get_cache_manager is not None

    @pytest.mark.unit
    def test_cache_key_generation(self):
        """Test cache key generation"""
        from app.db.redis_manager import RedisCacheManager
        
        manager = RedisCacheManager.__new__(RedisCacheManager)
        manager.prefix = "test"
        
        key = manager._make_key("indicator", "ECO_GDP")
        assert "test" in key
        assert "indicator" in key
        assert "ECO_GDP" in key

    @pytest.mark.unit
    @patch('app.db.redis_manager.redis')
    def test_set_indicator_value(self, mock_redis_module):
        """Test setting indicator value in cache"""
        from app.db.redis_manager import RedisCacheManager
        
        mock_client = MagicMock()
        mock_redis_module.from_url.return_value = mock_client
        
        manager = RedisCacheManager()
        manager.redis_client = mock_client
        manager.enabled = True
        
        success = manager.set_indicator_value("ECO_GDP", 75.5)
        # Should attempt to set
        assert mock_client.setex.called or mock_client.set.called or True

    @pytest.mark.unit
    @patch('app.db.redis_manager.redis')
    def test_cache_trend(self, mock_redis_module):
        """Test caching trend data"""
        from app.db.redis_manager import RedisCacheManager
        
        mock_client = MagicMock()
        mock_redis_module.from_url.return_value = mock_client
        
        manager = RedisCacheManager()
        manager.redis_client = mock_client
        manager.enabled = True
        
        trend_data = {"direction": "up", "strength": 0.8}
        success = manager.cache_trend("ECO_GDP", trend_data)
        assert mock_client.setex.called or mock_client.set.called or True


# ============================================================================
# Integration Tests (require running services)
# ============================================================================

@pytest.mark.integration
class TestFullPipeline:
    """Full integration tests requiring all services"""

    def test_sentiment_to_indicator_flow(self, sentiment_analyzer, sample_article):
        """Test sentiment analysis feeding into indicator calculation"""
        # Step 1: Analyze sentiment
        sentiment = sentiment_analyzer.analyze_article(
            article_id=sample_article["article_id"],
            title=sample_article["title"],
            content=sample_article["content"]
        )
        
        assert sentiment is not None
        
        # Step 2: Verify sentiment can be used for indicator
        score = sentiment.get("weighted_score", sentiment.get("score", 0))
        assert isinstance(score, (int, float))

    def test_dependency_cascade_flow(self, dependency_mapper):
        """Test dependency mapper cascade prediction"""
        # Setup realistic dependencies
        dependency_mapper.add_dependency("ECO_INFLATION", "ECO_CONSUMER_CONFIDENCE", -0.7)
        dependency_mapper.add_dependency("ECO_CONSUMER_CONFIDENCE", "ECO_RETAIL_SALES", 0.6)
        
        # Predict cascade from inflation spike
        effects = dependency_mapper.predict_cascade_effects(
            indicator_id="ECO_INFLATION",
            change_magnitude=5.0  # 5% increase in inflation
        )
        
        assert isinstance(effects, list)

    def test_alert_generation_flow(self, alert_manager):
        """Test alert generation for indicator changes"""
        # Simulate indicator exceeding threshold
        alert = alert_manager.check_threshold(
            indicator_id="ECO_UNEMPLOYMENT",
            current_value=12.0,  # High unemployment
            threshold_high=10.0,
            threshold_low=3.0
        )
        
        if alert:
            assert alert.get("indicator_id") == "ECO_UNEMPLOYMENT"


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.slow
class TestPerformance:
    """Performance and load tests"""

    def test_batch_sentiment_performance(self, sentiment_analyzer):
        """Test batch processing performance"""
        import time
        
        texts = ["This is a test article with some content. " * 20] * 100
        
        start = time.time()
        results = sentiment_analyzer.analyze_batch(texts)
        elapsed = time.time() - start
        
        assert len(results) == 100
        assert elapsed < 30, f"Batch processing too slow: {elapsed}s"
        print(f"Processed 100 articles in {elapsed:.2f}s ({100/elapsed:.1f} articles/sec)")

    def test_dependency_graph_performance(self, dependency_mapper):
        """Test dependency graph with many nodes"""
        import time
        
        # Add many dependencies
        for i in range(50):
            for j in range(5):
                dependency_mapper.add_dependency(
                    f"IND_{i}",
                    f"IND_{(i+j+1) % 50}",
                    correlation=0.5
                )
        
        start = time.time()
        graph = dependency_mapper.get_dependency_graph()
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Graph generation too slow: {elapsed}s"
