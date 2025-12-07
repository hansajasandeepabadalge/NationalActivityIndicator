"""
Layer 2 LLM Enhancement Configuration

This module provides centralized configuration for all LLM-powered services.
Settings can be overridden via environment variables.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================================
# Environment Variable Helpers
# ============================================================================

def get_env_bool(key: str, default: bool = True) -> bool:
    """Get boolean from environment variable."""
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes")


def get_env_float(key: str, default: float) -> float:
    """Get float from environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_int(key: str, default: int) -> int:
    """Get integer from environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


# ============================================================================
# Groq LLM Settings
# ============================================================================

@dataclass
class GroqSettings:
    """Groq API configuration."""
    
    # API credentials
    api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    
    # Model settings
    model: str = "llama-3.1-70b-versatile"  # Free tier
    temperature: float = 0.2
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3
    
    # Rate limiting (Groq free tier limits)
    requests_per_minute: int = 30
    tokens_per_minute: int = 6000
    
    def __post_init__(self):
        # Override from environment if set
        self.model = os.getenv("GROQ_MODEL", self.model)
        self.temperature = get_env_float("GROQ_TEMPERATURE", self.temperature)
        self.max_tokens = get_env_int("GROQ_MAX_TOKENS", self.max_tokens)
        self.timeout = get_env_int("GROQ_TIMEOUT", self.timeout)
        self.max_retries = get_env_int("GROQ_MAX_RETRIES", self.max_retries)


# ============================================================================
# Caching Settings
# ============================================================================

@dataclass
class CacheSettings:
    """Response caching configuration."""
    
    enabled: bool = True
    ttl_hours: int = 24
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", ""))
    prefix: str = "layer2_llm"
    
    def __post_init__(self):
        self.enabled = get_env_bool("LLM_CACHE_ENABLED", self.enabled)
        self.ttl_hours = get_env_int("LLM_CACHE_TTL_HOURS", self.ttl_hours)


# ============================================================================
# Feature Flags
# ============================================================================

@dataclass
class FeatureFlags:
    """Feature toggle configuration."""
    
    # LLM-powered features
    llm_classification_enabled: bool = True
    advanced_sentiment_enabled: bool = True
    smart_ner_enabled: bool = True
    topic_modeling_enabled: bool = True
    quality_scoring_enabled: bool = True
    adaptive_indicators_enabled: bool = True
    
    # Rollout percentages (for gradual deployment)
    llm_classification_percentage: float = 100.0
    advanced_sentiment_percentage: float = 100.0
    smart_ner_percentage: float = 100.0
    
    def __post_init__(self):
        self.llm_classification_enabled = get_env_bool(
            "LLM_CLASSIFICATION_ENABLED", self.llm_classification_enabled
        )
        self.advanced_sentiment_enabled = get_env_bool(
            "ADVANCED_SENTIMENT_ENABLED", self.advanced_sentiment_enabled
        )
        self.smart_ner_enabled = get_env_bool(
            "SMART_NER_ENABLED", self.smart_ner_enabled
        )
        self.topic_modeling_enabled = get_env_bool(
            "TOPIC_MODELING_ENABLED", self.topic_modeling_enabled
        )
        self.quality_scoring_enabled = get_env_bool(
            "QUALITY_SCORING_ENABLED", self.quality_scoring_enabled
        )
        self.adaptive_indicators_enabled = get_env_bool(
            "ADAPTIVE_INDICATORS_ENABLED", self.adaptive_indicators_enabled
        )
        
        # Rollout percentages
        self.llm_classification_percentage = get_env_float(
            "LLM_CLASSIFICATION_PERCENTAGE", self.llm_classification_percentage
        )
        self.advanced_sentiment_percentage = get_env_float(
            "ADVANCED_SENTIMENT_PERCENTAGE", self.advanced_sentiment_percentage
        )
        self.smart_ner_percentage = get_env_float(
            "SMART_NER_PERCENTAGE", self.smart_ner_percentage
        )


# ============================================================================
# Classification Settings
# ============================================================================

@dataclass
class ClassificationSettings:
    """LLM classification configuration."""
    
    # Processing thresholds
    min_text_length: int = 100
    max_text_length: int = 4000
    complexity_threshold: float = 0.6
    
    # Confidence thresholds
    high_confidence_threshold: float = 0.8
    low_confidence_threshold: float = 0.5
    
    # Multi-label settings
    max_categories: int = 4
    secondary_category_threshold: float = 0.3
    
    def __post_init__(self):
        self.min_text_length = get_env_int("CLASSIFICATION_MIN_LENGTH", self.min_text_length)
        self.max_text_length = get_env_int("CLASSIFICATION_MAX_LENGTH", self.max_text_length)
        self.complexity_threshold = get_env_float(
            "CLASSIFICATION_COMPLEXITY_THRESHOLD", self.complexity_threshold
        )


# ============================================================================
# Sentiment Settings
# ============================================================================

@dataclass
class SentimentSettings:
    """Advanced sentiment analysis configuration."""
    
    # Processing options
    skip_neutral_llm: bool = True
    neutral_threshold: float = 0.15
    min_text_length: int = 50
    
    # Dimensional weights
    dimension_weights: Dict[str, float] = field(default_factory=lambda: {
        "overall": 0.30,
        "business_confidence": 0.25,
        "public_mood": 0.20,
        "economic_outlook": 0.25
    })
    
    def __post_init__(self):
        self.skip_neutral_llm = get_env_bool("SENTIMENT_SKIP_NEUTRAL", self.skip_neutral_llm)
        self.neutral_threshold = get_env_float(
            "SENTIMENT_NEUTRAL_THRESHOLD", self.neutral_threshold
        )


# ============================================================================
# Entity Extraction Settings
# ============================================================================

@dataclass
class EntitySettings:
    """Smart entity extraction configuration."""
    
    min_text_length: int = 50
    max_entities: int = 50
    max_relationships: int = 20
    
    # Entity linking
    enable_entity_linking: bool = True
    fuzzy_match_threshold: float = 0.85
    
    # Importance thresholds
    high_importance_threshold: float = 0.7
    min_importance_threshold: float = 0.3


# ============================================================================
# Topic Modeling Settings
# ============================================================================

@dataclass
class TopicSettings:
    """Topic modeling configuration."""
    
    # ChromaDB settings
    collection_name: str = "article_topics"
    persist_directory: Optional[str] = None
    
    # Clustering settings
    similarity_threshold: float = 0.75
    min_cluster_size: int = 3
    
    # Trending detection
    trending_velocity_threshold: float = 1.0
    emerging_momentum_threshold: float = 0.5
    
    def __post_init__(self):
        self.persist_directory = os.getenv("CHROMADB_PERSIST_DIR", self.persist_directory)
        self.similarity_threshold = get_env_float(
            "TOPIC_SIMILARITY_THRESHOLD", self.similarity_threshold
        )


# ============================================================================
# Quality Scoring Settings
# ============================================================================

@dataclass
class QualitySettings:
    """Quality scoring configuration."""
    
    # Component weights (must sum to 1.0)
    dimension_weights: Dict[str, float] = field(default_factory=lambda: {
        "classification": 0.25,
        "sentiment": 0.20,
        "entity": 0.20,
        "validation": 0.20,
        "completeness": 0.15
    })
    
    # Quality thresholds
    min_acceptable_score: float = 50.0
    excellent_threshold: float = 90.0
    good_threshold: float = 75.0
    fair_threshold: float = 50.0
    poor_threshold: float = 25.0
    
    def __post_init__(self):
        self.min_acceptable_score = get_env_float(
            "QUALITY_MIN_ACCEPTABLE", self.min_acceptable_score
        )


# ============================================================================
# Pipeline Settings
# ============================================================================

@dataclass
class PipelineSettings:
    """Enhanced pipeline configuration."""
    
    # Processing mode
    parallel_processing: bool = True
    max_concurrency: int = 5
    timeout_seconds: int = 60
    
    # Fallback behavior
    use_fallbacks: bool = True
    log_fallback_usage: bool = True
    
    # Quality control
    reprocess_on_low_quality: bool = False
    min_quality_for_publish: float = 50.0
    
    def __post_init__(self):
        self.parallel_processing = get_env_bool(
            "PIPELINE_PARALLEL", self.parallel_processing
        )
        self.max_concurrency = get_env_int("PIPELINE_CONCURRENCY", self.max_concurrency)
        self.timeout_seconds = get_env_int("PIPELINE_TIMEOUT", self.timeout_seconds)


# ============================================================================
# Main Configuration Class
# ============================================================================

@dataclass
class Layer2LLMConfig:
    """
    Complete Layer 2 LLM enhancement configuration.
    
    Usage:
        config = Layer2LLMConfig()
        print(config.groq.model)
        print(config.features.llm_classification_enabled)
    """
    
    groq: GroqSettings = field(default_factory=GroqSettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    classification: ClassificationSettings = field(default_factory=ClassificationSettings)
    sentiment: SentimentSettings = field(default_factory=SentimentSettings)
    entity: EntitySettings = field(default_factory=EntitySettings)
    topic: TopicSettings = field(default_factory=TopicSettings)
    quality: QualitySettings = field(default_factory=QualitySettings)
    pipeline: PipelineSettings = field(default_factory=PipelineSettings)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        import dataclasses
        return {
            "groq": dataclasses.asdict(self.groq),
            "cache": dataclasses.asdict(self.cache),
            "features": dataclasses.asdict(self.features),
            "classification": dataclasses.asdict(self.classification),
            "sentiment": dataclasses.asdict(self.sentiment),
            "entity": dataclasses.asdict(self.entity),
            "topic": dataclasses.asdict(self.topic),
            "quality": dataclasses.asdict(self.quality),
            "pipeline": dataclasses.asdict(self.pipeline)
        }
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        """
        issues = []
        
        # Check Groq API key
        if self.features.llm_classification_enabled and not self.groq.api_key:
            issues.append("GROQ_API_KEY not set but LLM features enabled")
        
        # Check quality weights sum to 1.0
        weight_sum = sum(self.quality.dimension_weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            issues.append(f"Quality dimension weights sum to {weight_sum}, expected 1.0")
        
        # Check sentiment weights sum to 1.0
        sent_weight_sum = sum(self.sentiment.dimension_weights.values())
        if abs(sent_weight_sum - 1.0) > 0.01:
            issues.append(f"Sentiment dimension weights sum to {sent_weight_sum}, expected 1.0")
        
        return issues


# ============================================================================
# Global Configuration Instance
# ============================================================================

_config: Optional[Layer2LLMConfig] = None


def get_llm_config() -> Layer2LLMConfig:
    """Get or create global LLM configuration instance."""
    global _config
    if _config is None:
        _config = Layer2LLMConfig()
    return _config


def reset_config():
    """Reset global configuration (useful for testing)."""
    global _config
    _config = None


# ============================================================================
# Configuration Summary
# ============================================================================

def print_config_summary():
    """Print configuration summary for debugging."""
    config = get_llm_config()
    
    print("\n" + "=" * 60)
    print("Layer 2 LLM Enhancement Configuration")
    print("=" * 60)
    
    print("\n[Groq LLM]")
    print(f"  Model: {config.groq.model}")
    print(f"  API Key: {'*' * 8 if config.groq.api_key else 'NOT SET'}")
    print(f"  Temperature: {config.groq.temperature}")
    print(f"  Max Tokens: {config.groq.max_tokens}")
    
    print("\n[Feature Flags]")
    print(f"  LLM Classification: {config.features.llm_classification_enabled}")
    print(f"  Advanced Sentiment: {config.features.advanced_sentiment_enabled}")
    print(f"  Smart NER: {config.features.smart_ner_enabled}")
    print(f"  Topic Modeling: {config.features.topic_modeling_enabled}")
    print(f"  Quality Scoring: {config.features.quality_scoring_enabled}")
    
    print("\n[Caching]")
    print(f"  Enabled: {config.cache.enabled}")
    print(f"  TTL Hours: {config.cache.ttl_hours}")
    print(f"  Redis URL: {'Set' if config.cache.redis_url else 'Not Set (in-memory)'}")
    
    print("\n[Pipeline]")
    print(f"  Parallel Processing: {config.pipeline.parallel_processing}")
    print(f"  Max Concurrency: {config.pipeline.max_concurrency}")
    print(f"  Timeout: {config.pipeline.timeout_seconds}s")
    
    issues = config.validate()
    if issues:
        print("\n[Configuration Issues]")
        for issue in issues:
            print(f"  ⚠ {issue}")
    else:
        print("\n✓ Configuration valid")
    
    print("=" * 60 + "\n")
