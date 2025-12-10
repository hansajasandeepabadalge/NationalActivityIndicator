"""SQLAlchemy models package - Integrated from Developer A and Developer B"""

# Layer 1: Raw Article and Agent models
from app.models.raw_article import (
    RawArticle,
    RawContent,
    SourceInfo,
    ScrapeMetadata,
    ValidationStatus
)

from app.models.agent_models import (
    UrgencyLevel,
    PriorityLevel,
    AgentDecision,
    ScrapingSchedule,
    UrgencyClassification,
    QualityValidation,
    AgentMetrics,
    SourceConfig
)

# Layer 2 AI Enhancement Models
from app.models.processed_article_model import ProcessedArticleModel
from app.models.entity_models import (
    EntityMaster,
    ArticleEntity,
    TopicTrend
)

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

# Layer 4: Business Insights Engine models
from app.models.business_insight_models import (
    RiskOpportunityDefinition,
    BusinessInsight,
    InsightRecommendation,
    InsightFeedback,
    ScenarioSimulation,
    CompetitiveIntelligence,
    InsightTracking,
    InsightScoreHistory
)

from app.models.company_profile_models import (
    CompanyProfile
)

# Source Reputation System
from app.models.source_reputation_models import (
    SourceReputation,
    SourceReputationHistory,
    QualityFilterLog,
    ReputationThreshold,
    ReputationTier,
    FilterAction,
    DEFAULT_THRESHOLDS
)

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
    # Layer 4: Business Insights Engine
    "RiskOpportunityDefinition",
    "BusinessInsight",
    "InsightRecommendation",
    "InsightFeedback",
    "ScenarioSimulation",
    "CompetitiveIntelligence",
    "InsightTracking",
    "InsightScoreHistory",
    "CompanyProfile",
    # Layer 1: Raw Article and Agent models
    "RawArticle",
    "RawContent",
    "SourceInfo",
    "ScrapeMetadata",
    "ValidationStatus",
    "UrgencyLevel",
    "PriorityLevel",
    "AgentDecision",
    "ScrapingSchedule",
    "UrgencyClassification",
    "QualityValidation",
    "AgentMetrics",
    "SourceConfig",
    # Source Reputation System
    "SourceReputation",
    "SourceReputationHistory",
    "QualityFilterLog",
    "ReputationThreshold",
    "ReputationTier",
    "FilterAction",
    "DEFAULT_THRESHOLDS",
    # Layer 2: AI Enhancement
    "ProcessedArticleModel",
    "EntityMaster",
    "ArticleEntity",
    "TopicTrend",
]
