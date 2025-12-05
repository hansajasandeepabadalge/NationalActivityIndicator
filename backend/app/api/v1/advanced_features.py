"""
API Endpoints for Advanced Features Module.

Provides REST API access to:
- ML Impact Prediction
- Portfolio Analysis
- Scenario Simulation
- Correlation Analysis
- Trend Forecasting
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from app.layer4.advanced import (
    MLImpactPredictor,
    PortfolioAnalyzer,
    ScenarioSimulator,
    CorrelationAnalyzer,
    TrendForecaster,
)
from app.layer4.advanced.scenario_simulator import ScenarioType
from app.layer4.advanced.trend_forecaster import SeasonalPeriod

router = APIRouter(prefix="/advanced", tags=["Advanced Features"])

# Initialize services (in production, use dependency injection)
ml_predictor = MLImpactPredictor()
portfolio_analyzer = PortfolioAnalyzer()
scenario_simulator = ScenarioSimulator()
correlation_analyzer = CorrelationAnalyzer()
trend_forecaster = TrendForecaster()


# ============================================================================
# Request/Response Models
# ============================================================================

# ML Impact Prediction Models
class PredictionRequest(BaseModel):
    """Request for ML impact prediction."""
    company_id: str
    indicators: Dict[str, float]
    historical_data: Optional[List[Dict[str, float]]] = None
    context: Optional[Dict[str, Any]] = None
    horizon_days: int = Field(default=7, ge=1, le=90)


class PredictionResponse(BaseModel):
    """Response from ML impact prediction."""
    prediction_id: str
    company_id: str
    predicted_impact: float
    impact_direction: str
    confidence_score: float
    confidence_level: str
    prediction_horizon_days: int
    top_features: List[Dict[str, Any]]
    explanation: str


class TrainingRequest(BaseModel):
    """Request for model training."""
    model_id: str
    training_data: List[Dict[str, Any]]
    validation_split: float = Field(default=0.2, ge=0.1, le=0.5)


# Portfolio Analysis Models
class PortfolioCreateRequest(BaseModel):
    """Request to create a portfolio."""
    portfolio_id: str
    name: str


class CompanyAddRequest(BaseModel):
    """Request to add company to portfolio."""
    company_id: str
    company_name: str
    sector: str
    region: str
    portfolio_weight: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_scores: Optional[Dict[str, float]] = None
    indicators: Optional[Dict[str, float]] = None


class PortfolioRiskResponse(BaseModel):
    """Response for portfolio risk."""
    portfolio_id: str
    overall_risk_score: float
    risk_level: str
    weighted_supply_risk: float
    weighted_operational_risk: float
    weighted_financial_risk: float
    weighted_market_risk: float
    top_risk_contributors: List[str]


class DiversificationResponse(BaseModel):
    """Response for diversification analysis."""
    overall_score: float
    sector_diversification: float
    regional_diversification: float
    size_diversification: float
    sector_concentration: Dict[str, float]
    regional_concentration: Dict[str, float]
    recommendations: List[str]


# Scenario Simulation Models
class ScenarioCreateRequest(BaseModel):
    """Request to create a scenario."""
    name: str
    description: str
    scenario_type: str
    affected_indicators: Dict[str, float]
    duration_days: int = Field(default=30, ge=1, le=365)
    probability: float = Field(default=0.5, ge=0.0, le=1.0)


class SimulationRequest(BaseModel):
    """Request to run a simulation."""
    scenario_id: str
    company_id: str
    baseline_indicators: Dict[str, float]
    simulation_days: Optional[int] = None


class SimulationResponse(BaseModel):
    """Response from simulation."""
    simulation_id: str
    scenario_id: str
    company_id: str
    overall_impact: float
    impact_direction: str
    severity: str
    peak_impact: float
    peak_day: int
    recovery_time_days: int
    indicator_changes: Dict[str, float]


class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo simulation."""
    scenario_id: str
    company_id: str
    baseline_indicators: Dict[str, float]
    num_simulations: int = Field(default=100, ge=10, le=1000)
    variance_factor: float = Field(default=0.1, ge=0.01, le=0.5)


