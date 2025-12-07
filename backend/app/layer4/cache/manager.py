"""
manager.py - Cache Manager for Layer 4
"""

import redis
import json
import logging
import hashlib
from typing import Optional, Dict, Any, Union
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages caching of LLM responses
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        # Use settings if available, otherwise default to localhost (or None if testing)
        if redis_url:
            self.redis = redis.from_url(redis_url, decode_responses=True)
        else:
            # Fallback to local
            self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value"""
        try:
            val = self.redis.get(key)
            if val:
                return json.loads(val)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: int = 3600):
        """Set cached value"""
        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    def generate_key(self, prefix: str, data: Any) -> str:
        """Generate reliable cache key"""
        s = json.dumps(data, sort_keys=True)
        h = hashlib.md5(s.encode()).hexdigest()
        return f"layer4:{prefix}:{h}"
