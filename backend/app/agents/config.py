"""
AI Agent Configuration

Manages LLM providers, model selection, and agent settings.
Prioritizes FREE providers (Groq) with fallbacks.
"""

import os
from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GROQ = "groq"  # FREE - Primary
    TOGETHER = "together"  # FREE credits - Fallback
    OPENAI = "openai"  # Paid - Optional


class TaskComplexity(str, Enum):
    """Task complexity levels for model selection"""
    SIMPLE = "simple"  # Use fast 8B model
    MEDIUM = "medium"  # Use 70B model
    COMPLEX = "complex"  # Use best available


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.2
    max_tokens: int = 2000
    timeout: int = 30
    
    
@dataclass
class AgentConfig:
    """
    Central configuration for the AI Agent system.
    
    Loads settings from environment variables with sensible defaults.
    Prioritizes FREE Groq API for all operations.
    """
    
    # API Keys (loaded from environment)
    groq_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    together_api_key: Optional[str] = field(default_factory=lambda: os.getenv("TOGETHER_API_KEY"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    
    # Model configurations
    primary_model: str = "llama-3.1-70b-versatile"  # Groq - strategic tasks
    fast_model: str = "llama-3.1-8b-instant"  # Groq - simple tasks
    fallback_model: str = "meta-llama/Llama-3.1-70B-Instruct-Turbo"  # Together.ai
    
    # Rate limits (Groq free tier)
    groq_daily_limit: int = 14400  # Requests per day
    groq_requests_per_minute: int = 30
    
    # Agent execution settings
    cycle_interval_seconds: int = 300  # 5 minutes between cycles
    urgent_check_interval: int = 60  # 1 minute for urgent checks
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 2
    
    # Processing settings
    batch_size: int = 10
    parallel_processing: bool = True
    
    # Logging
    log_decisions: bool = True
    log_level: str = "INFO"
    
    # Feature flags
    enable_cost_tracking: bool = True
    enable_fallback: bool = True
    use_mock_llm: bool = False  # For testing without API calls
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate()
    
    def _validate(self):
        """Validate that required API keys are present"""
        if not self.groq_api_key and not self.use_mock_llm:
            logger.warning(
                "GROQ_API_KEY not set. AI agents will not work without it. "
                "Get a FREE key at https://console.groq.com"
            )
        
        if not self.together_api_key:
            logger.info(
                "TOGETHER_API_KEY not set. Fallback to Together.ai disabled. "
                "Get FREE $25 credits at https://api.together.xyz"
            )
    
    @property
    def has_groq(self) -> bool:
        """Check if Groq is configured"""
        return bool(self.groq_api_key)
    
    @property
    def has_together(self) -> bool:
        """Check if Together.ai is configured"""
        return bool(self.together_api_key)
    
    @property
    def has_openai(self) -> bool:
        """Check if OpenAI is configured"""
        return bool(self.openai_api_key)
    
    @property
    def primary_provider(self) -> LLMProvider:
        """Get the primary available provider"""
        if self.has_groq:
            return LLMProvider.GROQ
        elif self.has_together:
            return LLMProvider.TOGETHER
        elif self.has_openai:
            return LLMProvider.OPENAI
        else:
            raise ValueError("No LLM provider configured. Set GROQ_API_KEY in .env")
    
    def get_model_for_task(self, complexity: TaskComplexity) -> ModelConfig:
        """
        Get appropriate model based on task complexity.
        
        Args:
            complexity: Task complexity level
            
        Returns:
            ModelConfig for the appropriate model
        """
        if complexity == TaskComplexity.SIMPLE:
            return ModelConfig(
                provider=LLMProvider.GROQ,
                model_name=self.fast_model,
                temperature=0.1,
                max_tokens=1000,
                timeout=20
            )
        elif complexity == TaskComplexity.MEDIUM:
            return ModelConfig(
                provider=LLMProvider.GROQ,
                model_name=self.primary_model,
                temperature=0.2,
                max_tokens=2000,
                timeout=30
            )
        else:  # COMPLEX
            return ModelConfig(
                provider=LLMProvider.GROQ,
                model_name=self.primary_model,
                temperature=0.2,
                max_tokens=3000,
                timeout=45
            )


# Agent-specific model mappings
AGENT_MODEL_MAPPING: Dict[str, TaskComplexity] = {
    "source_monitor": TaskComplexity.MEDIUM,  # Needs reasoning
    "processing": TaskComplexity.SIMPLE,  # Fast classification
    "priority_detection": TaskComplexity.MEDIUM,  # Accuracy critical
    "validation": TaskComplexity.SIMPLE,  # Pattern recognition
    "scheduler": TaskComplexity.MEDIUM,  # Strategic planning
    "orchestrator": TaskComplexity.MEDIUM,  # Coordination
}


# Singleton configuration instance
_config: Optional[AgentConfig] = None


def get_agent_config() -> AgentConfig:
    """
    Get the singleton AgentConfig instance.
    
    Returns:
        AgentConfig: Configuration instance
    """
    global _config
    if _config is None:
        _config = AgentConfig()
    return _config


def reset_config():
    """Reset configuration (useful for testing)"""
    global _config
    _config = None
