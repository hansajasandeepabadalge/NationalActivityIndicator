"""
Layer 5: Dashboard Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InsightType(str, Enum):
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    RECOMMENDATION = "recommendation"


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


# ============== National Indicators (Layer 2) ==============

class NationalIndicatorResponse(BaseModel):
    """Schema for national indicator data"""
    indicator_id: str
    indicator_name: str
    pestel_category: str
    description: Optional[str] = None
    
    # Latest value
    current_value: Optional[float] = None
    previous_value: Optional[float] = None
    change_percentage: Optional[float] = None
    trend: Optional[TrendDirection] = None
    
    # Thresholds
    threshold_high: Optional[float] = None
    threshold_low: Optional[float] = None
    status: Optional[str] = None  # 'normal', 'warning', 'critical'
    
    # Metadata
    last_updated: Optional[datetime] = None
    confidence: Optional[float] = None
    source_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class NationalIndicatorListResponse(BaseModel):
    """Schema for list of national indicators"""
    indicators: List[NationalIndicatorResponse]
    total: int
    by_category: Dict[str, int]  # Count by PESTEL category


# ============== Operational Indicators (Layer 3) ==============

class OperationalIndicatorResponse(BaseModel):
    """Schema for company-specific operational indicator"""
    indicator_id: str
    indicator_name: str
    category: str
    
    # Values
    current_value: Optional[float] = None
    baseline_value: Optional[float] = None
    deviation: Optional[float] = None
    
    # Impact
    impact_score: Optional[float] = None
    trend: Optional[TrendDirection] = None
    
    # Thresholds
    is_above_threshold: bool = False
    is_below_threshold: bool = False
    
    # Context
    company_id: str
    calculated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OperationalIndicatorListResponse(BaseModel):
    """Schema for list of operational indicators"""
    company_id: str
    indicators: List[OperationalIndicatorResponse]
    total: int
    critical_count: int
    warning_count: int


# ============== Business Insights (Layer 4) ==============

class BusinessInsightResponse(BaseModel):
    """Schema for business insight (risk or opportunity)"""
    insight_id: int
    company_id: str
    
    # Type and classification
    insight_type: InsightType
    category: str
    
    # Content
    title: str
    description: Optional[str] = None
    
    # Scoring
    probability: Optional[float] = None
    impact: Optional[float] = None
    urgency: Optional[int] = None
    final_score: Optional[float] = None
    severity_level: Optional[SeverityLevel] = None
    confidence: Optional[float] = None
    
    # Temporal
    detected_at: datetime
    expected_impact_time: Optional[datetime] = None
    expected_duration_hours: Optional[int] = None
    
    # Status
    status: str = "active"
    is_urgent: bool = False
    requires_immediate_action: bool = False
    
    # Priority
    priority_rank: Optional[int] = None
    
    # Related data
    triggering_indicators: Optional[Dict[str, Any]] = None
    affected_operations: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class BusinessInsightListResponse(BaseModel):
    """Schema for list of business insights"""
    insights: List[BusinessInsightResponse]
    total: int
    risks_count: int
    opportunities_count: int
    critical_count: int
    by_category: Dict[str, int]


# ============== Dashboard Home ==============

class HealthScore(BaseModel):
    """Company health score summary"""
    overall_score: float = Field(..., ge=0, le=100)
    trend: TrendDirection
    components: Dict[str, float]  # e.g., {"financial": 75, "operational": 80}
    last_calculated: datetime


class RiskSummary(BaseModel):
    """Summary of risks for dashboard"""
    total_active: int
    critical: int
    high: int
    medium: int
    low: int
    recent_risks: List[BusinessInsightResponse]  # Last 5
    trend: TrendDirection  # Compared to last period


class OpportunitySummary(BaseModel):
    """Summary of opportunities for dashboard"""
    total_active: int
    high_potential: int
    medium_potential: int
    low_potential: int
    recent_opportunities: List[BusinessInsightResponse]  # Last 5
    trend: TrendDirection


class DashboardHomeResponse(BaseModel):
    """Complete dashboard home response for a user"""
    company_id: str
    company_name: str
    
    # Health overview
    health_score: HealthScore
    
    # Summaries
    risk_summary: RiskSummary
    opportunity_summary: OpportunitySummary
    
    # Key indicators (top 5 most impactful)
    key_indicators: List[OperationalIndicatorResponse]
    
    # Recent activity
    last_updated: datetime


# ============== Recommendations ==============

class RecommendationResponse(BaseModel):
    """Schema for recommendation data"""
    recommendation_id: int
    insight_id: Optional[int] = None
    category: Optional[str] = None  # 'immediate', 'short_term', 'medium_term'
    priority: int
    action_title: str
    action_description: Optional[str] = None
    responsible_role: Optional[str] = None
    estimated_effort: Optional[str] = None
    estimated_timeframe: Optional[str] = None
    expected_benefit: Optional[str] = None
    success_metrics: Optional[List[str]] = None
    status: Optional[str] = None  # 'pending', 'in_progress', 'completed'
    
    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Schema for list of recommendations"""
    recommendations: List[RecommendationResponse]
    total: int
    by_priority: Dict[str, int]


# ============== Admin Dashboard ==============

class IndustryIndicatorResponse(BaseModel):
    """Indicator aggregated by industry"""
    indicator_id: str
    indicator_name: str
    industry: str
    
    # Aggregated values
    average_value: float
    min_value: float
    max_value: float
    company_count: int
    
    # Insights
    companies_at_risk: int
    companies_with_opportunity: int


class IndustryOverviewResponse(BaseModel):
    """Industry-level overview for admin"""
    industry: str
    company_count: int
    
    # Aggregated health
    average_health_score: float
    
    # Risk/Opportunity summary
    total_active_risks: int
    total_active_opportunities: int
    critical_risks: int
    
    # Top indicators
    top_risk_indicators: List[str]
    top_opportunity_indicators: List[str]


class AdminDashboardResponse(BaseModel):
    """Admin dashboard overview"""
    total_companies: int
    total_active_users: int
    total_indicators: int = 0  # Layer 2 indicators count
    total_insights: int = 0  # Total business insights
    
    # System health
    total_active_risks: int
    total_active_opportunities: int
    critical_alerts: int
    
    # By industry
    industries: List[IndustryOverviewResponse]
    
    # Recent activity
    last_updated: datetime
