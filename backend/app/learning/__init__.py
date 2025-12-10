"""
Adaptive Learning System for Layer 1

This module provides self-improving quality mechanisms for the data acquisition pipeline.
It learns from historical performance, downstream feedback, and quality patterns to
automatically optimize scraping, validation, and quality thresholds.

Components:
- MetricsTracker: Collects and stores performance metrics
- FeedbackLoop: Receives and processes downstream signals
- AutoTuner: Dynamically adjusts parameters based on learning
- PerformanceOptimizer: Optimizes scraping and processing performance
- QualityAnalyzer: Identifies quality issues and suggests improvements

Usage:
    from app.learning import AdaptiveLearningSystem
    
    learning_system = AdaptiveLearningSystem(db_session)
    await learning_system.record_scrape_result(source_id, result)
    await learning_system.receive_feedback(article_id, feedback)
    recommendations = await learning_system.get_recommendations(source_id)
"""

from app.learning.metrics_tracker import MetricsTracker, MetricType, SourceMetrics
from app.learning.feedback_loop import FeedbackLoop, FeedbackType, FeedbackSignal
from app.learning.auto_tuner import AutoTuner, TuningConfig, TuningRecommendation
from app.learning.performance_optimizer import PerformanceOptimizer, PerformanceProfile, RetryStrategy
from app.learning.quality_analyzer import QualityAnalyzer, QualityIssue, QualityReport

# Import main system after dependencies
from app.learning.adaptive_system import (
    AdaptiveLearningSystem,
    LearningSystemConfig,
    LearningMode
)

# Integration utilities
from app.learning.integration import (
    LearningOrchestrator,
    LearningHooks,
    create_learning_orchestrator,
    get_learning_system
)

__all__ = [
    # Main system
    "AdaptiveLearningSystem",
    "LearningSystemConfig",
    "LearningMode",
    
    # Integration
    "LearningOrchestrator",
    "LearningHooks",
    "create_learning_orchestrator",
    "get_learning_system",
    
    # Metrics
    "MetricsTracker",
    "MetricType", 
    "SourceMetrics",
    
    # Feedback
    "FeedbackLoop",
    "FeedbackType",
    "FeedbackSignal",
    
    # Tuning
    "AutoTuner",
    "TuningConfig",
    "TuningRecommendation",
    
    # Performance
    "PerformanceOptimizer",
    "PerformanceProfile",
    "RetryStrategy",
    
    # Quality
    "QualityAnalyzer",
    "QualityIssue",
    "QualityReport",
]
