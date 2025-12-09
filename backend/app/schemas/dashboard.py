from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.Indicator import (
    NationalIndicatorResponse,
    OperationalIndicatorResponse
)
from app.schemas.Insight import InsightListItem


class UserDashboardHome(BaseModel):
    health_score: float
    health_trend: str
    health_trend_change: Optional[float] = None
    indicators: List[OperationalIndicatorResponse]
    recent_insights: List[InsightListItem]
    alert_count: int
    critical_risks: int
    high_opportunities: int
    company_name: str
    last_updated: datetime


class AdminDashboardHome(BaseModel):
    total_companies: int
    companies_at_risk: int
    avg_health_score: float
    national_indicators_summary: Dict[str, Any]
    critical_alerts_count: int
    recent_critical_insights: List[InsightListItem]
    industries_overview: List[Dict[str, Any]]
    system_health: Dict[str, Any]


class AlertItem(BaseModel):
    id: str
    type: str
    severity: str
    title: str
    created_at: datetime
    source: str  # "insight" or "indicator"


class UserAlertsResponse(BaseModel):
    alerts: List[AlertItem]
    unread_count: int
    total_count: int


class DashboardStats(BaseModel):
    total_indicators: int
    indicators_improving: int
    indicators_declining: int
    total_insights: int
    active_risks: int
    active_opportunities: int


class ReportRequest(BaseModel):
    report_type: str  # "summary", "detailed", "risks", "opportunities"
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    include_charts: bool = True
    format: str = "pdf"  # "pdf", "excel", "json"


class ReportResponse(BaseModel):
    report_id: str
    status: str  # "generating", "ready", "failed"
    download_url: Optional[str] = None
    generated_at: Optional[datetime] = None