"""
Change Detector Module

Specialized change detection strategies for different source types.
Provides multiple detection methods with fallback chains.
"""

import hashlib
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class ChangeCheckResult:
    """Result of a change detection check"""
    changed: bool
    reason: str
    confidence: float  # 0.0 to 1.0
    method_used: str
    check_duration_ms: int
    metadata: Dict[str, Any]


class BaseChangeDetector(ABC):
    """Abstract base class for change detectors"""
    
    @abstractmethod
    async def detect_change(
        self, 
        url: str, 
        cached_data: Dict[str, Any]
    ) -> ChangeCheckResult:
        """
        Detect if content has changed.
        
        Args:
            url: URL to check
            cached_data: Previously cached metadata
            
        Returns:
            ChangeCheckResult with detection outcome
        """
        pass


class HTTPHeaderDetector(BaseChangeDetector):
    """
    Detect changes using HTTP headers (ETag, Last-Modified).
    
    This is the fastest method - only requires a HEAD request.
    Works best with properly configured web servers.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True
            )
        return self._client
    
    async def detect_change(
        self, 
        url: str, 
        cached_data: Dict[str, Any]
    ) -> ChangeCheckResult:
        """Detect change using HTTP headers"""
        start = datetime.utcnow()
        
        try:
            client = await self._get_client()
            
            # Build conditional request headers
            headers = {}
            if cached_data.get("etag"):
                headers["If-None-Match"] = cached_data["etag"]
            if cached_data.get("last_modified"):
                headers["If-Modified-Since"] = cached_data["last_modified"]
            
            response = await client.head(url, headers=headers)
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            # 304 Not Modified - definitive no change
            if response.status_code == 304:
                return ChangeCheckResult(
                    changed=False,
                    reason="304_not_modified",
                    confidence=1.0,
                    method_used="http_headers",
                    check_duration_ms=duration,
                    metadata={"status_code": 304}
                )
            
            # Compare headers if available
            new_etag = response.headers.get("ETag")
            new_lm = response.headers.get("Last-Modified")
            
            # ETag comparison (most reliable)
            if cached_data.get("etag") and new_etag:
                if cached_data["etag"] == new_etag:
                    return ChangeCheckResult(
                        changed=False,
                        reason="etag_match",
                        confidence=0.95,
                        method_used="http_headers",
                        check_duration_ms=duration,
                        metadata={"etag": new_etag}
                    )
                else:
                    return ChangeCheckResult(
                        changed=True,
                        reason="etag_mismatch",
                        confidence=0.95,
                        method_used="http_headers",
                        check_duration_ms=duration,
                        metadata={"old_etag": cached_data["etag"], "new_etag": new_etag}
                    )
            
            # Last-Modified comparison
            if cached_data.get("last_modified") and new_lm:
                if cached_data["last_modified"] == new_lm:
                    return ChangeCheckResult(
                        changed=False,
                        reason="last_modified_match",
                        confidence=0.85,
                        method_used="http_headers",
                        check_duration_ms=duration,
                        metadata={"last_modified": new_lm}
                    )
                else:
                    return ChangeCheckResult(
                        changed=True,
                        reason="last_modified_mismatch",
                        confidence=0.85,
                        method_used="http_headers",
                        check_duration_ms=duration,
                        metadata={"old_lm": cached_data["last_modified"], "new_lm": new_lm}
                    )
            
            # No comparable headers - inconclusive
            return ChangeCheckResult(
                changed=True,
                reason="no_comparable_headers",
                confidence=0.3,
                method_used="http_headers",
                check_duration_ms=duration,
                metadata={"new_etag": new_etag, "new_lm": new_lm}
            )
            
        except httpx.TimeoutException:
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            return ChangeCheckResult(
                changed=True,
                reason="timeout",
                confidence=0.5,
                method_used="http_headers",
                check_duration_ms=duration,
                metadata={"error": "timeout"}
            )
        except Exception as e:
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            return ChangeCheckResult(
                changed=True,
                reason="error",
                confidence=0.5,
                method_used="http_headers",
                check_duration_ms=duration,
                metadata={"error": str(e)}
            )
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class ContentSignatureDetector(BaseChangeDetector):
    """
    Detect changes by comparing content signatures.
    
    Uses partial content download and hashing for quick comparison.
    More reliable than headers but requires more bandwidth.
    """
    
    def __init__(self, sample_size: int = 3000, timeout: int = 15):
        self.sample_size = sample_size
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True
            )
        return self._client
    
    def _normalize_content(self, content: str) -> str:
        """
        Normalize content for consistent signature generation.
        
        Removes:
        - Dynamic timestamps
        - Session IDs
        - Ad content markers
        - Extra whitespace
        """
        normalized = content
        
        # Remove common dynamic elements
        # Timestamps: 2025-12-07T10:30:00
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}(:\d{2})?', '', normalized)
        
        # Session/CSRF tokens
        normalized = re.sub(r'token["\']?\s*[:=]\s*["\'][a-zA-Z0-9_-]+["\']', '', normalized)
        
        # Random IDs
        normalized = re.sub(r'[a-f0-9]{32,}', '', normalized)
        
        # Whitespace normalization
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip().lower()
    
    def _calculate_signature(self, content: str) -> str:
        """Calculate MD5 signature of normalized content"""
        normalized = self._normalize_content(content)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def detect_change(
        self, 
        url: str, 
        cached_data: Dict[str, Any]
    ) -> ChangeCheckResult:
        """Detect change using content signature"""
        start = datetime.utcnow()
        
        cached_signature = cached_data.get("signature")
        if not cached_signature:
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            return ChangeCheckResult(
                changed=True,
                reason="no_cached_signature",
                confidence=0.5,
                method_used="content_signature",
                check_duration_ms=duration,
                metadata={}
            )
        
        try:
            client = await self._get_client()
            
            # Try Range request first (faster)
            try:
                headers = {"Range": f"bytes=0-{self.sample_size}"}
                response = await client.get(url, headers=headers)
                content = response.text[:self.sample_size]
            except:
                # Fallback to full GET and truncate
                response = await client.get(url)
                content = response.text[:self.sample_size]
            
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            # Calculate new signature
            new_signature = self._calculate_signature(content)
            
            if cached_signature == new_signature:
                return ChangeCheckResult(
                    changed=False,
                    reason="signature_match",
                    confidence=0.90,
                    method_used="content_signature",
                    check_duration_ms=duration,
                    metadata={"signature": new_signature}
                )
            else:
                return ChangeCheckResult(
                    changed=True,
                    reason="signature_mismatch",
                    confidence=0.90,
                    method_used="content_signature",
                    check_duration_ms=duration,
                    metadata={
                        "old_signature": cached_signature,
                        "new_signature": new_signature
                    }
                )
                
        except Exception as e:
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            return ChangeCheckResult(
                changed=True,
                reason="error",
                confidence=0.5,
                method_used="content_signature",
                check_duration_ms=duration,
                metadata={"error": str(e)}
            )
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class RSSFeedDetector(BaseChangeDetector):
    """
    Specialized detector for RSS/Atom feeds.
    
    Checks feed metadata and latest entry for changes.
    Very efficient for feed-based sources.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True
            )
        return self._client
    
    async def detect_change(
        self, 
        url: str, 
        cached_data: Dict[str, Any]
    ) -> ChangeCheckResult:
        """Detect change in RSS feed"""
        start = datetime.utcnow()
        
        try:
            client = await self._get_client()
            response = await client.get(url)
            content = response.text
            
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            # Quick checks on RSS content
            # Check lastBuildDate or pubDate
            last_build_match = re.search(r'<lastBuildDate>([^<]+)</lastBuildDate>', content)
            pub_date_match = re.search(r'<pubDate>([^<]+)</pubDate>', content)
            
            current_date = None
            if last_build_match:
                current_date = last_build_match.group(1)
            elif pub_date_match:
                current_date = pub_date_match.group(1)
            
            cached_date = cached_data.get("feed_date")
            
            if cached_date and current_date:
                if cached_date == current_date:
                    return ChangeCheckResult(
                        changed=False,
                        reason="feed_date_match",
                        confidence=0.95,
                        method_used="rss_feed",
                        check_duration_ms=duration,
                        metadata={"feed_date": current_date}
                    )
            
            # Check first item GUID or link
            first_guid_match = re.search(r'<guid[^>]*>([^<]+)</guid>', content)
            first_link_match = re.search(r'<item>.*?<link>([^<]+)</link>', content, re.DOTALL)
            
            current_first_item = None
            if first_guid_match:
                current_first_item = first_guid_match.group(1)
            elif first_link_match:
                current_first_item = first_link_match.group(1)
            
            cached_first_item = cached_data.get("first_item_id")
            
            if cached_first_item and current_first_item:
                if cached_first_item == current_first_item:
                    return ChangeCheckResult(
                        changed=False,
                        reason="first_item_match",
                        confidence=0.85,
                        method_used="rss_feed",
                        check_duration_ms=duration,
                        metadata={"first_item": current_first_item}
                    )
            
            # Count items as sanity check
            item_count = content.count('<item>')
            cached_count = cached_data.get("item_count", 0)
            
            if item_count != cached_count:
                return ChangeCheckResult(
                    changed=True,
                    reason="item_count_changed",
                    confidence=0.80,
                    method_used="rss_feed",
                    check_duration_ms=duration,
                    metadata={
                        "old_count": cached_count,
                        "new_count": item_count,
                        "feed_date": current_date,
                        "first_item": current_first_item
                    }
                )
            
            # If we have current data but nothing to compare, assume changed
            if current_date or current_first_item:
                return ChangeCheckResult(
                    changed=True,
                    reason="no_cached_comparison",
                    confidence=0.6,
                    method_used="rss_feed",
                    check_duration_ms=duration,
                    metadata={
                        "feed_date": current_date,
                        "first_item": current_first_item,
                        "item_count": item_count
                    }
                )
            
            return ChangeCheckResult(
                changed=True,
                reason="parse_failed",
                confidence=0.5,
                method_used="rss_feed",
                check_duration_ms=duration,
                metadata={}
            )
            
        except Exception as e:
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            return ChangeCheckResult(
                changed=True,
                reason="error",
                confidence=0.5,
                method_used="rss_feed",
                check_duration_ms=duration,
                metadata={"error": str(e)}
            )
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class ChangeDetector:
    """
    Unified change detector with fallback chain.
    
    Tries multiple detection methods in order of efficiency:
    1. HTTP Headers (fastest, lowest bandwidth)
    2. Content Signature (quick, medium bandwidth)
    3. RSS Feed (for feed sources)
    """
    
    def __init__(self):
        self.http_detector = HTTPHeaderDetector()
        self.signature_detector = ContentSignatureDetector()
        self.rss_detector = RSSFeedDetector()
    
    async def detect_change(
        self,
        url: str,
        cached_data: Dict[str, Any],
        source_type: str = "news",
        confidence_threshold: float = 0.7
    ) -> ChangeCheckResult:
        """
        Detect if content changed using optimal method chain.
        
        Args:
            url: URL to check
            cached_data: Previously cached metadata
            source_type: Type of source (news, rss, api, etc.)
            confidence_threshold: Minimum confidence to accept result
            
        Returns:
            ChangeCheckResult with final detection outcome
        """
        # For RSS feeds, use specialized detector
        if source_type == "rss" or url.endswith((".xml", ".rss", "/feed", "/rss")):
            result = await self.rss_detector.detect_change(url, cached_data)
            if result.confidence >= confidence_threshold:
                return result
        
        # Try HTTP headers first (fastest)
        result = await self.http_detector.detect_change(url, cached_data)
        if result.confidence >= confidence_threshold:
            return result
        
        # Fallback to content signature if headers inconclusive
        if result.confidence < confidence_threshold:
            sig_result = await self.signature_detector.detect_change(url, cached_data)
            if sig_result.confidence > result.confidence:
                return sig_result
        
        return result
    
    async def close(self):
        """Close all detector clients"""
        await self.http_detector.close()
        await self.signature_detector.close()
        await self.rss_detector.close()


# Global instance
_change_detector: Optional[ChangeDetector] = None


def get_change_detector() -> ChangeDetector:
    """Get global change detector instance"""
    global _change_detector
    if _change_detector is None:
        _change_detector = ChangeDetector()
    return _change_detector
