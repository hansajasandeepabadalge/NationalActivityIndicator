"""Redis caching layer for API responses"""

import redis
import json
from typing import Optional, Any
from app.core.config import settings


class RedisCache:
    """Redis caching layer for API responses"""

    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS
            )
            self.default_ttl = settings.API_RESPONSE_CACHE_TTL
            # Test connection
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            self.enabled = False

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cached value"""
        if not self.enabled:
            return False

        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete cached value"""
        if not self.enabled:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis clear error: {e}")
            return 0


# Singleton instance
cache = RedisCache()
