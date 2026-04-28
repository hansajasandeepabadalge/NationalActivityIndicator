"""
Layer 3 Redis Cache

Implements the key patterns defined in blueprint §3.4:

  company:current:{company_id}          Hash  – current indicator values (no TTL, updated on write)
  company:alerts:{company_id}           List  – active alerts sorted by severity (no TTL)
  industry:avg:{industry_id}:{code}     String – industry average (TTL 1 hour)
  calculation:cache:{company_id}:{code} Hash  – cached calculation result (TTL 15 min)
  location:status:{location_id}         Hash  – location-specific state (TTL 30 min)
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# TTLs (seconds)
_TTL_INDUSTRY_AVG = 3600        # 1 hour
_TTL_CALC_CACHE = 900           # 15 minutes
_TTL_LOCATION_STATUS = 1800     # 30 minutes


class Layer3RedisCache:
    """
    Layer 3 Redis cache façade.

    Uses the shared `app.db.redis_client.get_redis()` async client.
    All methods are async (redis.asyncio).
    Falls back gracefully if Redis is unavailable — caller gets None/[].
    """

    def __init__(self, redis_client=None):
        """
        Args:
            redis_client: An async redis client instance. If None, will
                          lazily import from app.db.redis_client.
        """
        self._client = redis_client

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from app.db.redis_client import get_redis
            return get_redis()
        except Exception as e:
            logger.warning(f"Redis client unavailable: {e}")
            return None

    # ── Key helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _key_current(company_id: str) -> str:
        return f"company:current:{company_id}"

    @staticmethod
    def _key_alerts(company_id: str) -> str:
        return f"company:alerts:{company_id}"

    @staticmethod
    def _key_industry_avg(industry_id: str, indicator_code: str) -> str:
        return f"industry:avg:{industry_id}:{indicator_code}"

    @staticmethod
    def _key_calc_cache(company_id: str, indicator_code: str) -> str:
        return f"calculation:cache:{company_id}:{indicator_code}"

    @staticmethod
    def _key_location_status(location_id: str) -> str:
        return f"location:status:{location_id}"

    # ── company:current:{company_id} ─────────────────────────────────────────

    async def set_current_indicators(
        self,
        company_id: str,
        indicators: Dict[str, float],
        last_updated: str,
    ) -> bool:
        """
        Write current operational indicator values for a company.
        Hash fields: indicator_code → str(value), plus 'last_updated'.
        No TTL — values stay until next calculation overwrites them.
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            key = self._key_current(company_id)
            mapping: Dict[str, str] = {k: str(v) for k, v in indicators.items()}
            mapping['last_updated'] = last_updated
            await client.hset(key, mapping=mapping)
            return True
        except Exception as e:
            logger.warning(f"Redis set_current_indicators failed: {e}")
            return False

    async def get_current_indicators(self, company_id: str) -> Optional[Dict[str, str]]:
        """Return all current indicator fields for a company, or None if missing."""
        client = self._get_client()
        if client is None:
            return None
        try:
            data = await client.hgetall(self._key_current(company_id))
            return data if data else None
        except Exception as e:
            logger.warning(f"Redis get_current_indicators failed: {e}")
            return None

    # ── company:alerts:{company_id} ──────────────────────────────────────────

    async def push_alert(self, company_id: str, alert: Dict[str, Any]) -> bool:
        """
        Prepend an alert to the company alerts list (most-recent first).
        Trims list to 100 entries.
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            key = self._key_alerts(company_id)
            await client.lpush(key, json.dumps(alert))
            await client.ltrim(key, 0, 99)
            return True
        except Exception as e:
            logger.warning(f"Redis push_alert failed: {e}")
            return False

    async def get_alerts(self, company_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Return active alerts for a company (most-recent first)."""
        client = self._get_client()
        if client is None:
            return []
        try:
            raw = await client.lrange(self._key_alerts(company_id), 0, limit - 1)
            return [json.loads(r) for r in raw]
        except Exception as e:
            logger.warning(f"Redis get_alerts failed: {e}")
            return []

    async def clear_alerts(self, company_id: str) -> bool:
        """Clear all alerts for a company."""
        client = self._get_client()
        if client is None:
            return False
        try:
            await client.delete(self._key_alerts(company_id))
            return True
        except Exception as e:
            logger.warning(f"Redis clear_alerts failed: {e}")
            return False

    # ── industry:avg:{industry_id}:{indicator_code} ──────────────────────────

    async def set_industry_average(
        self,
        industry_id: str,
        indicator_code: str,
        value: float,
    ) -> bool:
        """Cache industry average with 1-hour TTL."""
        client = self._get_client()
        if client is None:
            return False
        try:
            key = self._key_industry_avg(industry_id, indicator_code)
            await client.set(key, str(value), ex=_TTL_INDUSTRY_AVG)
            return True
        except Exception as e:
            logger.warning(f"Redis set_industry_average failed: {e}")
            return False

    async def get_industry_average(
        self, industry_id: str, indicator_code: str
    ) -> Optional[float]:
        """Return cached industry average or None on miss."""
        client = self._get_client()
        if client is None:
            return None
        try:
            val = await client.get(self._key_industry_avg(industry_id, indicator_code))
            return float(val) if val is not None else None
        except Exception as e:
            logger.warning(f"Redis get_industry_average failed: {e}")
            return None

    # ── calculation:cache:{company_id}:{indicator_code} ──────────────────────

    async def set_calculation_cache(
        self,
        company_id: str,
        indicator_code: str,
        result: Dict[str, Any],
    ) -> bool:
        """Cache a calculation result hash with 15-minute TTL."""
        client = self._get_client()
        if client is None:
            return False
        try:
            key = self._key_calc_cache(company_id, indicator_code)
            await client.set(key, json.dumps(result), ex=_TTL_CALC_CACHE)
            return True
        except Exception as e:
            logger.warning(f"Redis set_calculation_cache failed: {e}")
            return False

    async def get_calculation_cache(
        self, company_id: str, indicator_code: str
    ) -> Optional[Dict[str, Any]]:
        """Return cached calculation or None on miss/expiry."""
        client = self._get_client()
        if client is None:
            return None
        try:
            raw = await client.get(self._key_calc_cache(company_id, indicator_code))
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.warning(f"Redis get_calculation_cache failed: {e}")
            return None

    async def invalidate_calculation_cache(
        self, company_id: str, indicator_code: str
    ) -> bool:
        """Explicitly evict a cached calculation (e.g. after new data arrives)."""
        client = self._get_client()
        if client is None:
            return False
        try:
            await client.delete(self._key_calc_cache(company_id, indicator_code))
            return True
        except Exception as e:
            logger.warning(f"Redis invalidate_calculation_cache failed: {e}")
            return False

    # ── location:status:{location_id} ────────────────────────────────────────

    async def set_location_status(
        self,
        location_id: str,
        status: Dict[str, Any],
    ) -> bool:
        """Cache location-specific operational status with 30-minute TTL."""
        client = self._get_client()
        if client is None:
            return False
        try:
            key = self._key_location_status(location_id)
            mapping: Dict[str, str] = {k: json.dumps(v) for k, v in status.items()}
            await client.hset(key, mapping=mapping)
            await client.expire(key, _TTL_LOCATION_STATUS)
            return True
        except Exception as e:
            logger.warning(f"Redis set_location_status failed: {e}")
            return False

    async def get_location_status(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Return cached location status or None on miss."""
        client = self._get_client()
        if client is None:
            return None
        try:
            raw = await client.hgetall(self._key_location_status(location_id))
            if not raw:
                return None
            return {k: json.loads(v) for k, v in raw.items()}
        except Exception as e:
            logger.warning(f"Redis get_location_status failed: {e}")
            return None

    # ── Bulk helpers ──────────────────────────────────────────────────────────

    async def invalidate_company(self, company_id: str) -> None:
        """Delete all current-state keys for a company (call after full recalculation)."""
        client = self._get_client()
        if client is None:
            return
        try:
            await client.delete(self._key_current(company_id))
            # Leave alerts — they're a historical list
        except Exception as e:
            logger.warning(f"Redis invalidate_company failed: {e}")
