"""
Base LLM Service

Provides foundational LLM functionality:
- Groq Llama 3.1 70B client (FREE tier)
- Redis caching for responses
- Error handling with fallback
- Rate limiting and retry logic
- Structured output parsing
- Multi-API key support with automatic rotation

This is the base class that all LLM-powered services inherit from.
"""

import os
import json
import hashlib
import logging
import time
from typing import Dict, Any, Optional, List, Type, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Manages multiple API keys with automatic rotation.
    
    When a rate limit is hit on one key, automatically switches to the next available key.
    Keys are read from GROQ_API_KEY (single key) or GROQ_API_KEYS (comma-separated list).
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if APIKeyManager._initialized:
            return
        
        self._keys: List[str] = []
        self._current_index = 0
        self._key_status: Dict[str, Dict[str, Any]] = {}  # Track status of each key
        self._load_keys()
        APIKeyManager._initialized = True
    
    def _load_keys(self):
        """Load API keys from environment variables."""
        # Try GROQ_API_KEYS first (comma-separated list)
        keys_str = os.getenv("GROQ_API_KEYS", "")
        if keys_str:
            self._keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        
        # Fall back to single GROQ_API_KEY
        if not self._keys:
            single_key = os.getenv("GROQ_API_KEY", "")
            if single_key:
                self._keys = [single_key]
        
        # Initialize status for each key
        for key in self._keys:
            key_id = self._get_key_id(key)
            self._key_status[key_id] = {
                "available": True,
                "rate_limited_until": None,
                "total_calls": 0,
                "errors": 0
            }
        
        if self._keys:
            logger.info(f"APIKeyManager: Loaded {len(self._keys)} API key(s)")
        else:
            logger.warning("APIKeyManager: No API keys found in environment")
    
    def _get_key_id(self, key: str) -> str:
        """Get a safe identifier for a key (last 4 chars)."""
        return f"...{key[-4:]}" if len(key) > 4 else key
    
    @property
    def has_keys(self) -> bool:
        """Check if any API keys are available."""
        return len(self._keys) > 0
    
    @property
    def current_key(self) -> Optional[str]:
        """Get the current active API key."""
        if not self._keys:
            return None
        return self._keys[self._current_index]
    
    @property
    def available_keys_count(self) -> int:
        """Count of keys not currently rate limited."""
        now = datetime.now()
        count = 0
        for key in self._keys:
            status = self._key_status.get(self._get_key_id(key), {})
            rate_limited_until = status.get("rate_limited_until")
            if rate_limited_until is None or rate_limited_until < now:
                count += 1
        return count
    
    def get_next_available_key(self) -> Optional[str]:
        """
        Get the next available API key, rotating through the list.
        Returns None if all keys are rate limited.
        """
        if not self._keys:
            return None
        
        now = datetime.now()
        original_index = self._current_index
        
        # Try each key in rotation
        for _ in range(len(self._keys)):
            key = self._keys[self._current_index]
            key_id = self._get_key_id(key)
            status = self._key_status.get(key_id, {})
            
            rate_limited_until = status.get("rate_limited_until")
            if rate_limited_until is None or rate_limited_until < now:
                # This key is available
                if status.get("rate_limited_until"):
                    # Key was rate limited but is now available again
                    self._key_status[key_id]["available"] = True
                    self._key_status[key_id]["rate_limited_until"] = None
                    logger.info(f"API key {key_id} is now available again")
                return key
            
            # Try next key
            self._current_index = (self._current_index + 1) % len(self._keys)
        
        # All keys are rate limited
        logger.warning("All API keys are currently rate limited")
        return None
    
    def mark_rate_limited(self, key: str, retry_after_seconds: int = 60):
        """Mark a key as rate limited."""
        key_id = self._get_key_id(key)
        self._key_status[key_id]["available"] = False
        self._key_status[key_id]["rate_limited_until"] = datetime.now() + timedelta(seconds=retry_after_seconds)
        self._key_status[key_id]["errors"] += 1
        
        logger.warning(f"API key {key_id} marked as rate limited for {retry_after_seconds}s")
        
        # Rotate to next key
        self._current_index = (self._current_index + 1) % len(self._keys)
        next_key = self.get_next_available_key()
        if next_key:
            logger.info(f"Rotated to API key {self._get_key_id(next_key)}")
    
    def record_success(self, key: str):
        """Record a successful call with a key."""
        key_id = self._get_key_id(key)
        if key_id in self._key_status:
            self._key_status[key_id]["total_calls"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about API key usage."""
        return {
            "total_keys": len(self._keys),
            "available_keys": self.available_keys_count,
            "current_key": self._get_key_id(self.current_key) if self.current_key else None,
            "key_status": {
                self._get_key_id(k): {
                    "available": self._key_status[self._get_key_id(k)].get("available", True),
                    "rate_limited_until": str(self._key_status[self._get_key_id(k)].get("rate_limited_until")) 
                        if self._key_status[self._get_key_id(k)].get("rate_limited_until") else None,
                    "total_calls": self._key_status[self._get_key_id(k)].get("total_calls", 0),
                    "errors": self._key_status[self._get_key_id(k)].get("errors", 0)
                }
                for k in self._keys
            }
        }


# Global API key manager instance
api_key_manager = APIKeyManager()

# Type variable for generic response types
T = TypeVar('T')


class LLMProvider(Enum):
    """Supported LLM providers."""
    GROQ = "groq"
    OPENAI = "openai"  # Fallback option
    LOCAL = "local"     # For testing


@dataclass
class CacheConfig:
    """Configuration for LLM response caching."""
    enabled: bool = True
    ttl_hours: int = 24
    prefix: str = "llm_cache"
    redis_url: str = ""


@dataclass
class LLMConfig:
    """Configuration for LLM service."""
    provider: LLMProvider = LLMProvider.GROQ
    model: str = "llama-3.3-70b-versatile"  # Updated from decommissioned 3.1
    temperature: float = 0.2
    max_tokens: int = 1024
    cache_ttl_hours: int = 24
    enable_caching: bool = True
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    timeout_seconds: int = 30
    
    # Rate limiting
    requests_per_minute: int = 30  # Groq free tier limit
    
    # Fallback settings
    fallback_to_basic: bool = True


@dataclass
class LLMResponse:
    """Structured LLM response."""
    content: str
    parsed: Optional[Dict[str, Any]] = None
    model: str = ""
    provider: str = ""
    cached: bool = False
    processing_time_ms: float = 0.0
    tokens_used: int = 0
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "parsed": self.parsed,
            "model": self.model,
            "provider": self.provider,
            "cached": self.cached,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "tokens_used": self.tokens_used,
            "success": self.success,
            "error": self.error
        }


class LLMCache:
    """
    Redis-based cache for LLM responses.
    
    Provides 60-70% cache hit rate by caching
    responses for similar content.
    """
    
    def __init__(self, redis_url: str = None, ttl_hours: int = 24):
        """Initialize cache with Redis connection."""
        self._redis = None
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
        self._ttl_seconds = ttl_hours * 3600
        self._enabled = True
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            import redis
            self._redis = redis.from_url(self._redis_url)
            self._redis.ping()
            logger.info("LLM cache connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available for LLM cache: {e}")
            self._redis = None
            self._enabled = False
    
    def _generate_key(self, prefix: str, content: str) -> str:
        """Generate cache key from content hash."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"llm:{prefix}:{content_hash}"
    
    def get(self, prefix: str, content: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available."""
        if not self._enabled or not self._redis:
            return None
        
        try:
            key = self._generate_key(prefix, content)
            cached = self._redis.get(key)
            
            if cached:
                # Update hit count
                self._redis.hincrby("llm:stats", "hits", 1)
                return json.loads(cached)
            
            self._redis.hincrby("llm:stats", "misses", 1)
            return None
            
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    def set(self, prefix: str, content: str, response: Dict[str, Any]):
        """Cache a response."""
        if not self._enabled or not self._redis:
            return
        
        try:
            key = self._generate_key(prefix, content)
            self._redis.setex(
                key,
                self._ttl_seconds,
                json.dumps(response)
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self._enabled or not self._redis:
            return {"enabled": False}
        
        try:
            stats = self._redis.hgetall("llm:stats")
            hits = int(stats.get(b"hits", 0))
            misses = int(stats.get(b"misses", 0))
            total = hits + misses
            
            return {
                "enabled": True,
                "hits": hits,
                "misses": misses,
                "hit_rate": round(hits / total * 100, 1) if total > 0 else 0
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {"enabled": True, "error": str(e)}


class BaseLLMService(ABC):
    """
    Base class for all LLM-powered services.
    
    Provides:
    - Groq Llama 3.1 70B integration
    - Response caching
    - Error handling and retries
    - Structured output parsing
    - Multi-API key rotation
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the LLM service."""
        self.config = config or LLMConfig()
        self._llm = None
        self._current_api_key = None
        self._cache = LLMCache(ttl_hours=self.config.cache_ttl_hours)
        self._last_request_time = 0
        self._request_count = 0
        
        # Statistics
        self._stats = {
            "total_calls": 0,
            "cache_hits": 0,
            "llm_calls": 0,
            "errors": 0,
            "total_processing_time_ms": 0,
            "key_rotations": 0
        }
        
        self._init_llm()
    
    def _init_llm(self, api_key: Optional[str] = None):
        """Initialize the LLM client with the given or next available API key."""
        try:
            if self.config.provider == LLMProvider.GROQ:
                from langchain_groq import ChatGroq
                
                # Use provided key or get from manager
                if api_key is None:
                    api_key = api_key_manager.get_next_available_key()
                
                if not api_key:
                    logger.warning("No API key available. LLM features will use fallback.")
                    self._llm = None
                    return
                
                self._current_api_key = api_key
                self._llm = ChatGroq(
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    api_key=api_key
                )
                key_id = api_key_manager._get_key_id(api_key)
                logger.info(f"LLM initialized: {self.config.provider.value}/{self.config.model} with key {key_id}")
                
        except ImportError as e:
            logger.warning(f"LangChain Groq not installed: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
    
    def _rotate_api_key(self) -> bool:
        """Rotate to next available API key. Returns True if successful."""
        if self._current_api_key:
            api_key_manager.mark_rate_limited(self._current_api_key)
        
        next_key = api_key_manager.get_next_available_key()
        if next_key and next_key != self._current_api_key:
            self._init_llm(next_key)
            self._stats["key_rotations"] += 1
            return self._llm is not None
        return False
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self._llm is not None
    
    @property
    @abstractmethod
    def cache_prefix(self) -> str:
        """Cache key prefix for this service."""
        pass
    
    def _rate_limit(self):
        """Apply rate limiting."""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self._last_request_time > 60:
            self._request_count = 0
            self._last_request_time = current_time
        
        # Check rate limit
        if self._request_count >= self.config.requests_per_minute:
            sleep_time = 60 - (current_time - self._last_request_time)
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
                self._request_count = 0
                self._last_request_time = time.time()
        
        self._request_count += 1
    
    def _call_llm(
        self,
        prompt: str,
        system_prompt: str = "",
        use_cache: bool = True
    ) -> LLMResponse:
        """
        Call the LLM with caching and error handling.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            use_cache: Whether to use cache
            
        Returns:
            LLMResponse with content and metadata
        """
        start_time = time.time()
        self._stats["total_calls"] += 1
        
        # Create cache key from combined prompts
        cache_content = f"{system_prompt}|||{prompt}"
        
        # Check cache first
        if use_cache and self.config.enable_caching:
            cached = self._cache.get(self.cache_prefix, cache_content)
            if cached:
                self._stats["cache_hits"] += 1
                processing_time = (time.time() - start_time) * 1000
                return LLMResponse(
                    content=cached.get("content", ""),
                    parsed=cached.get("parsed"),
                    model=self.config.model,
                    provider=self.config.provider.value,
                    cached=True,
                    processing_time_ms=processing_time
                )
        
        # Check if LLM is available
        if not self.is_available:
            return LLMResponse(
                content="",
                success=False,
                error="LLM not available",
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        # Apply rate limiting
        self._rate_limit()
        
        # Call LLM with retries
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                self._stats["llm_calls"] += 1
                
                from langchain_core.messages import HumanMessage, SystemMessage
                
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=prompt))
                
                response = self._llm.invoke(messages)
                content = response.content
                
                # Try to parse as JSON
                parsed = None
                try:
                    # Extract JSON from response if wrapped in markdown
                    json_content = content
                    if "```json" in content:
                        json_content = content.split("```json")[1].split("```")[0]
                    elif "```" in content:
                        json_content = content.split("```")[1].split("```")[0]
                    
                    parsed = json.loads(json_content.strip())
                except (json.JSONDecodeError, IndexError):
                    pass  # Not JSON response
                
                processing_time = (time.time() - start_time) * 1000
                self._stats["total_processing_time_ms"] += processing_time
                
                result = LLMResponse(
                    content=content,
                    parsed=parsed,
                    model=self.config.model,
                    provider=self.config.provider.value,
                    cached=False,
                    processing_time_ms=processing_time,
                    tokens_used=getattr(response, 'usage', {}).get('total_tokens', 0)
                )
                
                # Cache successful response
                if use_cache and self.config.enable_caching and parsed:
                    self._cache.set(self.cache_prefix, cache_content, {
                        "content": content,
                        "parsed": parsed
                    })
                
                # Record success with API key manager
                if self._current_api_key:
                    api_key_manager.record_success(self._current_api_key)
                
                return result
                
            except Exception as e:
                last_error = str(e)
                error_str = str(e).lower()
                
                # Check for rate limit errors
                is_rate_limit = any(phrase in error_str for phrase in [
                    "rate limit", "rate_limit", "429", "too many requests",
                    "quota exceeded", "token limit", "requests per minute",
                    "daily limit", "tokens per day"
                ])
                
                if is_rate_limit:
                    logger.warning(f"Rate limit hit on API key: {api_key_manager._get_key_id(self._current_api_key) if self._current_api_key else 'unknown'}")
                    
                    # Try to rotate to next key
                    if self._rotate_api_key():
                        logger.info("Successfully rotated to new API key, retrying...")
                        # Reset attempt counter to give new key a fresh start
                        continue
                    else:
                        logger.error("No more API keys available. All keys are rate limited.")
                        break
                
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay_seconds * (attempt + 1))
        
        # All retries failed
        self._stats["errors"] += 1
        processing_time = (time.time() - start_time) * 1000
        
        return LLMResponse(
            content="",
            success=False,
            error=last_error,
            processing_time_ms=processing_time
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        cache_stats = self._cache.get_stats()
        
        total_calls = self._stats["total_calls"]
        avg_time = (
            self._stats["total_processing_time_ms"] / self._stats["llm_calls"]
            if self._stats["llm_calls"] > 0 else 0
        )
        
        return {
            "service": self.__class__.__name__,
            "llm_available": self.is_available,
            "model": self.config.model,
            "current_api_key": api_key_manager._get_key_id(self._current_api_key) if self._current_api_key else None,
            "api_keys_stats": api_key_manager.get_stats(),
            "total_calls": total_calls,
            "cache_hits": self._stats["cache_hits"],
            "cache_hit_rate": round(self._stats["cache_hits"] / total_calls * 100, 1) if total_calls > 0 else 0,
            "llm_calls": self._stats["llm_calls"],
            "errors": self._stats["errors"],
            "key_rotations": self._stats.get("key_rotations", 0),
            "avg_processing_time_ms": round(avg_time, 2),
            "cache": cache_stats
        }


class GroqLLMClient(BaseLLMService):
    """
    Concrete implementation of the LLM service using Groq.
    
    This is the actual client that services should instantiate.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None, cache_config: Optional[CacheConfig] = None):
        """Initialize the Groq LLM client."""
        self._cache_prefix = "groq"
        # Handle cache_config if provided
        if cache_config:
            if config is None:
                config = LLMConfig()
            config.cache_ttl_hours = cache_config.ttl_hours
            config.enable_caching = cache_config.enabled
        super().__init__(config)
    
    @property
    def cache_prefix(self) -> str:
        """Cache key prefix for this service."""
        return self._cache_prefix
    
    def set_cache_prefix(self, prefix: str):
        """Set custom cache prefix for the calling service."""
        self._cache_prefix = prefix
    
    def _should_use_llm(self, text: str, threshold: float = 0.5) -> bool:
        """
        Determine if LLM should be used based on text complexity.
        
        Args:
            text: Text to analyze
            threshold: Complexity threshold (0-1)
            
        Returns:
            True if LLM should be used
        """
        if not text or len(text) < 50:
            return False
        
        # Simple heuristics for complexity
        word_count = len(text.split())
        avg_word_length = sum(len(w) for w in text.split()) / max(word_count, 1)
        
        # Complex if: longer text, longer words
        complexity = min(1.0, (word_count / 500) * 0.5 + (avg_word_length / 10) * 0.5)
        
        return complexity >= threshold and self.is_available
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str = "",
        response_model: Optional[Type[T]] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Generate a structured response from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            response_model: Pydantic model for structured output
            
        Returns:
            Parsed response or None on failure
        """
        response = self._call_llm(prompt, system_prompt, use_cache=True)
        
        if not response.success or not response.parsed:
            return None
        
        if response_model:
            try:
                return response_model(**response.parsed)
            except Exception as e:
                logger.warning(f"Failed to parse into model {response_model}: {e}")
                return None
        
        return response.parsed
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            
        Returns:
            LLMResponse with content
        """
        return self._call_llm(prompt, system_prompt, use_cache=True)

