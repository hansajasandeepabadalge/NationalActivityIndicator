from datetime import datetime
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


class IndicatorHistoryPoint(BaseModel):
    value: float
    recorded_at: datetime


class NationalIndicatorResponse(BaseModel):
    id: str
    indicator_name: str
    category: str
    value: float
    trend: str
    trend_change: Optional[float] = None
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    status: str  # good, warning, critical
    status_color: str
    calculated_at: datetime

    class Config:
        from_attributes = True


class NationalIndicatorWithHistory(NationalIndicatorResponse):
    history: List[IndicatorHistoryPoint] = Field(default_factory=list)


class NationalIndicatorsGrouped(BaseModel):
    political: List[NationalIndicatorResponse]
    economic: List[NationalIndicatorResponse]
    social: List[NationalIndicatorResponse]
    infrastructure: List[NationalIndicatorResponse]


class OperationalIndicatorResponse(BaseModel):
    id: str
    company_id: str
    indicator_name: str
    value: float
    trend: str
    trend_change: Optional[float] = None
    display_name: Optional[str] = None
    status: str
    contributing_factors: List[str] = Field(default_factory=list)
    calculated_at: datetime

    class Config:
        from_attributes = True


class OperationalIndicatorWithHistory(OperationalIndicatorResponse):
    history: List[IndicatorHistoryPoint] = Field(default_factory=list)


class IndicatorHistoryRequest(BaseModel):
    indicator_name: str
    days: int = Field(default=30, ge=1, le=365)


class IndicatorHistoryResponse(BaseModel):
    indicator_name: str
    data_points: List[IndicatorHistoryPoint]


class HealthScoreResponse(BaseModel):
    health_score: float
    trend: str
    trend_change: Optional[float] = None
    indicators: List[OperationalIndicatorResponse]
    last_updated: datetime


class IndustryIndicatorSummary(BaseModel):
    industry: str
    company_count: int
    avg_indicators: Dict[str, float]
    indicator_distribution: Dict[str, Dict[str, int]]  # indicator -> {good, warning, critical}