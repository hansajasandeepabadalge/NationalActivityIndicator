"""Pydantic response schemas for API endpoints"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class IndicatorBasic(BaseModel):
    """Basic indicator info"""
    indicator_id: str
    name: str
    category: str  # "ECO", "POL", "SOC"
    description: str


class IndicatorDetail(IndicatorBasic):
    """Detailed indicator with latest value"""
    latest_value: Optional[float] = None
    latest_confidence: Optional[float] = None
    last_updated: Optional[datetime] = None
    narrative: Optional[str] = None


class IndicatorHistory(BaseModel):
    """Time series data point"""
    date: datetime
    value: float
    confidence: float


class IndicatorHistoryResponse(BaseModel):
    """Historical data for an indicator"""
    indicator_id: str
    time_series: List[IndicatorHistory]
    period_start: datetime
    period_end: datetime


class TrendInfo(BaseModel):
    """Trend detection result"""
    indicator_id: str
    trend: str  # "rising", "falling", "stable"
    strength: float
    change_percent: float
    forecast_7d: Optional[float] = None


class AnomalyInfo(BaseModel):
    """Anomaly detection result"""
    indicator_id: str
    date: datetime
    value: float
    expected_range: tuple[float, float]
    severity: str  # "low", "medium", "high"


class AlertInfo(BaseModel):
    """Alert for significant changes"""
    indicator_id: str
    alert_type: str  # "spike", "drop", "threshold"
    message: str
    triggered_at: datetime
    severity: str


class CompositeMetric(BaseModel):
    """Composite indicator calculation"""
    metric_id: str
    name: str
    value: float
    components: Dict[str, float]
    last_updated: datetime
