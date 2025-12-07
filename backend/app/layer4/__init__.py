"""
Layer 4: Business Insights Layer

This layer provides high-level business intelligence by aggregating data
from Layer 3 and generating actionable insights using LLM technology.

Components:
- LLM Engine: OpenAI/Anthropic integration for insight generation
- Cache: Redis-based caching for LLM responses
- Data: Aggregation and context preparation for LLM
"""

# LLM Engine exports
from app.layer4.llm import UnifiedLLMClient, LLMConfig, LLMInsightService, PromptTemplateManager

# Cache exports
from app.layer4.cache import CacheManager

# Data exports
from app.layer4.data import DataAggregator, Layer3Connector

__all__ = [
    # LLM
    "UnifiedLLMClient",
    "LLMConfig",
    "LLMInsightService",
    "PromptTemplateManager",
    # Cache
    "CacheManager",
    # Data
    "DataAggregator",
    "Layer3Connector",
]
