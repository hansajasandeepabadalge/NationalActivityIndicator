"""
Smart Cache Manager

Central manager for intelligent caching of scraped content.
Integrates change detection, content caching, and metrics.

Features:
1. Quick change detection (HEAD request, ETag, Last-Modified)
2. Page signature matching (partial content hash)
3. Full article caching with configurable TTL
4. Automatic cache invalidation
5. Performance metrics tracking

Usage:
    cache = SmartCacheManager()
    
    # Check if source needs scraping
    if await cache.needs_scraping(source_name, url):
        articles = await scraper.fetch_articles()
        await cache.cache_articles(source_name, articles)
    else:
        articles = await cache.get_cached_articles(source_name)
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import httpx

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached entry with metadata"""
    source_name: str
    url: str
    etag: Optional[str]
    last_modified: Optional[str]
    content_signature: str
    articles_count: int
    cached_at: str
    expires_at: str
    

@dataclass
class CacheConfig:
    """Configuration for cache behavior per source type"""
    # TTL settings (in seconds)
    default_ttl: int = 3600  # 1 hour
    news_ttl: int = 900  # 15 minutes for news
    government_ttl: int = 7200  # 2 hours for government
    api_ttl: int = 1800  # 30 minutes for APIs
    social_ttl: int = 300  # 5 minutes for social media
    
    # Signature settings
    signature_sample_size: int = 2000  # First N chars for signature
    
    # Retry settings
    head_request_timeout: int = 10
    
    def get_ttl_for_type(self, source_type: str) -> int:
        """Get appropriate TTL based on source type"""
        ttl_map = {
            "news": self.news_ttl,
            "government": self.government_ttl,
            "api": self.api_ttl,
            "social": self.social_ttl,
            "financial": self.api_ttl
        }
        return ttl_map.get(source_type, self.default_ttl)