# Correlation Analysis Models
class CorrelationDataRequest(BaseModel):
    """Request to add correlation data."""
    company_id: str
    timestamp: datetime
    indicators: Dict[str, float]


class CorrelationMatrixResponse(BaseModel):
    """Response for correlation matrix."""
    matrix_id: str
    indicators: List[str]
    correlations: Dict[str, Dict[str, float]]
    average_correlation: float
    sample_size: int


class LeadLagRequest(BaseModel):
    """Request for lead/lag detection."""
    company_id: str
    indicator_a: str
    indicator_b: str
    max_lag_days: int = Field(default=30, ge=1, le=90)


class RelationshipResponse(BaseModel):
    """Response for indicator relationship."""
    indicator_a: str
    indicator_b: str
    correlation: float
    correlation_type: str
    lead_lag_days: Optional[int]
    leading_indicator: Optional[str]
    causal_direction: Optional[str]
    relationship_strength: str
    relationship_summary: str


# Trend Forecasting Models
class TrendDataRequest(BaseModel):
    """Request to add trend data."""
    company_id: str
    indicator: str
    timestamp: datetime
    value: float


class TrendResponse(BaseModel):
    """Response for trend detection."""
    trend_id: str
    indicator: str
    direction: str
    trend_type: str
    slope: float
    r_squared: float
    is_significant: bool
    confidence: float
    volatility: float


class ForecastRequest(BaseModel):
    """Request for forecast generation."""
    company_id: str
    indicator: str
    horizon_days: int = Field(default=30, ge=1, le=90)
    include_seasonality: bool = True
    confidence_level: float = Field(default=0.95, ge=0.8, le=0.99)


class ForecastResponse(BaseModel):
    """Response for forecast."""
    forecast_id: str
    indicator: str
    horizon_days: int
    expected_change: float
    change_direction: str
    mape: float
    forecasted_values: List[Dict[str, Any]]


# ============================================================================
# ML Impact Prediction Endpoints
# ============================================================================

