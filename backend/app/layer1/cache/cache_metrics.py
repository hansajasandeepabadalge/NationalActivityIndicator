"""
Cache Metrics Tracking

Tracks cache performance metrics including hit rates, miss reasons,
and bandwidth savings. Provides insights for optimization.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache statistics snapshot"""
    total_hits: int
    total_misses: int
    hit_rate: float
    misses_by_reason: Dict[str, int]
    hits_by_source: Dict[str, int]
    misses_by_source: Dict[str, int]
    estimated_bandwidth_saved_kb: float
    estimated_time_saved_seconds: float
    period_start: str
    period_end: str


class CacheMetrics:
    """
    Tracks and reports cache performance metrics.
    
    Metrics tracked:
    - Hit/miss rates overall and per source
    - Miss reasons distribution
    - Bandwidth savings estimation
    - Time savings estimation
    """
    
    # Redis key prefixes
    KEY_PREFIX = "cache:metrics"
    
    # Estimated savings per cache hit
    ESTIMATED_BANDWIDTH_PER_HIT_KB = 150  # Average page size
    ESTIMATED_TIME_PER_HIT_SECONDS = 2.5  # Average scrape time
    
    def __init__(self, redis_client=None):
        """
        Initialize metrics tracker.
        
        Args:
            redis_client: Redis client (auto-loads if None)
        """
        self.redis = redis_client
    
    async def _get_redis(self):
        """Lazy load Redis client"""
        if self.redis is None:
            from app.db.redis_client import get_redis
            self.redis = get_redis()
        return self.redis
    
    def _make_key(self, *parts) -> str:
        """Generate Redis key"""
        return ":".join([self.KEY_PREFIX] + list(parts))
    
    # ==========================================
    # Recording Methods
    # ==========================================
    
    async def record_hit(self, source_name: str, saved_articles: int = 0):
        """
        Record a cache hit.
        
        Args:
            source_name: Name of the source
            saved_articles: Number of articles that didn't need re-scraping
        """
        redis = await self._get_redis()
        
        try:
            # Increment counters
            await redis.incr(self._make_key("hits", "total"))
            await redis.incr(self._make_key("hits", "source", source_name))
            
            # Track daily stats
            today = datetime.utcnow().strftime("%Y-%m-%d")
            await redis.incr(self._make_key("daily", today, "hits"))
            
            # Track articles saved
            if saved_articles > 0:
                await redis.incrby(
                    self._make_key("saved_articles", "total"),
                    saved_articles
                )
            
            logger.debug(f"[CacheMetrics] Recorded hit for {source_name}")
            
        except Exception as e:
            logger.warning(f"[CacheMetrics] Failed to record hit: {e}")
    
    async def record_miss(
        self, 
        source_name: str, 
        reason: str,
        check_duration_ms: int = 0
    ):
        """
        Record a cache miss with reason.
        
        Args:
            source_name: Name of the source
            reason: Reason for cache miss
            check_duration_ms: Time spent checking cache
        """
        redis = await self._get_redis()
        
        try:
            # Increment counters
            await redis.incr(self._make_key("misses", "total"))
            await redis.incr(self._make_key("misses", "source", source_name))
            await redis.incr(self._make_key("misses", "reason", reason))
            
            # Track daily stats
            today = datetime.utcnow().strftime("%Y-%m-%d")
            await redis.incr(self._make_key("daily", today, "misses"))
            
            # Track check duration for optimization
            if check_duration_ms > 0:
                await redis.lpush(
                    self._make_key("check_times", source_name),
                    str(check_duration_ms)
                )
                # Keep only last 100 entries
                await redis.ltrim(self._make_key("check_times", source_name), 0, 99)
            
            logger.debug(f"[CacheMetrics] Recorded miss for {source_name}: {reason}")
            
        except Exception as e:
            logger.warning(f"[CacheMetrics] Failed to record miss: {e}")
    
    async def record_scrape_completed(
        self,
        source_name: str,
        articles_count: int,
        duration_ms: int,
        from_cache: bool
    ):
        """
        Record completed scrape (cached or fresh).
        
        Args:
            source_name: Name of the source
            articles_count: Number of articles
            duration_ms: Scrape duration
            from_cache: Whether articles came from cache
        """
        redis = await self._get_redis()
        
        try:
            # Track scrape duration
            await redis.lpush(
                self._make_key("scrape_times", source_name),
                str(duration_ms)
            )
            await redis.ltrim(self._make_key("scrape_times", source_name), 0, 99)
            
            # Track total operations
            await redis.incr(self._make_key("scrapes", "total"))
            
            if from_cache:
                await redis.incr(self._make_key("scrapes", "from_cache"))
            else:
                await redis.incr(self._make_key("scrapes", "fresh"))
            
        except Exception as e:
            logger.warning(f"[CacheMetrics] Failed to record scrape: {e}")
    
    # ==========================================
    # Reporting Methods
    # ==========================================
    
    async def get_stats(self, period_days: int = 7) -> CacheStats:
        """
        Get cache statistics for specified period.
        
        Args:
            period_days: Number of days to include
            
        Returns:
            CacheStats object with all metrics
        """
        redis = await self._get_redis()
        
        try:
            # Get totals
            total_hits = int(await redis.get(self._make_key("hits", "total")) or 0)
            total_misses = int(await redis.get(self._make_key("misses", "total")) or 0)
            
            # Calculate hit rate
            total = total_hits + total_misses
            hit_rate = (total_hits / total * 100) if total > 0 else 0.0
            
            # Get misses by reason
            misses_by_reason = await self._get_misses_by_reason()
            
            # Get per-source stats
            hits_by_source = await self._get_hits_by_source()
            misses_by_source = await self._get_misses_by_source()
            
            # Calculate savings
            bandwidth_saved = total_hits * self.ESTIMATED_BANDWIDTH_PER_HIT_KB
            time_saved = total_hits * self.ESTIMATED_TIME_PER_HIT_SECONDS
            
            # Period info
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=period_days)
            
            return CacheStats(
                total_hits=total_hits,
                total_misses=total_misses,
                hit_rate=round(hit_rate, 2),
                misses_by_reason=misses_by_reason,
                hits_by_source=hits_by_source,
                misses_by_source=misses_by_source,
                estimated_bandwidth_saved_kb=round(bandwidth_saved, 2),
                estimated_time_saved_seconds=round(time_saved, 2),
                period_start=period_start.isoformat(),
                period_end=period_end.isoformat()
            )
            
        except Exception as e:
            logger.error(f"[CacheMetrics] Error getting stats: {e}")
            return CacheStats(
                total_hits=0,
                total_misses=0,
                hit_rate=0.0,
                misses_by_reason={},
                hits_by_source={},
                misses_by_source={},
                estimated_bandwidth_saved_kb=0.0,
                estimated_time_saved_seconds=0.0,
                period_start=datetime.utcnow().isoformat(),
                period_end=datetime.utcnow().isoformat()
            )
    
    async def _get_misses_by_reason(self) -> Dict[str, int]:
        """Get miss counts by reason"""
        redis = await self._get_redis()
        
        reasons = [
            "ttl_expired",
            "no_previous_scrape",
            "etag_changed",
            "last_modified_changed",
            "signature_changed",
            "no_cached_headers",
            "force_requested",
            "error"
        ]
        
        result = {}
        for reason in reasons:
            count = await redis.get(self._make_key("misses", "reason", reason))
            if count:
                result[reason] = int(count)
        
        return result
    
    async def _get_hits_by_source(self) -> Dict[str, int]:
        """Get hit counts by source"""
        redis = await self._get_redis()
        
        # Scan for source keys
        result = {}
        pattern = self._make_key("hits", "source", "*")
        
        try:
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                for key in keys:
                    source = key.split(":")[-1]
                    count = await redis.get(key)
                    if count:
                        result[source] = int(count)
                if cursor == 0:
                    break
        except:
            pass
        
        return result
    
    async def _get_misses_by_source(self) -> Dict[str, int]:
        """Get miss counts by source"""
        redis = await self._get_redis()
        
        result = {}
        pattern = self._make_key("misses", "source", "*")
        
        try:
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                for key in keys:
                    source = key.split(":")[-1]
                    count = await redis.get(key)
                    if count:
                        result[source] = int(count)
                if cursor == 0:
                    break
        except:
            pass
        
        return result
    
    async def get_source_stats(self, source_name: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            Dict with source-specific metrics
        """
        redis = await self._get_redis()
        
        try:
            hits = int(await redis.get(self._make_key("hits", "source", source_name)) or 0)
            misses = int(await redis.get(self._make_key("misses", "source", source_name)) or 0)
            
            # Get average check times
            check_times = await redis.lrange(
                self._make_key("check_times", source_name), 0, -1
            )
            avg_check_time = 0
            if check_times:
                avg_check_time = sum(int(t) for t in check_times) / len(check_times)
            
            # Get average scrape times
            scrape_times = await redis.lrange(
                self._make_key("scrape_times", source_name), 0, -1
            )
            avg_scrape_time = 0
            if scrape_times:
                avg_scrape_time = sum(int(t) for t in scrape_times) / len(scrape_times)
            
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0.0
            
            return {
                "source_name": source_name,
                "hits": hits,
                "misses": misses,
                "hit_rate": round(hit_rate, 2),
                "avg_check_time_ms": round(avg_check_time, 2),
                "avg_scrape_time_ms": round(avg_scrape_time, 2),
                "estimated_bandwidth_saved_kb": hits * self.ESTIMATED_BANDWIDTH_PER_HIT_KB,
                "estimated_time_saved_seconds": hits * self.ESTIMATED_TIME_PER_HIT_SECONDS
            }
            
        except Exception as e:
            logger.error(f"[CacheMetrics] Error getting source stats: {e}")
            return {
                "source_name": source_name,
                "error": str(e)
            }
    
    async def get_daily_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get daily cache performance trend.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of daily stat dictionaries
        """
        redis = await self._get_redis()
        
        trend = []
        today = datetime.utcnow()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            
            try:
                hits = int(await redis.get(self._make_key("daily", date, "hits")) or 0)
                misses = int(await redis.get(self._make_key("daily", date, "misses")) or 0)
                total = hits + misses
                hit_rate = (hits / total * 100) if total > 0 else 0.0
                
                trend.append({
                    "date": date,
                    "hits": hits,
                    "misses": misses,
                    "total": total,
                    "hit_rate": round(hit_rate, 2)
                })
            except:
                trend.append({
                    "date": date,
                    "hits": 0,
                    "misses": 0,
                    "total": 0,
                    "hit_rate": 0.0
                })
        
        return trend
    
    async def reset_stats(self):
        """Reset all cache metrics (use with caution)"""
        redis = await self._get_redis()
        
        try:
            # Find all cache:metrics keys
            pattern = f"{self.KEY_PREFIX}:*"
            cursor = 0
            keys_to_delete = []
            
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                keys_to_delete.extend(keys)
                if cursor == 0:
                    break
            
            if keys_to_delete:
                await redis.delete(*keys_to_delete)
                logger.info(f"[CacheMetrics] Reset {len(keys_to_delete)} metric keys")
            
            return True
            
        except Exception as e:
            logger.error(f"[CacheMetrics] Error resetting stats: {e}")
            return False
    
    def to_dict(self, stats: CacheStats) -> Dict[str, Any]:
        """Convert CacheStats to dictionary"""
        return asdict(stats)


# Global instance
_cache_metrics: Optional[CacheMetrics] = None


def get_cache_metrics() -> CacheMetrics:
    """Get global cache metrics instance"""
    global _cache_metrics
    if _cache_metrics is None:
        _cache_metrics = CacheMetrics()
    return _cache_metrics
