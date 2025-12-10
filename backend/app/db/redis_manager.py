"""
Redis Cache Manager - High-level caching utilities for indicators.

Provides:
- Indicator value caching
- Alert caching
- Trend caching
- TTL management
"""
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from redis import Redis
from app.core.config import settings


class RedisCacheManager:
    """
    High-level Redis caching for indicator data.
    
    Key patterns:
    - indicator:current:{id} - Current indicator value
    - indicator:history:{id} - Recent historical values
    - alert:active:{id} - Active alerts
    - trend:{id} - Trend analysis cache
    """
    
    # TTL defaults (seconds)
    TTL_CURRENT_VALUE = 300      # 5 minutes
    TTL_HISTORY = 3600           # 1 hour
    TTL_TREND = 1800             # 30 minutes
    TTL_ALERT = 86400            # 24 hours
    
    def __init__(self, redis_url: str = None):
        url = redis_url or settings.REDIS_URL
        self._redis = Redis.from_url(url, decode_responses=True)
    
    # === Indicator Values ===
    
    def set_indicator_value(self, indicator_id: str, value: float, 
                            metadata: Dict = None, ttl: int = None):
        """Cache current indicator value"""
        key = f"indicator:current:{indicator_id}"
        data = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self._redis.setex(key, ttl or self.TTL_CURRENT_VALUE, json.dumps(data))
    
    def get_indicator_value(self, indicator_id: str) -> Optional[Dict]:
        """Get cached indicator value"""
        key = f"indicator:current:{indicator_id}"
        data = self._redis.get(key)
        return json.loads(data) if data else None
    
    def get_all_indicator_values(self, indicator_ids: List[str]) -> Dict[str, Dict]:
        """Get multiple indicator values"""
        result = {}
        for ind_id in indicator_ids:
            val = self.get_indicator_value(ind_id)
            if val:
                result[ind_id] = val
        return result
    
    def invalidate_indicator(self, indicator_id: str):
        """Clear cached indicator value"""
        self._redis.delete(f"indicator:current:{indicator_id}")
    
    # === Historical Values ===
    
    def push_historical_value(self, indicator_id: str, value: float, 
                               max_entries: int = 100):
        """Add value to historical list"""
        key = f"indicator:history:{indicator_id}"
        data = {"value": value, "timestamp": datetime.utcnow().isoformat()}
        self._redis.lpush(key, json.dumps(data))
        self._redis.ltrim(key, 0, max_entries - 1)
        self._redis.expire(key, self.TTL_HISTORY)
    
    def get_historical_values(self, indicator_id: str, count: int = 50) -> List[Dict]:
        """Get recent historical values"""
        key = f"indicator:history:{indicator_id}"
        data = self._redis.lrange(key, 0, count - 1)
        return [json.loads(d) for d in data]
    
    # === Trends ===
    
    def set_trend(self, indicator_id: str, trend_data: Dict, ttl: int = None):
        """Cache trend analysis"""
        key = f"trend:{indicator_id}"
        self._redis.setex(key, ttl or self.TTL_TREND, json.dumps(trend_data))
    
    def get_trend(self, indicator_id: str) -> Optional[Dict]:
        """Get cached trend"""
        key = f"trend:{indicator_id}"
        data = self._redis.get(key)
        return json.loads(data) if data else None
    
    # === Alerts ===
    
    def set_alert(self, alert_id: str, alert_data: Dict, ttl: int = None):
        """Cache alert"""
        key = f"alert:{alert_id}"
        self._redis.setex(key, ttl or self.TTL_ALERT, json.dumps(alert_data))
        # Also add to active alerts set
        self._redis.sadd("alerts:active", alert_id)
    
    def get_alert(self, alert_id: str) -> Optional[Dict]:
        """Get alert by ID"""
        key = f"alert:{alert_id}"
        data = self._redis.get(key)
        return json.loads(data) if data else None
    
    def get_active_alert_ids(self) -> List[str]:
        """Get all active alert IDs"""
        return list(self._redis.smembers("alerts:active"))
    
    def remove_alert(self, alert_id: str):
        """Remove alert from cache"""
        self._redis.delete(f"alert:{alert_id}")
        self._redis.srem("alerts:active", alert_id)
    
    # === Utilities ===
    
    def clear_all_indicators(self):
        """Clear all indicator caches"""
        for key in self._redis.scan_iter("indicator:*"):
            self._redis.delete(key)
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "indicator_values": len(list(self._redis.scan_iter("indicator:current:*"))),
            "history_entries": len(list(self._redis.scan_iter("indicator:history:*"))),
            "trends": len(list(self._redis.scan_iter("trend:*"))),
            "alerts": self._redis.scard("alerts:active")
        }
    
    def ping(self) -> bool:
        """Check Redis connection"""
        try:
            return self._redis.ping()
        except:
            return False


# Singleton instance
_cache_manager: Optional[RedisCacheManager] = None

def get_cache_manager() -> RedisCacheManager:
    """Get or create cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = RedisCacheManager()
    return _cache_manager