@router.post("/ml/predict", response_model=PredictionResponse)
async def predict_impact(request: PredictionRequest):
    """
    Generate ML-based impact prediction.
    
    Uses ensemble methods to predict business impacts from operational
    indicators with confidence scoring.
    """
    try:
        features = ml_predictor.extract_features(
            request.company_id,
            request.indicators,
            request.historical_data,
            request.context,
        )
        
        prediction = ml_predictor.predict_impact(
            features,
            horizon_days=request.horizon_days,
        )
        
        return PredictionResponse(
            prediction_id=prediction.prediction_id,
            company_id=prediction.company_id,
            predicted_impact=prediction.predicted_impact,
            impact_direction=prediction.impact_direction,
            confidence_score=prediction.confidence_score,
            confidence_level=prediction.confidence_level.value,
            prediction_horizon_days=prediction.prediction_horizon_days,
            top_features=[
                {"feature": f[0], "contribution": f[1]}
                for f in prediction.top_features
            ],
            explanation=prediction.explanation,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ml/predictions/{company_id}")
async def get_predictions(
    company_id: str,
    limit: int = Query(default=10, ge=1, le=100),
):
    """Get recent predictions for a company."""
    predictions = ml_predictor.get_predictions_for_company(company_id, limit)
    return {
        "company_id": company_id,
        "count": len(predictions),
        "predictions": [
            {
                "prediction_id": p.prediction_id,
                "predicted_impact": p.predicted_impact,
                "impact_direction": p.impact_direction,
                "confidence_level": p.confidence_level.value,
                "timestamp": p.timestamp.isoformat(),
            }
            for p in predictions
        ],
    }


@router.get("/ml/feature-importance")
async def get_feature_importance(model_id: str = "default"):
    """Get feature importance for a model."""
    importance = ml_predictor.get_feature_importance(model_id)
    return {
        "model_id": model_id,
        "feature_importance": importance,
    }


@router.get("/ml/models")
async def list_models():
    """List all available ML models."""
    models = ml_predictor.list_models()
    return {"models": models}


# ============================================================================
# Portfolio Analysis Endpoints
# ============================================================================

@router.post("/portfolio/create")
async def create_portfolio(request: PortfolioCreateRequest):
    """Create a new portfolio."""
    try:
        portfolio = portfolio_analyzer.create_portfolio(
            request.portfolio_id,
            request.name,
        )
        return {
            "portfolio_id": portfolio.portfolio_id,
            "name": portfolio.name,
            "created_at": portfolio.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/portfolio/{portfolio_id}/companies")
async def add_company(portfolio_id: str, request: CompanyAddRequest):
    """Add a company to a portfolio."""
    try:
        profile = portfolio_analyzer.add_company(
            portfolio_id,
            request.company_id,
            request.company_name,
            request.sector,
            request.region,
            request.portfolio_weight,
            request.risk_scores,
            request.indicators,
        )
        return {
            "company_id": profile.company_id,
            "company_name": profile.company_name,
            "sector": profile.sector,
            "region": profile.region,
            "portfolio_weight": profile.portfolio_weight,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/portfolio/{portfolio_id}/risk", response_model=PortfolioRiskResponse)
async def get_portfolio_risk(portfolio_id: str):
    """Calculate portfolio risk."""
    try:
        risk = portfolio_analyzer.calculate_portfolio_risk(portfolio_id)
        return PortfolioRiskResponse(
            portfolio_id=risk.portfolio_id,
            overall_risk_score=risk.overall_risk_score,
            risk_level=risk.risk_level.value,
            weighted_supply_risk=risk.weighted_supply_risk,
            weighted_operational_risk=risk.weighted_operational_risk,
            weighted_financial_risk=risk.weighted_financial_risk,
            weighted_market_risk=risk.weighted_market_risk,
            top_risk_contributors=risk.top_risk_contributors,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/portfolio/{portfolio_id}/diversification", response_model=DiversificationResponse)
async def get_diversification(portfolio_id: str):
    """Analyze portfolio diversification."""
    try:
        div = portfolio_analyzer.analyze_diversification(portfolio_id)
        return DiversificationResponse(
            overall_score=div.overall_score,
            sector_diversification=div.sector_diversification,
            regional_diversification=div.regional_diversification,
            size_diversification=div.size_diversification,
            sector_concentration=div.sector_concentration,
            regional_concentration=div.regional_concentration,
            recommendations=div.recommendations,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/portfolio/{portfolio_id}/alerts")
async def get_concentration_alerts(portfolio_id: str):
    """Get concentration risk alerts for a portfolio."""
    try:
        alerts = portfolio_analyzer.check_concentration_alerts(portfolio_id)
        return {
            "portfolio_id": portfolio_id,
            "alert_count": len(alerts),
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "alert_type": a.alert_type,
                    "severity": a.severity.value,
                    "concentrated_element": a.concentrated_element,
                    "concentration_percentage": a.concentration_percentage,
                    "recommendation": a.recommendation,
                }
                for a in alerts
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/portfolio/{portfolio_id}/stress-test")
async def run_stress_test(
    portfolio_id: str,
    scenario: str = Query(default="market_crash"),
):
    """Run stress test on portfolio."""
    try:
        results = portfolio_analyzer.get_stress_test_results(portfolio_id, scenario)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/portfolio")
async def list_portfolios():
    """List all portfolios."""
    portfolios = portfolio_analyzer.list_portfolios()
    return {"portfolios": portfolios}


# ============================================================================
# Scenario Simulation Endpoints
# ============================================================================

@router.post("/scenario/create")
async def create_scenario(request: ScenarioCreateRequest):
    """Create a new scenario."""
    try:
        scenario_type = ScenarioType(request.scenario_type)
    except ValueError:
        scenario_type = ScenarioType.CUSTOM
    
    scenario = scenario_simulator.create_scenario(
        name=request.name,
        description=request.description,
        scenario_type=scenario_type,
        affected_indicators=request.affected_indicators,
        duration_days=request.duration_days,
        probability=request.probability,
    )
    
    return {
        "scenario_id": scenario.scenario_id,
        "name": scenario.name,
        "scenario_type": scenario.scenario_type.value,
        "duration_days": scenario.duration_days,
    }


@router.post("/scenario/preset/{preset}")
async def create_preset_scenario(
    preset: str,
    severity: str = Query(default="moderate"),
):
    """Create a preset scenario."""
    try:
        scenario = scenario_simulator.create_preset_scenario(preset, severity)
        return {
            "scenario_id": scenario.scenario_id,
            "name": scenario.name,
            "scenario_type": scenario.scenario_type.value,
            "affected_indicators": scenario.affected_indicators,
            "duration_days": scenario.duration_days,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/scenario/simulate", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """Run a scenario simulation."""
    try:
        result = scenario_simulator.run_simulation(
            request.scenario_id,
            request.company_id,
            request.baseline_indicators,
            request.simulation_days,
        )
        
        return SimulationResponse(
            simulation_id=result.simulation_id,
            scenario_id=result.scenario_id,
            company_id=result.company_id,
            overall_impact=result.overall_impact,
            impact_direction=result.impact_direction,
            severity=result.severity,
            peak_impact=result.peak_impact,
            peak_day=result.peak_day,
            recovery_time_days=result.recovery_time_days,
            indicator_changes=result.indicator_changes,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/scenario/monte-carlo")
async def run_monte_carlo(request: MonteCarloRequest):
    """Run Monte Carlo simulation."""
    try:
        results = scenario_simulator.run_monte_carlo(
            request.scenario_id,
            request.company_id,
            request.baseline_indicators,
            request.num_simulations,
            request.variance_factor,
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/scenario/sensitivity")
async def run_sensitivity_analysis(request: SimulationRequest):
    """Run sensitivity analysis on a scenario."""
    try:
        analysis = scenario_simulator.run_sensitivity_analysis(
            request.scenario_id,
            request.company_id,
            request.baseline_indicators,
        )
        return {
            "analysis_id": analysis.analysis_id,
            "scenario_id": analysis.scenario_id,
            "parameter_sensitivities": analysis.parameter_sensitivities,
            "top_sensitive_params": analysis.top_sensitive_params,
            "elasticities": analysis.elasticities,
            "critical_thresholds": analysis.critical_thresholds,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/scenario/compare")
async def compare_scenarios(
    scenario_ids: List[str],
    company_id: str,
    baseline_indicators: Dict[str, float],
):
    """Compare multiple scenarios."""
    comparison = scenario_simulator.compare_scenarios(
        scenario_ids,
        company_id,
        baseline_indicators,
    )
    return comparison


@router.get("/scenario")
async def list_scenarios():
    """List all scenarios."""
    scenarios = scenario_simulator.list_scenarios()
    return {
        "scenarios": [
            {
                "scenario_id": s.scenario_id,
                "name": s.name,
                "scenario_type": s.scenario_type.value,
                "duration_days": s.duration_days,
            }
            for s in scenarios
        ]
    }


# ============================================================================
# Correlation Analysis Endpoints
# ============================================================================

@router.post("/correlation/data")
async def add_correlation_data(request: CorrelationDataRequest):
    """Add data point for correlation analysis."""
    correlation_analyzer.add_data_point(
        request.company_id,
        request.timestamp,
        request.indicators,
    )
    return {"status": "success", "company_id": request.company_id}


@router.post("/correlation/data/batch")
async def add_correlation_data_batch(
    company_id: str,
    data: List[Dict[str, Any]],
):
    """Add batch data for correlation analysis."""
    for point in data:
        timestamp = datetime.fromisoformat(point["timestamp"])
        correlation_analyzer.add_data_point(
            company_id,
            timestamp,
            point["indicators"],
        )
    return {"status": "success", "points_added": len(data)}


@router.get("/correlation/{company_id}/matrix", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix(
    company_id: str,
    indicators: Optional[str] = Query(default=None),
):
    """Calculate correlation matrix."""
    try:
        indicator_list = indicators.split(",") if indicators else None
        matrix = correlation_analyzer.calculate_correlation_matrix(
            company_id, indicator_list
        )
        
        return CorrelationMatrixResponse(
            matrix_id=matrix.matrix_id,
            indicators=matrix.indicators,
            correlations=matrix.correlations,
            average_correlation=matrix.average_correlation,
            sample_size=matrix.sample_size,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/correlation/lead-lag")
async def detect_lead_lag(request: LeadLagRequest):
    """Detect lead/lag relationship between indicators."""
    try:
        relation = correlation_analyzer.detect_lead_lag(
            request.company_id,
            request.indicator_a,
            request.indicator_b,
            request.max_lag_days,
        )
        
        return {
            "leading_indicator": relation.leading_indicator,
            "lagging_indicator": relation.lagging_indicator,
            "lag_days": relation.lag_days,
            "correlation_at_lag": relation.correlation_at_lag,
            "correlation_type": relation.correlation_type.value,
            "predictive_power": relation.predictive_power,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/correlation/{company_id}/relationship", response_model=RelationshipResponse)
async def analyze_relationship(
    company_id: str,
    indicator_a: str,
    indicator_b: str,
):
    """Analyze comprehensive relationship between two indicators."""
    try:
        relationship = correlation_analyzer.analyze_relationship(
            company_id, indicator_a, indicator_b
        )
        
        return RelationshipResponse(
            indicator_a=relationship.indicator_a,
            indicator_b=relationship.indicator_b,
            correlation=relationship.correlation.correlation,
            correlation_type=relationship.correlation.correlation_type.value,
            lead_lag_days=relationship.lead_lag.lag_days if relationship.lead_lag else None,
            leading_indicator=relationship.lead_lag.leading_indicator if relationship.lead_lag else None,
            causal_direction=relationship.causal_link.direction.value if relationship.causal_link else None,
            relationship_strength=relationship.relationship_strength,
            relationship_summary=relationship.relationship_summary,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/correlation/{company_id}/clusters")
async def cluster_indicators(
    company_id: str,
    num_clusters: int = Query(default=3, ge=2, le=10),
):
    """Cluster indicators based on correlation patterns."""
    try:
        clusters = correlation_analyzer.cluster_indicators(company_id, num_clusters)
        return {
            "company_id": company_id,
            "clusters": [
                {
                    "cluster_id": c.cluster_id,
                    "name": c.name,
                    "indicators": c.indicators,
                    "average_internal_correlation": c.average_internal_correlation,
                    "centroid_indicator": c.centroid_indicator,
                }
                for c in clusters
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/correlation/{company_id}/top")
async def get_top_correlations(
    company_id: str,
    n: int = Query(default=10, ge=1, le=50),
    positive_only: bool = False,
):
    """Get top N correlations."""
    try:
        pairs = correlation_analyzer.get_top_correlations(company_id, n, positive_only)
        return {
            "company_id": company_id,
            "correlations": [
                {
                    "indicator_a": p.indicator_a,
                    "indicator_b": p.indicator_b,
                    "correlation": p.correlation,
                    "correlation_type": p.correlation_type.value,
                }
                for p in pairs
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Trend Forecasting Endpoints
# ============================================================================

@router.post("/trend/data")
async def add_trend_data(request: TrendDataRequest):
    """Add data point for trend analysis."""
    trend_forecaster.add_data_point(
        request.company_id,
        request.indicator,
        request.timestamp,
        request.value,
    )
    return {"status": "success"}


@router.post("/trend/data/batch")
async def add_trend_data_batch(
    company_id: str,
    indicator: str,
    data: List[Dict[str, Any]],
):
    """Add batch data for trend analysis."""
    for point in data:
        timestamp = datetime.fromisoformat(point["timestamp"])
        trend_forecaster.add_data_point(
            company_id, indicator, timestamp, point["value"]
        )
    return {"status": "success", "points_added": len(data)}


@router.get("/trend/{company_id}/{indicator}", response_model=TrendResponse)
async def detect_trend(
    company_id: str,
    indicator: str,
    lookback_days: Optional[int] = None,
):
    """Detect trend in indicator time series."""
    try:
        trend = trend_forecaster.detect_trend(company_id, indicator, lookback_days)
        
        return TrendResponse(
            trend_id=trend.trend_id,
            indicator=trend.indicator,
            direction=trend.direction.value,
            trend_type=trend.trend_type.value,
            slope=trend.slope,
            r_squared=trend.r_squared,
            is_significant=trend.is_significant,
            confidence=trend.confidence,
            volatility=trend.volatility,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trend/{company_id}/{indicator}/seasonality")
async def detect_seasonality(
    company_id: str,
    indicator: str,
    period: str = Query(default="weekly"),
):
    """Detect seasonal pattern in indicator."""
    period_map = {
        "weekly": SeasonalPeriod.WEEKLY,
        "monthly": SeasonalPeriod.MONTHLY,
        "quarterly": SeasonalPeriod.QUARTERLY,
        "yearly": SeasonalPeriod.YEARLY,
    }
    
    try:
        seasonal_period = period_map.get(period, SeasonalPeriod.WEEKLY)
        pattern = trend_forecaster.detect_seasonality(
            company_id, indicator, seasonal_period
        )
        
        return {
            "pattern_id": pattern.pattern_id,
            "indicator": pattern.indicator,
            "period": pattern.period.name,
            "period_days": pattern.period_days,
            "strength": pattern.strength,
            "peak_index": pattern.peak_index,
            "peak_factor": pattern.peak_factor,
            "trough_index": pattern.trough_index,
            "trough_factor": pattern.trough_factor,
            "seasonal_factors": pattern.seasonal_factors,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/trend/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    """Generate forecast for an indicator."""
    try:
        forecast = trend_forecaster.generate_forecast(
            request.company_id,
            request.indicator,
            request.horizon_days,
            request.include_seasonality,
            request.confidence_level,
        )
        
        return ForecastResponse(
            forecast_id=forecast.forecast_id,
            indicator=forecast.indicator,
            horizon_days=forecast.horizon_days,
            expected_change=forecast.expected_change,
            change_direction=forecast.change_direction,
            mape=forecast.mape,
            forecasted_values=[
                {
                    "date": fv.date.isoformat(),
                    "predicted_value": fv.predicted_value,
                    "lower_bound": fv.lower_bound,
                    "upper_bound": fv.upper_bound,
                }
                for fv in forecast.forecasted_values
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trend/{company_id}/{indicator}/anomalies")
async def detect_anomalies(
    company_id: str,
    indicator: str,
    sensitivity: float = Query(default=2.0, ge=1.0, le=4.0),
):
    """Detect anomalies in indicator time series."""
    try:
        anomalies = trend_forecaster.detect_anomalies(
            company_id, indicator, sensitivity
        )
        
        return {
            "company_id": company_id,
            "indicator": indicator,
            "anomaly_count": len(anomalies),
            "anomalies": [
                {
                    "anomaly_id": a.anomaly_id,
                    "detected_at": a.detected_at.isoformat(),
                    "anomaly_type": a.anomaly_type,
                    "severity": a.severity,
                    "expected_value": a.expected_value,
                    "actual_value": a.actual_value,
                    "deviation": a.deviation,
                    "explanation": a.explanation,
                }
                for a in anomalies
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trend/{company_id}/compare")
async def compare_trends(
    company_id: str,
    indicators: str,
):
    """Compare trends across multiple indicators."""
    indicator_list = indicators.split(",")
    comparison = trend_forecaster.compare_trends(company_id, indicator_list)
    return comparison


@router.get("/trend/{company_id}/summary")
async def get_trend_data_summary(company_id: str):
    """Get summary of available trend data."""
    summary = trend_forecaster.get_data_summary(company_id)
    return summary
