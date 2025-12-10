"""
manager.py - Cache Manager for Layer 4

Provides caching functionality for LLM responses to reduce API costs
and improve response times.
"""

import json
import logging
import hashlib
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Try to import redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class CacheManager:
    """
    Manages caching of LLM responses
    
    Falls back to in-memory cache if Redis is not available.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self._memory_cache: Dict[str, str] = {}
        
        if REDIS_AVAILABLE:
            try:
                if redis_url:
                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                else:
                    # Try to get from settings, fallback to localhost
                    try:
                        from app.core.config import settings
                        redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
                        self.redis_client = redis.from_url(redis_url, decode_responses=True)
                    except Exception:
                        self.redis_client = redis.Redis(
                            host='localhost', 
                            port=6379, 
                            db=0, 
                            decode_responses=True
                        )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed, using in-memory cache: {e}")
                self.redis_client = None
        else:
            logger.info("Redis not available, using in-memory cache")

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value"""
        try:
            if self.redis_client:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
            else:
                # In-memory fallback
                val = self._memory_cache.get(key)
                if val:
                    return json.loads(val)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None

    async def set(self, key: str, value: Dict[str, Any], ttl: int = 3600):
        """Set cached value with TTL"""
        try:
            json_value = json.dumps(value)
            if self.redis_client:
                self.redis_client.setex(key, ttl, json_value)
            else:
                # In-memory fallback (no TTL support)
                self._memory_cache[key] = json_value
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    async def delete(self, key: str):
        """Delete a cached value"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self._memory_cache.pop(key, None)
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")

    async def clear_prefix(self, prefix: str):
        """Clear all keys with a given prefix"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(f"{prefix}*")
                if keys:
                    self.redis_client.delete(*keys)
            else:
                keys_to_delete = [k for k in self._memory_cache if k.startswith(prefix)]
                for k in keys_to_delete:
                    del self._memory_cache[k]
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")

    def generate_key(self, prefix: str, data: Any) -> str:
        """Generate reliable cache key from data"""
        try:
            s = json.dumps(data, sort_keys=True, default=str)
        except (TypeError, ValueError):
            s = str(data)
        h = hashlib.md5(s.encode()).hexdigest()
        return f"layer4:{prefix}:{h}"

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if self.redis_client:
            try:
                self.redis_client.ping()
                return True
            except Exception:
                return False
        return False
