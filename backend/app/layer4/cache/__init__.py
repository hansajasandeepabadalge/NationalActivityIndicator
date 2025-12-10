"""
Layer 4 Cache Module

Provides caching for LLM responses to reduce API costs and latency.
"""

from app.layer4.cache.manager import CacheManager

__all__ = ["CacheManager"]
