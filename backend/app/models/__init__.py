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
try:
    from app.models.indicator import IndicatorDependency, IndicatorThreshold
except ImportError:
    IndicatorDependency = None
    IndicatorThreshold = None

# Developer B trend model (alias to TrendAnalysis)
try:
    from app.models.indicator_value import IndicatorTrend
except ImportError:
    IndicatorTrend = TrendAnalysis  # Fallback to Developer A's model

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
    "IndicatorTrend",  # Alias
    # Mapping models
    "ArticleIndicatorMapping",
    # Extended models (Developer B)
    "IndicatorDependency",
    "IndicatorThreshold",
]