class SmartCacheManager:
    """
    Intelligent cache manager that minimizes redundant scraping.
    
    Provides multi-level caching:
    Level 1: HTTP-level (ETag, Last-Modified) - Fastest
    Level 2: Content signature (partial hash) - Quick
    Level 3: Full article cache - Most complete
    """
    
    # Redis key prefixes
    KEY_PREFIX = "cache:source"
    KEY_ETAG = "etag"
    KEY_LAST_MODIFIED = "last_modified"
    KEY_SIGNATURE = "signature"
    KEY_ARTICLES = "articles"
    KEY_METADATA = "metadata"
    KEY_SCRAPED_AT = "scraped_at"
    
    def __init__(self, redis_client=None, config: Optional[CacheConfig] = None):
        """
        Initialize Smart Cache Manager.
        
        Args:
            redis_client: Redis client instance (auto-connected if None)
            config: Cache configuration (uses defaults if None)
        """
        self.redis = redis_client
        self.config = config or CacheConfig()
        self._http_client: Optional[httpx.AsyncClient] = None
        
    async def _get_redis(self):
        """Lazy load Redis client"""
        if self.redis is None:
            from app.db.redis_client import redis_client, get_redis
            # Ensure Redis is connected
            if redis_client.client is None:
                redis_client.connect()
            self.redis = get_redis()
        return self.redis
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=self.config.head_request_timeout,
                follow_redirects=True
            )
        return self._http_client
    
    def _make_key(self, source_name: str, key_type: str) -> str:
        """Generate Redis key"""
        return f"{self.KEY_PREFIX}:{source_name}:{key_type}"
    
    # ==========================================
    # Main Public API
    # ==========================================
    
    async def needs_scraping(
        self, 
        source_name: str, 
        url: str,
        source_type: str = "news",
        force: bool = False
    ) -> Tuple[bool, str]:
        """
        Check if a source needs to be scraped.
        
        Uses multi-level detection:
        1. Check if cache expired (TTL)
        2. HEAD request for ETag/Last-Modified
        3. Content signature comparison
        
        Args:
            source_name: Name of the source
            url: URL to check
            source_type: Type of source (news, government, api, social)
            force: Force scrape regardless of cache
            
        Returns:
            Tuple of (needs_scraping: bool, reason: str)
        """
        if force:
            logger.info(f"[Cache] Force scrape requested for {source_name}")
            await self._track_miss(source_name, "force")
            return True, "force_requested"
        
        redis = await self._get_redis()
        
        # Level 0: Check if TTL expired
        ttl_expired, reason = await self._check_ttl_expired(source_name, source_type)
        if ttl_expired:
            logger.info(f"[Cache] TTL expired for {source_name}: {reason}")
            await self._track_miss(source_name, reason)
            return True, reason
        
        # Level 1: Quick HTTP header check (ETag, Last-Modified)
        changed, reason = await self._check_http_headers(source_name, url)
        if changed:
            logger.info(f"[Cache] HTTP headers indicate change for {source_name}: {reason}")
            await self._track_miss(source_name, reason)
            return True, reason
        
        # Level 2: Content signature check (lightweight GET)
        changed, reason = await self._check_content_signature(source_name, url)
        if changed:
            logger.info(f"[Cache] Content signature changed for {source_name}: {reason}")
            await self._track_miss(source_name, reason)
            return True, reason
        
        # Cache is still valid
        logger.info(f"[Cache] HIT for {source_name} - no scraping needed")
        await self._track_hit(source_name)
        return False, "cache_valid"
    
    # Alias for backwards compatibility
    async def should_scrape(
        self, 
        source_name: str, 
        url: str,
        source_type: str = "news",
        force: bool = False
    ) -> Tuple[bool, str]:
        """Alias for needs_scraping (backwards compatibility)."""
        return await self.needs_scraping(source_name, url, source_type, force)
    
    async def get_cached_articles(self, source_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached articles for a source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            List of cached article dictionaries or None if not cached
        """
        redis = await self._get_redis()
        key = self._make_key(source_name, self.KEY_ARTICLES)
        
        try:
            cached = await redis.get(key)
            if cached:
                articles = json.loads(cached)
                logger.debug(f"[Cache] Retrieved {len(articles)} cached articles for {source_name}")
                return articles
        except Exception as e:
            logger.error(f"[Cache] Error retrieving cached articles: {e}")
        
        return None
    
    async def cache_articles(
        self, 
        source_name: str,
        url: str,
        articles: List[Dict[str, Any]],
        source_type: str = "news",
        response_headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Cache scraped articles with metadata.
        
        Args:
            source_name: Name of the source
            url: URL that was scraped
            articles: List of article dictionaries
            source_type: Type of source for TTL calculation
            response_headers: HTTP response headers (for ETag, Last-Modified)
            
        Returns:
            True if caching succeeded
        """
        redis = await self._get_redis()
        ttl = self.config.get_ttl_for_type(source_type)
        
        try:
            # Store articles
            articles_key = self._make_key(source_name, self.KEY_ARTICLES)
            await redis.setex(articles_key, ttl, json.dumps(articles))
            
            # Store metadata
            metadata = CacheEntry(
                source_name=source_name,
                url=url,
                etag=response_headers.get("ETag") if response_headers else None,
                last_modified=response_headers.get("Last-Modified") if response_headers else None,
                content_signature=self._calculate_signature(json.dumps(articles)),
                articles_count=len(articles),
                cached_at=datetime.utcnow().isoformat(),
                expires_at=(datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
            )
            
            metadata_key = self._make_key(source_name, self.KEY_METADATA)
            await redis.setex(metadata_key, ttl, json.dumps(asdict(metadata)))
            
            # Store individual cache components for quick access
            if response_headers:
                if "ETag" in response_headers:
                    etag_key = self._make_key(source_name, self.KEY_ETAG)
                    await redis.setex(etag_key, ttl, response_headers["ETag"])
                    
                if "Last-Modified" in response_headers:
                    lm_key = self._make_key(source_name, self.KEY_LAST_MODIFIED)
                    await redis.setex(lm_key, ttl, response_headers["Last-Modified"])
            
            # Store content signature
            sig_key = self._make_key(source_name, self.KEY_SIGNATURE)
            signature = self._calculate_signature(json.dumps(articles))
            await redis.setex(sig_key, ttl, signature)
            
            # Store scrape timestamp
            time_key = self._make_key(source_name, self.KEY_SCRAPED_AT)
            await redis.setex(time_key, ttl, datetime.utcnow().isoformat())
            
            logger.info(f"[Cache] Cached {len(articles)} articles for {source_name} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"[Cache] Error caching articles: {e}")
            return False
    
    async def invalidate(self, source_name: str) -> bool:
        """
        Invalidate cache for a source.
        
        Args:
            source_name: Name of the source to invalidate
            
        Returns:
            True if invalidation succeeded
        """
        redis = await self._get_redis()
        
        try:
            keys = [
                self._make_key(source_name, self.KEY_ARTICLES),
                self._make_key(source_name, self.KEY_METADATA),
                self._make_key(source_name, self.KEY_ETAG),
                self._make_key(source_name, self.KEY_LAST_MODIFIED),
                self._make_key(source_name, self.KEY_SIGNATURE),
                self._make_key(source_name, self.KEY_SCRAPED_AT)
            ]
            
            await redis.delete(*keys)
            logger.info(f"[Cache] Invalidated cache for {source_name}")
            return True
            
        except Exception as e:
            logger.error(f"[Cache] Error invalidating cache: {e}")
            return False
    
    # Alias for API consistency
    async def invalidate_source(self, source_name: str) -> bool:
        """Alias for invalidate() for API consistency."""
        return await self.invalidate(source_name)
    
    async def get_cache_status(self, source_name: str) -> Dict[str, Any]:
        """
        Get detailed cache status for a source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            Dict with cache status information
        """
        redis = await self._get_redis()
        
        metadata_key = self._make_key(source_name, self.KEY_METADATA)
        articles_key = self._make_key(source_name, self.KEY_ARTICLES)
        
        try:
            metadata_raw = await redis.get(metadata_key)
            articles_ttl = await redis.ttl(articles_key)
            
            if metadata_raw:
                metadata = json.loads(metadata_raw)
                return {
                    "cached": True,
                    "source_name": source_name,
                    "articles_count": metadata.get("articles_count", 0),
                    "cached_at": metadata.get("cached_at"),
                    "expires_at": metadata.get("expires_at"),
                    "ttl_remaining": articles_ttl,
                    "etag": metadata.get("etag"),
                    "last_modified": metadata.get("last_modified")
                }
            else:
                return {
                    "cached": False,
                    "source_name": source_name,
                    "reason": "no_cache_entry"
                }
                
        except Exception as e:
            return {
                "cached": False,
                "source_name": source_name,
                "error": str(e)
            }
    
    # ==========================================
    # Change Detection Methods
    # ==========================================
    
    async def _check_ttl_expired(
        self, 
        source_name: str, 
        source_type: str
    ) -> Tuple[bool, str]:
        """Check if cache TTL has expired"""
        redis = await self._get_redis()
        
        time_key = self._make_key(source_name, self.KEY_SCRAPED_AT)
        scraped_at_str = await redis.get(time_key)
        
        if not scraped_at_str:
            return True, "no_previous_scrape"
        
        try:
            scraped_at = datetime.fromisoformat(scraped_at_str)
            ttl = self.config.get_ttl_for_type(source_type)
            expires_at = scraped_at + timedelta(seconds=ttl)
            
            if datetime.utcnow() > expires_at:
                return True, "ttl_expired"
            
            return False, "ttl_valid"
            
        except Exception as e:
            logger.warning(f"[Cache] Error parsing scraped_at: {e}")
            return True, "parse_error"
    
    async def _check_http_headers(
        self, 
        source_name: str, 
        url: str
    ) -> Tuple[bool, str]:
        """
        Check if content changed using HTTP headers (HEAD request).
        
        Uses ETag and Last-Modified headers for efficient change detection.
        """
        redis = await self._get_redis()
        
        try:
            client = await self._get_http_client()
            
            # Get cached headers
            etag_key = self._make_key(source_name, self.KEY_ETAG)
            lm_key = self._make_key(source_name, self.KEY_LAST_MODIFIED)
            
            cached_etag = await redis.get(etag_key)
            cached_last_modified = await redis.get(lm_key)
            
            # Make HEAD request with conditional headers
            headers = {}
            if cached_etag:
                headers["If-None-Match"] = cached_etag
            if cached_last_modified:
                headers["If-Modified-Since"] = cached_last_modified
            
            response = await client.head(url, headers=headers)
            
            # 304 Not Modified = no change
            if response.status_code == 304:
                return False, "not_modified_304"
            
            # Compare current headers with cached
            current_etag = response.headers.get("ETag")
            current_lm = response.headers.get("Last-Modified")
            
            # Check ETag
            if cached_etag and current_etag:
                if cached_etag != current_etag:
                    return True, "etag_changed"
            
            # Check Last-Modified
            if cached_last_modified and current_lm:
                if cached_last_modified != current_lm:
                    return True, "last_modified_changed"
            
            # No cached headers to compare - need full check
            if not cached_etag and not cached_last_modified:
                return True, "no_cached_headers"
            
            return False, "headers_unchanged"
            
        except httpx.TimeoutException:
            logger.warning(f"[Cache] HEAD request timeout for {url}")
            return True, "head_timeout"
        except Exception as e:
            logger.warning(f"[Cache] HEAD request error: {e}")
            return True, "head_error"
    
    async def _check_content_signature(
        self, 
        source_name: str, 
        url: str
    ) -> Tuple[bool, str]:
        """
        Quick content signature check using partial content.
        
        Downloads only first N characters and compares hash.
        """
        redis = await self._get_redis()
        
        try:
            client = await self._get_http_client()
            
            # Get cached signature
            sig_key = self._make_key(source_name, self.KEY_SIGNATURE)
            cached_signature = await redis.get(sig_key)
            
            if not cached_signature:
                return True, "no_cached_signature"
            
            # Request only first N bytes using Range header
            headers = {"Range": f"bytes=0-{self.config.signature_sample_size}"}
            
            try:
                response = await client.get(url, headers=headers)
                partial_content = response.text[:self.config.signature_sample_size]
            except:
                # If Range not supported, get full content and slice
                response = await client.get(url)
                partial_content = response.text[:self.config.signature_sample_size]
            
            # Calculate signature
            current_signature = self._calculate_signature(partial_content)
            
            if cached_signature != current_signature:
                return True, "signature_changed"
            
            return False, "signature_unchanged"
            
        except Exception as e:
            logger.warning(f"[Cache] Signature check error: {e}")
            return True, "signature_error"
    
    # ==========================================
    # Helper Methods
    # ==========================================
    
    def _calculate_signature(self, content: str) -> str:
        """Calculate MD5 signature of content"""
        # Normalize content for consistent hashing
        normalized = content.lower().strip()
        # Remove common dynamic elements
        import re
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '', normalized)  # Remove timestamps
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def _track_hit(self, source_name: str):
        """Track cache hit"""
        try:
            redis = await self._get_redis()
            await redis.incr("cache:metrics:hits:total")
            await redis.incr(f"cache:metrics:hits:{source_name}")
        except:
            pass  # Don't fail on metrics
    
    async def _track_miss(self, source_name: str, reason: str):
        """Track cache miss with reason"""
        try:
            redis = await self._get_redis()
            await redis.incr("cache:metrics:misses:total")
            await redis.incr(f"cache:metrics:misses:{source_name}")
            await redis.incr(f"cache:metrics:misses:reason:{reason}")
        except:
            pass  # Don't fail on metrics
    
    async def close(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics synchronously.
        
        Returns:
            Dict with cache statistics
        """
        # Return basic stats from internal tracking
        # For full async stats, use CacheMetrics.get_stats()
        return {
            "hit_rate": 0.0,  # Will be calculated from Redis
            "total_hits": 0,
            "total_misses": 0,
            "bandwidth_saved_kb": 0.0,
            "time_saved_seconds": 0.0,
            "sources": {},
            "status": "operational"
        }
    
    @property
    def metrics(self):
        """Get metrics tracker for recording hits/misses"""
        if not hasattr(self, '_metrics'):
            from app.cache.cache_metrics import CacheMetrics
            self._metrics = CacheMetrics(self.redis)
        return self._metrics


# ==========================================
# Global Cache Instance
# ==========================================

_cache_manager: Optional[SmartCacheManager] = None


def get_cache_manager() -> SmartCacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = SmartCacheManager()
    return _cache_manager


async def check_cache(
    source_name: str, 
    url: str, 
    source_type: str = "news"
) -> Tuple[bool, str]:
    """
    Convenience function to check if scraping is needed.
    
    Args:
        source_name: Name of the source
        url: URL to check
        source_type: Type of source
        
    Returns:
        Tuple of (needs_scraping, reason)
    """
    cache = get_cache_manager()
    return await cache.needs_scraping(source_name, url, source_type)
