"""SQLAlchemy models package - Integrated from Developer A and Developer B"""

# Developer A models (comprehensive with relationships and ENUMs)
from app.models.indicator_models import (
    IndicatorDefinition,
    IndicatorKeyword,
    IndicatorValue,
    IndicatorEvent,
    IndicatorCorrelation
)

from app.models.ml_models import (
    MLClassificationResult
)

from app.models.analysis_models import (
    TrendAnalysis
)

from app.models.article_mapping import (
    ArticleIndicatorMapping
)

# Developer B additional models (dependency/threshold tracking)
from app.models.indicator import IndicatorDependency, IndicatorThreshold

# Alias for backward compatibility
IndicatorTrend = TrendAnalysis

__all__ = [
    # Core indicator models
    "IndicatorDefinition",
    "IndicatorKeyword",
    "IndicatorValue",
    "IndicatorEvent",
    "IndicatorCorrelation",
    # ML models
    "MLClassificationResult",
    # Analysis models
    "TrendAnalysis",
    "IndicatorTrend",  # Alias to TrendAnalysis
    # Mapping models
    "ArticleIndicatorMapping",
    # Extended models (Developer B)
    "IndicatorDependency",
    "IndicatorThreshold",
]
