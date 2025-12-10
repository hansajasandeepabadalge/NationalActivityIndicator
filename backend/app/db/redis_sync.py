"""
Synchronous Redis connection management
Use this for Layer 2 processing tasks that require sync caching
"""
from redis import Redis, ConnectionPool
from app.core.config import settings
import json
import logging
from typing import Any, Optional
from datetime import timedelta

logger = logging.getLogger(__name__)


class RedisCacheSync:
    """
    Synchronous Redis client for Layer 2 caching
    Use this for caching indicator values, ML model predictions, etc.
    """

    def __init__(self):
        self.pool: ConnectionPool = None
        self.client: Redis = None

    def connect(self):
        """Connect to Redis using synchronous client"""
        try:
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True
            )
            self.client = Redis(connection_pool=self.pool)
            # Test connection
            self.client.ping()
            logger.info("Synchronous Redis client connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect synchronous Redis client: {e}")
            raise

    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            logger.info("Synchronous Redis client closed")
        if self.pool:
            self.pool.disconnect()

    def get_client(self) -> Redis:
        """Get Redis client"""
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client

    # Helper methods for common operations

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a key-value pair with optional TTL

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: settings.REDIS_DEFAULT_TTL)
        """
        try:
            serialized = json.dumps(value)
            ttl = ttl or settings.REDIS_DEFAULT_TTL
            return self.client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value (JSON deserialized) or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        try:
            return self.client.delete(key) > 0
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern

        Args:
            pattern: Pattern to match (e.g., "indicator:*")

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0

    # Layer 2 specific caching methods

    def cache_indicator_value(self, indicator_id: str, value: float, ttl: int = 300) -> bool:
        """Cache current indicator value"""
        key = f"indicator:current:{indicator_id}"
        return self.set(key, {"value": value, "indicator_id": indicator_id}, ttl)

    def get_indicator_value(self, indicator_id: str) -> Optional[float]:
        """Get cached indicator value"""
        key = f"indicator:current:{indicator_id}"
        data = self.get(key)
        return data.get("value") if data else None

    def cache_ml_prediction(self, article_id: str, predictions: dict, ttl: int = 3600) -> bool:
        """Cache ML classification predictions"""
        key = f"ml:prediction:{article_id}"
        return self.set(key, predictions, ttl)

    def get_ml_prediction(self, article_id: str) -> Optional[dict]:
        """Get cached ML prediction"""
        key = f"ml:prediction:{article_id}"
        return self.get(key)

    def cache_trend_analysis(self, indicator_id: str, trend_data: dict, ttl: int = 1800) -> bool:
        """Cache trend analysis results"""
        key = f"trend:analysis:{indicator_id}"
        return self.set(key, trend_data, ttl)

    def get_trend_analysis(self, indicator_id: str) -> Optional[dict]:
        """Get cached trend analysis"""
        key = f"trend:analysis:{indicator_id}"
        return self.get(key)

    def invalidate_indicator(self, indicator_id: str) -> int:
        """Invalidate all caches related to an indicator"""
        pattern = f"*:{indicator_id}"
        return self.clear_pattern(pattern)


# Singleton instance
redis_cache_sync = RedisCacheSync()


def get_redis_sync() -> Redis:
    """Dependency for getting synchronous Redis client"""
    return redis_cache_sync.get_client()
