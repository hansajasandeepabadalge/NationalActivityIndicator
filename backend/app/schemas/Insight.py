"""
Insight schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


class RecommendationSchema(BaseModel):
    """Schema for recommendation."""
    title: str
    description: str
    priority: Literal["high", "medium", "low"] = "medium"
    action_type: Optional[str] = None
    estimated_effort: Optional[str] = None
    potential_impact: Optional[str] = None


class RelatedIndicatorSchema(BaseModel):
    """Schema for related indicator."""
    indicator_name: str
    indicator_type: Literal["national", "operational"]
    contribution_weight: Optional[float] = None


class InsightResponse(BaseModel):
    """Schema for business insight response."""
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
    """Schema for insight list item."""
    id: str
    company_id: str
    type: str
    severity: str
    title: str
    summary: Optional[str] = None
    impact_score: int
    probability: int
    category: Optional[str] = None
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InsightListWithCompany(InsightListItem):
    """Schema for insight list item with company info (admin view)."""
    company_name: str
    industry: str


class InsightsFilter(BaseModel):
    """Schema for filtering insights."""
    type: Optional[Literal["risk", "opportunity"]] = None
    severity: Optional[Literal["critical", "high", "medium", "low"]] = None
    category: Optional[str] = None
    active: Optional[bool] = True
    industry: Optional[str] = None  # For admin
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class InsightAcknowledge(BaseModel):
    """Schema for acknowledging an insight."""
    notes: Optional[str] = None


class InsightsSummary(BaseModel):
    """Schema for insights summary."""
    total_risks: int
    critical_risks: int
    high_risks: int
    total_opportunities: int
    high_value_opportunities: int
    recent_insights: List[InsightListItem]


class AdminInsightsSummary(BaseModel):
    """Schema for admin insights summary."""
    total_companies: int
    companies_with_critical_risks: int
    total_risks: int
    total_opportunities: int
    risks_by_severity: Dict[str, int]
    risks_by_category: Dict[str, int]
    industries_at_risk: List[str]