"""
Feedback & Learning System for Layer 4 Business Insights

This module provides:
- FeedbackCollector: Collect user feedback on insights
- OutcomeTracker: Track actual outcomes vs predictions
- ModelRetrainer: Update model weights based on feedback
- AdaptiveThresholds: Self-adjusting risk/opportunity thresholds
- PersonalizationEngine: Learn user preferences over time
"""

from .feedback_collector import (
    FeedbackCollector,
    InsightFeedback,
    FeedbackType,
    FeedbackRating,
    FeedbackSummary,
)
from .outcome_tracker import (
    OutcomeTracker,
    PredictedOutcome,
    ActualOutcome,
    OutcomeComparison,
    AccuracyMetrics,
)
from .model_retrainer import (
    ModelRetrainer,
    RetrainingConfig,
    RetrainingResult,
    WeightUpdate,
)
from .adaptive_thresholds import (
    AdaptiveThresholdManager,
    ThresholdConfig,
    ThresholdAdjustment,
    ThresholdHistory,
)
from .personalization import (
    PersonalizationEngine,
    UserPreferences,
    PreferenceUpdate,
    PersonalizedSettings,
)

__all__ = [
    # Feedback Collector
    "FeedbackCollector",
    "InsightFeedback",
    "FeedbackType",
    "FeedbackRating",
    "FeedbackSummary",
    # Outcome Tracker
    "OutcomeTracker",
    "PredictedOutcome",
    "ActualOutcome",
    "OutcomeComparison",
    "AccuracyMetrics",
    # Model Retrainer
    "ModelRetrainer",
    "RetrainingConfig",
    "RetrainingResult",
    "WeightUpdate",
    # Adaptive Thresholds
    "AdaptiveThresholdManager",
    "ThresholdConfig",
    "ThresholdAdjustment",
    "ThresholdHistory",
    # Personalization
    "PersonalizationEngine",
    "UserPreferences",
    "PreferenceUpdate",
    "PersonalizedSettings",
]
