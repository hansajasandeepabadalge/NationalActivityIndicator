"""
Layer 4: Business Insight Pydantic Schemas (Unified risks and opportunities)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class BusinessInsightBase(BaseModel):
    """Base schema for business insight"""
    company_id: str = Field(..., max_length=50)
    insight_type: str = Field(..., description="risk or opportunity")
    category: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    description: str

    probability: Optional[Decimal] = Field(None, ge=0, le=1)
    impact: Optional[Decimal] = Field(None, ge=0, le=10)
    urgency: Optional[int] = Field(None, ge=1, le=5)
    confidence: Decimal = Field(..., ge=0, le=1)

    final_score: Decimal
    severity_level: str

    triggering_indicators: Dict[str, Any]
    affected_operations: Optional[List[str]] = None

    expected_impact_time: Optional[datetime] = None
    expected_duration_hours: Optional[int] = None


class BusinessInsightCreate(BusinessInsightBase):
    """Schema for creating a business insight"""
    definition_id: Optional[int] = None
    status: str = "active"
    priority_rank: Optional[int] = None
    is_urgent: bool = False
    requires_immediate_action: bool = False


class BusinessInsightUpdate(BaseModel):
    """Schema for updating a business insight"""
    status: Optional[str] = None
    priority_rank: Optional[int] = None
    resolution_notes: Optional[str] = None
    actual_impact: Optional[str] = None
    actual_outcome: Optional[str] = None


class BusinessInsight(BusinessInsightBase):
    """Complete business insight schema"""
    insight_id: int
    definition_id: Optional[int] = None

    detected_at: datetime
    status: str
    priority_rank: Optional[int] = None
    is_urgent: bool
    requires_immediate_action: bool

    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    actual_impact: Optional[str] = None
    actual_outcome: Optional[str] = None
    lessons_learned: Optional[str] = None

    related_insights: Optional[List[int]] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightPriority(BaseModel):
    """Prioritized insight for action"""
    insight_id: int
    company_id: str
    insight_type: str
    title: str
    category: str

    final_score: Decimal
    severity_level: str
    priority_rank: int

    is_urgent: bool
    requires_immediate_action: bool

    actionability_score: Decimal = Field(..., description="How actionable (0-1)")
    strategic_importance: Decimal = Field(..., description="Strategic value (0-1)")
    priority_score: Decimal = Field(..., description="Combined priority metric")

    detected_at: datetime
    status: str


class TopPriorities(BaseModel):
    """Top 5 priority insights for a company"""
    company_id: str
    as_of: datetime
    total_active_insights: int
    total_risks: int
    total_opportunities: int

    priorities: List[InsightPriority] = Field(..., max_length=5)


class InsightFeedbackCreate(BaseModel):
    """Schema for creating insight feedback"""
    insight_id: int
    company_id: str
    feedback_type: str = Field(..., description="accuracy, relevance, usefulness, outcome")

    accuracy_rating: Optional[int] = Field(None, ge=1, le=5)
    relevance_rating: Optional[int] = Field(None, ge=1, le=5)
    usefulness_rating: Optional[int] = Field(None, ge=1, le=5)
    timeliness_rating: Optional[int] = Field(None, ge=1, le=5)

    comments: Optional[str] = None

    did_risk_materialize: Optional[bool] = None
    did_opportunity_exist: Optional[bool] = None
    was_action_taken: Optional[bool] = None
    action_effectiveness: Optional[str] = None

    actual_business_impact: Optional[str] = None
    financial_impact_estimate: Optional[Decimal] = None

    what_was_wrong: Optional[str] = None
    what_was_missing: Optional[str] = None
    suggestions: Optional[str] = None

    provided_by: str


class InsightFeedback(InsightFeedbackCreate):
    """Complete insight feedback schema"""
    feedback_id: int
    provided_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightTrackingSnapshot(BaseModel):
    """Daily tracking snapshot"""
    time: datetime
    company_id: str

    total_active_risks: int
    total_active_opportunities: int

    critical_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int

    operational_risks: int
    financial_risks: int
    competitive_risks: int
    reputational_risks: int
    compliance_risks: int
    strategic_risks: int

    market_opportunities: int
    cost_opportunities: int
    strategic_opportunities: int

    recommendations_generated: int
    actions_taken: int
    actions_completed: int

    risks_materialized: int
    risks_avoided: int
    opportunities_captured: int
    opportunities_missed: int

    model_config = ConfigDict(from_attributes=True)


class InsightScoreUpdate(BaseModel):
    """Update to insight score over time"""
    time: datetime
    insight_id: int

    probability: Optional[Decimal] = None
    impact: Optional[Decimal] = None
    urgency: Optional[int] = None
    confidence: Decimal

    final_score: Decimal
    severity_level: str

    triggering_indicators: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class CompetitiveIntelligenceCreate(BaseModel):
    """Schema for creating competitive intelligence"""
    company_id: str
    competitor_name: Optional[str] = None
    competitor_industry: Optional[str] = None

    intel_type: str = Field(..., description="weakness, strength, movement, vulnerability")
    description: str
    source: Optional[str] = None
    confidence_level: Decimal = Field(..., ge=0, le=1)

    relevance_score: Decimal = Field(..., ge=0, le=1)
    potential_opportunity: Optional[str] = None
    suggested_response: Optional[str] = None

    detected_at: datetime
    expires_at: Optional[datetime] = None


class CompetitiveIntelligence(CompetitiveIntelligenceCreate):
    """Complete competitive intelligence schema"""
    intel_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
