"""
Layer 4: Redis Cache Manager for Fast Insight Retrieval

Handles caching of:
- Company insights
- Narratives
- Portfolio metrics
- Detection results
"""
from typing import Optional, List, Dict, Any
import json
import logging
from redis import Redis
from datetime import timedelta

logger = logging.getLogger(__name__)


class InsightCacheManager:
    """
    Redis caching for Layer 4 insights

    Features:
    - Fast retrieval of current insights
    - TTL-based expiration
    - Automatic invalidation on updates
    - Portfolio metrics caching
    """

    def __init__(self, redis_client: Redis, default_ttl: int = 900):
        """
        Initialize cache manager

        Args:
            redis_client: Redis client instance
            default_ttl: Default TTL in seconds (default: 900 = 15 minutes)
        """
        self.redis = redis_client
        self.default_ttl = default_ttl

    def cache_company_insights(
        self,
        company_id: str,
        insights: List[Dict],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache company's current insights

        Args:
            company_id: Company identifier
            insights: List of insight dictionaries
            ttl: Time-to-live in seconds (None = use default)

        Returns:
            True if successful
        """
        try:
            key = f"cache:insights:company:{company_id}:current"
            ttl_seconds = ttl or self.default_ttl

            # Serialize to JSON
            data = json.dumps(insights, default=str)

            # Store with TTL
            self.redis.setex(key, ttl_seconds, data)

            logger.debug(f"Cached {len(insights)} insights for company {company_id} (TTL: {ttl_seconds}s)")
            return True

        except Exception as e:
            logger.error(f"Failed to cache insights for company {company_id}: {e}")
            return False

    def get_cached_insights(self, company_id: str) -> Optional[List[Dict]]:
        """
        Retrieve cached insights for a company

        Args:
            company_id: Company identifier

        Returns:
            List of insight dictionaries or None if not cached
        """
        try:
            key = f"cache:insights:company:{company_id}:current"
            data = self.redis.get(key)

            if data:
                insights = json.loads(data)
                logger.debug(f"Retrieved {len(insights)} cached insights for company {company_id}")
                return insights
            else:
                logger.debug(f"No cached insights found for company {company_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve cached insights for company {company_id}: {e}")
            return None

    def cache_narrative(
        self,
        insight_id: int,
        narrative: Dict,
        ttl: int = 3600  # 1 hour default
    ) -> bool:
        """
        Cache generated narrative

        Args:
            insight_id: PostgreSQL insight_id
            narrative: Narrative dictionary
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            key = f"cache:narrative:insight:{insight_id}"
            data = json.dumps(narrative, default=str)

            self.redis.setex(key, ttl, data)

            logger.debug(f"Cached narrative for insight {insight_id} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Failed to cache narrative for insight {insight_id}: {e}")
            return False

    def get_cached_narrative(self, insight_id: int) -> Optional[Dict]:
        """
        Retrieve cached narrative

        Args:
            insight_id: PostgreSQL insight_id

        Returns:
            Narrative dictionary or None
        """
        try:
            key = f"cache:narrative:insight:{insight_id}"
            data = self.redis.get(key)

            if data:
                narrative = json.loads(data)
                logger.debug(f"Retrieved cached narrative for insight {insight_id}")
                return narrative
            else:
                logger.debug(f"No cached narrative found for insight {insight_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve cached narrative for insight {insight_id}: {e}")
            return None

    def cache_portfolio_metrics(
        self,
        company_id: str,
        metrics: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache portfolio metrics

        Args:
            company_id: Company identifier
            metrics: Portfolio metrics dictionary
            ttl: Time-to-live in seconds (None = use default)

        Returns:
            True if successful
        """
        try:
            key = f"cache:portfolio:company:{company_id}"
            ttl_seconds = ttl or self.default_ttl

            data = json.dumps(metrics, default=str)
            self.redis.setex(key, ttl_seconds, data)

            logger.debug(f"Cached portfolio metrics for company {company_id} (TTL: {ttl_seconds}s)")
            return True

        except Exception as e:
            logger.error(f"Failed to cache portfolio metrics for company {company_id}: {e}")
            return False

    def get_cached_portfolio_metrics(self, company_id: str) -> Optional[Dict]:
        """
        Retrieve cached portfolio metrics

        Args:
            company_id: Company identifier

        Returns:
            Portfolio metrics dictionary or None
        """
        try:
            key = f"cache:portfolio:company:{company_id}"
            data = self.redis.get(key)

            if data:
                metrics = json.loads(data)
                logger.debug(f"Retrieved cached portfolio metrics for company {company_id}")
                return metrics
            else:
                logger.debug(f"No cached portfolio metrics found for company {company_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve cached portfolio metrics for company {company_id}: {e}")
            return None

    def cache_detection_result(
        self,
        company_id: str,
        detection_type: str,
        results: List[Dict],
        ttl: int = 300  # 5 minutes default
    ) -> bool:
        """
        Cache detection results (risk or opportunity)

        Args:
            company_id: Company identifier
            detection_type: 'risk' or 'opportunity'
            results: Detection results
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            key = f"cache:detection:{detection_type}:company:{company_id}"
            data = json.dumps(results, default=str)

            self.redis.setex(key, ttl, data)

            logger.debug(f"Cached {len(results)} {detection_type} detections for company {company_id} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Failed to cache {detection_type} detections for company {company_id}: {e}")
            return False

    def get_cached_detection_result(
        self,
        company_id: str,
        detection_type: str
    ) -> Optional[List[Dict]]:
        """
        Retrieve cached detection results

        Args:
            company_id: Company identifier
            detection_type: 'risk' or 'opportunity'

        Returns:
            Detection results or None
        """
        try:
            key = f"cache:detection:{detection_type}:company:{company_id}"
            data = self.redis.get(key)

            if data:
                results = json.loads(data)
                logger.debug(f"Retrieved {len(results)} cached {detection_type} detections for company {company_id}")
                return results
            else:
                logger.debug(f"No cached {detection_type} detections found for company {company_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve cached {detection_type} detections for company {company_id}: {e}")
            return None

    def invalidate_company_cache(self, company_id: str) -> int:
        """
        Clear all cache entries for a company

        Args:
            company_id: Company identifier

        Returns:
            Number of keys deleted
        """
        try:
            # Find all keys related to this company
            patterns = [
                f"cache:insights:company:{company_id}:*",
                f"cache:portfolio:company:{company_id}",
                f"cache:detection:*:company:{company_id}"
            ]

            deleted_count = 0
            for pattern in patterns:
                keys = self.redis.keys(pattern)
                if keys:
                    deleted_count += self.redis.delete(*keys)

            logger.info(f"Invalidated {deleted_count} cache entries for company {company_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to invalidate cache for company {company_id}: {e}")
            return 0

    def invalidate_insight_cache(self, insight_id: int) -> int:
        """
        Clear cache entries for a specific insight

        Args:
            insight_id: PostgreSQL insight_id

        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"cache:narrative:insight:{insight_id}"
            keys = self.redis.keys(pattern)

            if keys:
                deleted_count = self.redis.delete(*keys)
                logger.info(f"Invalidated {deleted_count} cache entries for insight {insight_id}")
                return deleted_count
            else:
                logger.debug(f"No cache entries found for insight {insight_id}")
                return 0

        except Exception as e:
            logger.error(f"Failed to invalidate cache for insight {insight_id}: {e}")
            return 0

    def set_with_ttl(
        self,
        key: str,
        value: Any,
        ttl: int
    ) -> bool:
        """
        Generic cache setter with TTL

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            data = json.dumps(value, default=str)
            self.redis.setex(key, ttl, data)

            logger.debug(f"Cached key '{key}' (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Failed to cache key '{key}': {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Generic cache getter

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            data = self.redis.get(key)

            if data:
                value = json.loads(data)
                logger.debug(f"Retrieved cached key '{key}'")
                return value
            else:
                logger.debug(f"Key '{key}' not found in cache")
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve key '{key}': {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete a cache key

        Args:
            key: Cache key to delete

        Returns:
            True if successful
        """
        try:
            deleted = self.redis.delete(key)

            if deleted > 0:
                logger.debug(f"Deleted cache key '{key}'")
                return True
            else:
                logger.debug(f"Cache key '{key}' not found")
                return False

        except Exception as e:
            logger.error(f"Failed to delete key '{key}': {e}")
            return False

    def flush_all(self) -> bool:
        """
        Clear all cache (USE WITH CAUTION)

        Returns:
            True if successful
        """
        try:
            self.redis.flushdb()
            logger.warning("Flushed all cache entries")
            return True

        except Exception as e:
            logger.error(f"Failed to flush cache: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        try:
            info = self.redis.info()

            return {
                "connected": self.redis.ping(),
                "used_memory": info.get('used_memory_human', 'N/A'),
                "total_keys": self.redis.dbsize(),
                "uptime_seconds": info.get('uptime_in_seconds', 0),
                "connected_clients": info.get('connected_clients', 0),
                "cache_hit_rate": info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1))
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
