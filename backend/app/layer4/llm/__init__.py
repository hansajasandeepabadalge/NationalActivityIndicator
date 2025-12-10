"""
Layer 4 LLM Module

Provides LLM-based insight generation capabilities:
- UnifiedLLMClient: Unified client for OpenAI, Anthropic, and DeepSeek
- LLMInsightService: High-level service for generating business insights
- PromptTemplateManager: Manages all LLM prompt templates
"""

from app.layer4.llm.llm_client import UnifiedLLMClient, LLMConfig, openai_client, anthropic_client, deepseek_client
from app.layer4.llm.llm_service import LLMInsightService
from app.layer4.llm.prompts import PromptTemplateManager

__all__ = [
    "UnifiedLLMClient",
    "LLMConfig",
    "openai_client",
    "anthropic_client",
    "deepseek_client",
    "LLMInsightService",
    "PromptTemplateManager",
]
