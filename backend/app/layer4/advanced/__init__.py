"""
Advanced Features Module for Layer 4 Business Insights Engine.

This module provides advanced analytical capabilities including:
- ML Impact Prediction: Machine learning for impact forecasting
- Portfolio Analysis: Multi-company risk aggregation
- Scenario Simulation: What-if analysis engine
- Correlation Analysis: Cross-indicator relationships
- Trend Forecasting: Time-series predictions
"""

from .ml_impact_predictor import (
    MLImpactPredictor,
    ImpactPrediction,
    FeatureSet,
    ModelMetrics,
    PredictionConfidence,
)

from .portfolio_analyzer import (
    PortfolioAnalyzer,
    Portfolio,
    PortfolioRisk,
    ConcentrationAlert,
    DiversificationScore,
)

from .scenario_simulator import (
    ScenarioSimulator,
    Scenario,
    SimulationResult,
    ImpactPropagation,
    SensitivityAnalysis,
)

from .correlation_analyzer import (
    CorrelationAnalyzer,
    CorrelationMatrix,
    LeadLagRelation,
    CausalLink,
    IndicatorRelationship,
)

from .trend_forecaster import (
    TrendForecaster,
    Trend,
    Forecast,
    SeasonalPattern,
    TrendDirection,
)

__all__ = [
    # ML Impact Prediction
    "MLImpactPredictor",
    "ImpactPrediction",
    "FeatureSet",
    "ModelMetrics",
    "PredictionConfidence",
    # Portfolio Analysis
    "PortfolioAnalyzer",
    "Portfolio",
    "PortfolioRisk",
    "ConcentrationAlert",
    "DiversificationScore",
    # Scenario Simulation
    "ScenarioSimulator",
    "Scenario",
    "SimulationResult",
    "ImpactPropagation",
    "SensitivityAnalysis",
    # Correlation Analysis
    "CorrelationAnalyzer",
    "CorrelationMatrix",
    "LeadLagRelation",
    "CausalLink",
    "IndicatorRelationship",
    # Trend Forecasting
    "TrendForecaster",
    "Trend",
    "Forecast",
    "SeasonalPattern",
    "TrendDirection",
]
