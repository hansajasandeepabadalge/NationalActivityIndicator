"""
Layer 4: Contextual Intelligence Module

Provides comprehensive contextual analysis for business insights:
- Industry benchmarking and context
- Historical event matching and pattern analysis
- Cross-industry dependency tracking
- Cascading impact modeling
- Competitive intelligence
"""

from app.layer4.context.industry_context import (
    IndustryContextProvider,
    IndustryBenchmark,
)

from app.layer4.context.historical_context import (
    HistoricalContextAnalyzer,
    HistoricalEvent,
    HistoricalMatch,
    TrendContext,
)

from app.layer4.context.cross_industry import (
    CrossIndustryAnalyzer,
    CrossIndustryInsight,
    IndustryRelationship,
    ImpactDirection,
    ImpactStrength,
)

from app.layer4.context.cascading_impacts import (
    CascadingImpactAnalyzer,
    CascadeChain,
    CascadeNode,
    PropagationModel,
    ImpactPhase,
)

from app.layer4.context.competitive_intel import (
    CompetitiveIntelligenceAnalyzer,
    CompetitorProfile,
    CompetitorMove,
    MarketPositionAnalysis,
    CompetitorMoveType,
    ThreatLevel,
    OpportunityLevel,
)


__all__ = [
    # Industry Context
    "IndustryContextProvider",
    "IndustryBenchmark",
    
    # Historical Context
    "HistoricalContextAnalyzer",
    "HistoricalEvent",
    "HistoricalMatch",
    "TrendContext",
    
    # Cross-Industry
    "CrossIndustryAnalyzer",
    "CrossIndustryInsight",
    "IndustryRelationship",
    "ImpactDirection",
    "ImpactStrength",
    
    # Cascading Impacts
    "CascadingImpactAnalyzer",
    "CascadeChain",
    "CascadeNode",
    "PropagationModel",
    "ImpactPhase",
    
    # Competitive Intelligence
    "CompetitiveIntelligenceAnalyzer",
    "CompetitorProfile",
    "CompetitorMove",
    "MarketPositionAnalysis",
    "CompetitorMoveType",
    "ThreatLevel",
    "OpportunityLevel",
]
