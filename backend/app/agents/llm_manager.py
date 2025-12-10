"""
LLM Manager - Handles LLM initialization, selection, and fallbacks.

Provides a unified interface to multiple LLM providers:
- Groq (FREE - Primary)
- DeepSeek (Very affordable - Secondary)
- Together.ai (FREE credits - Fallback)
- OpenAI (Paid - Optional)
"""

import logging
from typing import Optional, Any, Dict
from datetime import datetime, date
from dataclasses import dataclass, field

from app.agents.config import (
    AgentConfig, 
    get_agent_config, 
    LLMProvider, 
    TaskComplexity,
    ModelConfig,
    AGENT_MODEL_MAPPING
)

logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Track API usage statistics"""
    date: date = field(default_factory=date.today)
    groq_requests: int = 0
    deepseek_requests: int = 0
    together_requests: int = 0
    openai_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    
    def reset_if_new_day(self):
        """Reset counters if it's a new day"""
        if date.today() != self.date:
            self.date = date.today()
            self.groq_requests = 0
            self.deepseek_requests = 0
            self.together_requests = 0
            self.openai_requests = 0
            self.total_tokens = 0
            self.total_cost_usd = 0.0


class LLMManager:
    """
    Manages LLM instances with automatic fallback and usage tracking.
    
    Prioritizes FREE Groq API, falls back to DeepSeek or Together.ai if rate limited,
    and optionally uses OpenAI for premium quality if configured.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize LLM Manager.
        
        Args:
            config: Optional AgentConfig. Uses singleton if not provided.
        """
        self.config = config or get_agent_config()
        self.usage = UsageStats()
        self._llm_cache: Dict[str, Any] = {}
        
        # Initialize LLMs lazily
        self._groq_llm: Optional[Any] = None
        self._deepseek_llm: Optional[Any] = None
        self._together_llm: Optional[Any] = None
        self._openai_llm: Optional[Any] = None
        
        logger.info(f"LLMManager initialized. Primary provider: {self.config.primary_provider.value}")
    
    def _get_deepseek_llm(self, model_config: ModelConfig) -> Any:
        """Get or create DeepSeek LLM instance (OpenAI-compatible API)"""
        cache_key = f"deepseek_{model_config.model_name}"
        
        if cache_key not in self._llm_cache:
            try:
                from langchain_openai import ChatOpenAI
                
                self._llm_cache[cache_key] = ChatOpenAI(
                    model=self.config.deepseek_model,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens,
                    api_key=self.config.deepseek_api_key,
                    base_url=self.config.deepseek_base_url,
                    request_timeout=model_config.timeout
                )
                logger.debug(f"Created DeepSeek LLM: {self.config.deepseek_model}")
            except ImportError:
                logger.error("langchain-openai not installed. Run: pip install langchain-openai")
                raise
            except Exception as e:
                logger.error(f"Failed to create DeepSeek LLM: {e}")
                raise
        
        return self._llm_cache[cache_key]
    
    def _get_groq_llm(self, model_config: ModelConfig) -> Any:
        """Get or create Groq LLM instance"""
        cache_key = f"groq_{model_config.model_name}"
        
        if cache_key not in self._llm_cache:
            try:
                from langchain_groq import ChatGroq
                
                self._llm_cache[cache_key] = ChatGroq(
                    model=model_config.model_name,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens,
                    api_key=self.config.groq_api_key,
                    request_timeout=model_config.timeout
                )
                logger.debug(f"Created Groq LLM: {model_config.model_name}")
            except ImportError:
                logger.error("langchain-groq not installed. Run: pip install langchain-groq")
                raise
            except Exception as e:
                logger.error(f"Failed to create Groq LLM: {e}")
                raise
        
        return self._llm_cache[cache_key]
    
    def _get_together_llm(self, model_config: ModelConfig) -> Any:
        """Get or create Together.ai LLM instance"""
        cache_key = f"together_{model_config.model_name}"
        
        if cache_key not in self._llm_cache:
            try:
                from langchain_community.llms import Together
                
                self._llm_cache[cache_key] = Together(
                    model=self.config.fallback_model,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens,
                    together_api_key=self.config.together_api_key
                )
                logger.debug(f"Created Together.ai LLM: {self.config.fallback_model}")
            except ImportError:
                logger.error("langchain-community not installed")
                raise
            except Exception as e:
                logger.error(f"Failed to create Together.ai LLM: {e}")
                raise
        
        return self._llm_cache[cache_key]
    
    def _get_openai_llm(self, model_config: ModelConfig) -> Any:
        """Get or create OpenAI LLM instance (optional, paid)"""
        cache_key = f"openai_{model_config.model_name}"
        
        if cache_key not in self._llm_cache:
            try:
                from langchain_openai import ChatOpenAI
                
                self._llm_cache[cache_key] = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens,
                    api_key=self.config.openai_api_key,
                    request_timeout=model_config.timeout
                )
                logger.debug("Created OpenAI LLM: gpt-3.5-turbo")
            except ImportError:
                logger.error("langchain-openai not installed")
                raise
            except Exception as e:
                logger.error(f"Failed to create OpenAI LLM: {e}")
                raise
        
        return self._llm_cache[cache_key]
    
    def get_llm_for_agent(self, agent_name: str) -> Any:
        """
        Get appropriate LLM for a specific agent.
        
        Args:
            agent_name: Name of the agent (e.g., "source_monitor")
            
        Returns:
            LLM instance configured for the agent's task complexity
        """
        complexity = AGENT_MODEL_MAPPING.get(agent_name, TaskComplexity.MEDIUM)
        return self.get_llm(complexity)
    
    def get_llm(self, complexity: TaskComplexity = TaskComplexity.MEDIUM) -> Any:
        """
        Get LLM based on task complexity with automatic fallback.
        
        Args:
            complexity: Task complexity level
            
        Returns:
            LLM instance
            
        Raises:
            ValueError: If no LLM provider is available
        """
        self.usage.reset_if_new_day()
        
        model_config = self.config.get_model_for_task(complexity)
        
        # Check Groq rate limit
        if self._is_groq_rate_limited():
            logger.warning("Groq rate limit approaching, switching to fallback")
            return self._get_fallback_llm(model_config)
        
        # Try primary provider (Groq)
        if self.config.has_groq:
            try:
                return self._get_groq_llm(model_config)
            except Exception as e:
                logger.warning(f"Groq unavailable: {e}, trying fallback")
        
        # Fallback to Together.ai
        return self._get_fallback_llm(model_config)
    
    def _is_groq_rate_limited(self) -> bool:
        """Check if we're approaching Groq's daily limit"""
        # Leave 20% buffer
        limit_threshold = int(self.config.groq_daily_limit * 0.8)
        return self.usage.groq_requests >= limit_threshold
    
    def _get_fallback_llm(self, model_config: ModelConfig) -> Any:
        """Get fallback LLM when primary (Groq) is unavailable"""
        # First fallback: DeepSeek (very affordable)
        if self.config.has_deepseek:
            try:
                logger.info("Using DeepSeek as fallback (affordable)")
                return self._get_deepseek_llm(model_config)
            except Exception as e:
                logger.warning(f"DeepSeek fallback failed: {e}")
        
        # Second fallback: Together.ai (free credits)
        if self.config.has_together:
            try:
                logger.info("Using Together.ai as fallback")
                return self._get_together_llm(model_config)
            except Exception as e:
                logger.warning(f"Together.ai fallback failed: {e}")
        
        # Last resort: OpenAI (paid)
        if self.config.has_openai:
            logger.warning("Using paid OpenAI as last resort fallback")
            return self._get_openai_llm(model_config)
        
        raise ValueError(
            "No LLM provider available. "
            "Set GROQ_API_KEY (FREE) or DEEPSEEK_API_KEY in your .env file. "
            "Get a Groq key at https://console.groq.com"
        )
    
    def track_usage(self, provider: LLMProvider, tokens: int = 0, cost: float = 0.0):
        """
        Track API usage for monitoring.
        
        Args:
            provider: Which provider was used
            tokens: Number of tokens used
            cost: Cost in USD (usually $0 for free providers)
        """
        self.usage.reset_if_new_day()
        
        if provider == LLMProvider.GROQ:
            self.usage.groq_requests += 1
        elif provider == LLMProvider.DEEPSEEK:
            self.usage.deepseek_requests += 1
        elif provider == LLMProvider.TOGETHER:
            self.usage.together_requests += 1
        elif provider == LLMProvider.OPENAI:
            self.usage.openai_requests += 1
        
        self.usage.total_tokens += tokens
        self.usage.total_cost_usd += cost
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        self.usage.reset_if_new_day()
        
        return {
            "date": str(self.usage.date),
            "groq_requests": self.usage.groq_requests,
            "groq_remaining": self.config.groq_daily_limit - self.usage.groq_requests,
            "together_requests": self.usage.together_requests,
            "openai_requests": self.usage.openai_requests,
            "total_tokens": self.usage.total_tokens,
            "total_cost_usd": self.usage.total_cost_usd,
            "cost_note": "Groq is FREE, Together.ai uses free credits"
        }


# Singleton instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get singleton LLMManager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager


def reset_llm_manager():
    """Reset LLM manager (useful for testing)"""
    global _llm_manager
    _llm_manager = None
