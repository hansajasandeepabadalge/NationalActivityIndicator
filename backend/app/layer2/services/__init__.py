"""
Layer 2 AI/LLM Enhancement Services

This module provides intelligent AI-powered services for enhanced article processing:

Services:
- LLMClassifier: Groq Llama 3.1 70B classification (90%+ accuracy)
- AdvancedSentimentAnalyzer: Multi-dimensional sentiment analysis
- SmartEntityExtractor: Entity relationships and linking
- TopicModeler: Semantic topic extraction with trends
- QualityScorer: 0-100 quality scoring for all outputs
- EnhancedPipeline: Unified orchestration with fallback

Configuration:
All services can be toggled via feature flags in config.
If LLM services fail, the system falls back to existing basic services.

Cost: $0/month using Groq's free tier
"""

import os
from typing import Optional

# ============================================================================
# Feature Flags - Toggle individual enhancements
# ============================================================================

# Can be overridden via environment variables
LLM_CLASSIFICATION_ENABLED = os.getenv("LLM_CLASSIFICATION_ENABLED", "true").lower() == "true"
ADVANCED_SENTIMENT_ENABLED = os.getenv("ADVANCED_SENTIMENT_ENABLED", "true").lower() == "true"
SMART_NER_ENABLED = os.getenv("SMART_NER_ENABLED", "true").lower() == "true"
TOPIC_MODELING_ENABLED = os.getenv("TOPIC_MODELING_ENABLED", "true").lower() == "true"
QUALITY_SCORING_ENABLED = os.getenv("QUALITY_SCORING_ENABLED", "true").lower() == "true"
ADAPTIVE_INDICATORS_ENABLED = os.getenv("ADAPTIVE_INDICATORS_ENABLED", "true").lower() == "true"


# ============================================================================
# Singleton Instances (Lazy Loading)
# ============================================================================

_llm_classifier = None
_sentiment_analyzer = None
_entity_extractor = None
_topic_modeler = None
_quality_scorer = None
_enhanced_pipeline = None


def get_llm_classifier():
    """Get LLM classifier singleton."""
    global _llm_classifier
    if _llm_classifier is None:
        from .llm_classifier import create_llm_classifier
        _llm_classifier = create_llm_classifier()
    return _llm_classifier


def get_advanced_sentiment():
    """Get advanced sentiment analyzer singleton."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        from .advanced_sentiment import create_advanced_sentiment_analyzer
        _sentiment_analyzer = create_advanced_sentiment_analyzer()
    return _sentiment_analyzer


def get_smart_entity_extractor():
    """Get smart entity extractor singleton."""
    global _entity_extractor
    if _entity_extractor is None:
        from .smart_entity_extractor import create_smart_entity_extractor
        _entity_extractor = create_smart_entity_extractor()
    return _entity_extractor


def get_topic_modeler():
    """Get topic modeler singleton."""
    global _topic_modeler
    if _topic_modeler is None:
        from .topic_modeler import create_topic_modeler
        _topic_modeler = create_topic_modeler()
    return _topic_modeler


def get_quality_scorer():
    """Get quality scorer singleton."""
    global _quality_scorer
    if _quality_scorer is None:
        from .quality_scorer import create_quality_scorer
        _quality_scorer = create_quality_scorer()
    return _quality_scorer


def get_enhanced_pipeline():
    """Get enhanced pipeline singleton."""
    global _enhanced_pipeline
    if _enhanced_pipeline is None:
        from .enhanced_pipeline import create_enhanced_pipeline
        _enhanced_pipeline = create_enhanced_pipeline()
    return _enhanced_pipeline


def reset_singletons():
    """Reset all singletons - useful for testing."""
    global _llm_classifier, _sentiment_analyzer, _entity_extractor
    global _topic_modeler, _quality_scorer, _enhanced_pipeline
    _llm_classifier = None
    _sentiment_analyzer = None
    _entity_extractor = None
    _topic_modeler = None
    _quality_scorer = None
    _enhanced_pipeline = None


# ============================================================================
# Exports
# ============================================================================

# Feature flags
__all__ = [
    # Feature flags
    "LLM_CLASSIFICATION_ENABLED",
    "ADVANCED_SENTIMENT_ENABLED",
    "SMART_NER_ENABLED",
    "TOPIC_MODELING_ENABLED",
    "QUALITY_SCORING_ENABLED",
    "ADAPTIVE_INDICATORS_ENABLED",
    
    # Singleton getters
    "get_llm_classifier",
    "get_advanced_sentiment",
    "get_smart_entity_extractor",
    "get_topic_modeler",
    "get_quality_scorer",
    "get_enhanced_pipeline",
    "reset_singletons",
]
