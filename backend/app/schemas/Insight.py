from datetime import datetime
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


class RecommendationSchema(BaseModel):
    title: str
    description: str
    priority: Literal["high", "medium", "low"] = "medium"
    action_type: Optional[str] = None
    estimated_effort: Optional[str] = None
    potential_impact: Optional[str] = None


class RelatedIndicatorSchema(BaseModel):
    indicator_name: str
    indicator_type: Literal["national", "operational"]
    contribution_weight: Optional[float] = None


class InsightResponse(BaseModel):
    id: str
    company_id: str
    type: str
    severity: str
    title: str
    description: str
    summary: Optional[str] = None
    impact_score: int
    probability: int
    risk_score: Optional[float] = None
    potential_value: Optional[float] = None
    feasibility: Optional[int] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    recommendations: List[RecommendationSchema] = Field(default_factory=list)
    time_horizon: Optional[str] = None
    active: bool
    acknowledged: bool
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InsightListItem(BaseModel):
    id: str
    company_id: str
    type: str
    severity: str
    title: str
    summary: Optional[str] = None
    impact_score: Optional[int] = None
    probability: Optional[int] = None
    category: Optional[str] = None
    active: Optional[bool] = True
    created_at: datetime

    class Config:
        from_attributes = True


class InsightListWithCompany(InsightListItem):
    company_name: str
    industry: str


class InsightsFilter(BaseModel):
    type: Optional[Literal["risk", "opportunity"]] = None
    severity: Optional[Literal["critical", "high", "medium", "low"]] = None
    category: Optional[str] = None
    active: Optional[bool] = True
    industry: Optional[str] = None  # For admin
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class InsightAcknowledge(BaseModel):
    notes: Optional[str] = None


class InsightsSummary(BaseModel):
    total_risks: int
    critical_risks: int
    high_risks: int
    total_opportunities: int
    high_value_opportunities: int
    recent_insights: List[InsightListItem]


class AdminInsightsSummary(BaseModel):
    total_companies: int
    companies_with_critical_risks: int
    total_risks: int
    total_opportunities: int
    risks_by_severity: Dict[str, int]
    risks_by_category: Dict[str, int]
    industries_at_risk: List[str]