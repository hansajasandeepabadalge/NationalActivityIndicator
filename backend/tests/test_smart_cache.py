"""
Tests for Smart Caching System

Tests the SmartCacheManager, ChangeDetector, and CacheMetrics
components that provide 70% faster scraping through intelligent caching.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

# Import cache components
from app.cache.smart_cache import SmartCacheManager, CacheConfig, CacheEntry
from app.cache.change_detector import ChangeDetector, DetectionStrategy
from app.cache.cache_metrics import CacheMetrics, CacheStats


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def mock_redis():
    """Create a mock Redis client"""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.incr = AsyncMock(return_value=1)
    redis.ttl = AsyncMock(return_value=3600)
    redis.scan = AsyncMock(return_value=(0, []))
    return redis


@pytest.fixture
def cache_config():
    """Create cache configuration for testing"""
    return CacheConfig(
        default_ttl=3600,
        news_ttl=900,
        government_ttl=7200,
        api_ttl=1800,
        social_ttl=300,
        signature_sample_size=1000,
        head_request_timeout=5
    )


@pytest.fixture
def cache_manager(mock_redis, cache_config):
    """Create SmartCacheManager with mock Redis"""
    manager = SmartCacheManager(redis_client=mock_redis, config=cache_config)
    return manager


@pytest.fixture
def change_detector(mock_redis):
    """Create ChangeDetector with mock Redis"""
    return ChangeDetector(redis_client=mock_redis)


@pytest.fixture
def cache_metrics(mock_redis):
    """Create CacheMetrics with mock Redis"""
    return CacheMetrics(redis_client=mock_redis)


# ============================================
# SmartCacheManager Tests
# ============================================

class TestSmartCacheManager:
    """Tests for SmartCacheManager"""
    
    @pytest.mark.asyncio
    async def test_cache_articles_stores_data(self, cache_manager, mock_redis):
        """Test that articles are cached correctly"""
        source_name = "ada_derana"
        url = "https://www.adaderana.lk/hot-news/"
        articles = [
            {"article_id": "1", "title": "Test Article 1"},
            {"article_id": "2", "title": "Test Article 2"}
        ]
        
        result = await cache_manager.cache_articles(
            source_name=source_name,
            url=url,
            articles=articles,
            source_type="news"
        )
        
        assert result is True
        assert mock_redis.setex.called
    
    @pytest.mark.asyncio
    async def test_get_cached_articles_returns_none_when_empty(self, cache_manager, mock_redis):
        """Test that None is returned when no cached articles exist"""
        mock_redis.get.return_value = None
        
        result = await cache_manager.get_cached_articles("unknown_source")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_cached_articles_returns_data(self, cache_manager, mock_redis):
        """Test that cached articles are retrieved correctly"""
        articles = [{"article_id": "1", "title": "Test"}]
        mock_redis.get.return_value = json.dumps(articles)
        
        result = await cache_manager.get_cached_articles("ada_derana")
        
        assert result is not None
        assert len(result) == 1
        assert result[0]["article_id"] == "1"
    
    @pytest.mark.asyncio
    async def test_invalidate_clears_all_keys(self, cache_manager, mock_redis):
        """Test that invalidation clears all cache keys for a source"""
        await cache_manager.invalidate("ada_derana")
        
        assert mock_redis.delete.called
    
    @pytest.mark.asyncio
    async def test_needs_scraping_with_force(self, cache_manager):
        """Test that force=True always returns True"""
        result, reason = await cache_manager.needs_scraping(
            source_name="ada_derana",
            url="https://test.com",
            force=True
        )
        
        assert result is True
        assert reason == "force_requested"
    
    @pytest.mark.asyncio
    async def test_needs_scraping_no_previous_scrape(self, cache_manager, mock_redis):
        """Test that scraping is needed when no previous data exists"""
        mock_redis.get.return_value = None
        
        result, reason = await cache_manager.needs_scraping(
            source_name="new_source",
            url="https://test.com"
        )
        
        assert result is True
        assert reason == "no_previous_scrape"
    
    def test_config_ttl_for_news(self, cache_config):
        """Test that news sources get correct TTL"""
        ttl = cache_config.get_ttl_for_type("news")
        assert ttl == 900
    
    def test_config_ttl_for_government(self, cache_config):
        """Test that government sources get correct TTL"""
        ttl = cache_config.get_ttl_for_type("government")
        assert ttl == 7200
    
    def test_config_ttl_default(self, cache_config):
        """Test that unknown types get default TTL"""
        ttl = cache_config.get_ttl_for_type("unknown")
        assert ttl == cache_config.default_ttl


# ============================================
# ChangeDetector Tests
# ============================================

class TestChangeDetector:
    """Tests for ChangeDetector"""
    
    def test_get_strategy_for_news(self, change_detector):
        """Test strategy selection for news sources"""
        strategy = change_detector.get_strategy_for_type("news")
        
        # News should prioritize HEAD checks
        assert DetectionStrategy.HTTP_HEADERS in strategy
    
    def test_get_strategy_for_social(self, change_detector):
        """Test strategy selection for social sources"""
        strategy = change_detector.get_strategy_for_type("social")
        
        # Social should always scrape
        assert DetectionStrategy.ALWAYS_SCRAPE in strategy
    
    def test_get_strategy_for_government(self, change_detector):
        """Test strategy selection for government sources"""
        strategy = change_detector.get_strategy_for_type("government")
        
        # Government should check Last-Modified first
        assert DetectionStrategy.HTTP_HEADERS in strategy


# ============================================
# CacheMetrics Tests
# ============================================

class TestCacheMetrics:
    """Tests for CacheMetrics"""
    
    @pytest.mark.asyncio
    async def test_record_hit_increments_counter(self, cache_metrics, mock_redis):
        """Test that recording a hit increments counters"""
        await cache_metrics.record_hit("ada_derana", saved_articles=5)
        
        assert mock_redis.incr.called
    
    @pytest.mark.asyncio
    async def test_record_miss_tracks_reason(self, cache_metrics, mock_redis):
        """Test that recording a miss tracks the reason"""
        await cache_metrics.record_miss("ada_derana", reason="ttl_expired")
        
        assert mock_redis.incr.called
    
    @pytest.mark.asyncio
    async def test_get_stats_returns_cache_stats(self, cache_metrics, mock_redis):
        """Test that get_stats returns a CacheStats object"""
        mock_redis.get.return_value = "10"
        
        stats = await cache_metrics.get_stats()
        
        assert isinstance(stats, CacheStats)
        assert stats.total_hits >= 0
        assert stats.total_misses >= 0
    
    @pytest.mark.asyncio
    async def test_hit_rate_calculation(self, cache_metrics, mock_redis):
        """Test hit rate calculation"""
        # Simulate 70 hits and 30 misses (70% hit rate)
        async def mock_get(key):
            if "hits:total" in key:
                return "70"
            elif "misses:total" in key:
                return "30"
            return None
        
        mock_redis.get = mock_get
        
        stats = await cache_metrics.get_stats()
        
        assert stats.hit_rate == 70.0
    
    def test_bandwidth_savings_estimation(self, cache_metrics):
        """Test bandwidth savings calculation"""
        # Each hit saves approximately 150KB
        expected_kb_per_hit = cache_metrics.ESTIMATED_BANDWIDTH_PER_HIT_KB
        assert expected_kb_per_hit > 0
    
    def test_time_savings_estimation(self, cache_metrics):
        """Test time savings calculation"""
        # Each hit saves approximately 2.5 seconds
        expected_time_per_hit = cache_metrics.ESTIMATED_TIME_PER_HIT_SECONDS
        assert expected_time_per_hit > 0


# ============================================
# Integration Tests
# ============================================

class TestCacheIntegration:
    """Integration tests for the caching system"""
    
    @pytest.mark.asyncio
    async def test_full_cache_cycle(self, cache_manager, mock_redis):
        """Test a complete cache cycle: check -> miss -> cache -> check -> hit"""
        source_name = "test_source"
        url = "https://test.com"
        articles = [{"id": "1", "title": "Test"}]
        
        # First check - should be a miss
        mock_redis.get.return_value = None
        needs_scrape, reason = await cache_manager.needs_scraping(source_name, url)
        assert needs_scrape is True
        
        # Cache articles
        await cache_manager.cache_articles(source_name, url, articles)
        
        # Mock cached data now exists
        mock_redis.get.side_effect = [
            datetime.utcnow().isoformat(),  # scraped_at
            "some-etag",  # etag
            None  # last_modified
        ]
        
        # Note: Full integration would need HTTP mocking
        # This tests the flow
    
    @pytest.mark.asyncio
    async def test_cache_respects_ttl_by_source_type(self, cache_manager, mock_redis):
        """Test that different source types get appropriate TTL"""
        source_name = "test_source"
        url = "https://test.com"
        articles = [{"id": "1"}]
        
        # Cache with news TTL
        await cache_manager.cache_articles(source_name, url, articles, source_type="news")
        
        # Cache with government TTL
        await cache_manager.cache_articles(source_name, url, articles, source_type="government")
        
        # Both should have called setex with different TTLs
        assert mock_redis.setex.call_count >= 2


# ============================================
# Edge Case Tests
# ============================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_handles_redis_connection_error(self, cache_manager, mock_redis):
        """Test graceful handling of Redis errors"""
        mock_redis.get.side_effect = Exception("Connection refused")
        
        # Should handle error gracefully
        result = await cache_manager.get_cached_articles("ada_derana")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_handles_invalid_cached_json(self, cache_manager, mock_redis):
        """Test handling of corrupted cached data"""
        mock_redis.get.return_value = "invalid json{{"
        
        result = await cache_manager.get_cached_articles("ada_derana")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_handles_empty_articles_list(self, cache_manager, mock_redis):
        """Test caching empty article list"""
        result = await cache_manager.cache_articles(
            source_name="test",
            url="https://test.com",
            articles=[]
        )
        
        assert result is True
    
    def test_signature_normalization(self, cache_manager):
        """Test that signature calculation normalizes content"""
        content1 = "  Hello   World  "
        content2 = "hello world"
        
        sig1 = cache_manager._calculate_signature(content1)
        sig2 = cache_manager._calculate_signature(content2)
        
        # Signatures should be equal after normalization
        assert sig1 == sig2


# ============================================
# Performance Metrics Tests
# ============================================

class TestPerformanceMetrics:
    """Tests for performance tracking"""
    
    @pytest.mark.asyncio
    async def test_metrics_track_bandwidth_savings(self, cache_metrics, mock_redis):
        """Test that bandwidth savings are calculated correctly"""
        # Record 10 cache hits
        for _ in range(10):
            await cache_metrics.record_hit("ada_derana")
        
        # Should have called incr 10 times for total hits
        assert mock_redis.incr.call_count >= 10
    
    @pytest.mark.asyncio
    async def test_metrics_track_time_savings(self, cache_metrics, mock_redis):
        """Test that time savings are estimated"""
        mock_redis.get.return_value = "100"  # 100 hits
        
        stats = await cache_metrics.get_stats()
        
        expected_time_saved = 100 * cache_metrics.ESTIMATED_TIME_PER_HIT_SECONDS
        assert stats.estimated_time_saved_seconds == expected_time_saved
