"""
Layer 4: Opportunity Detection Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class OpportunityDefinitionBase(BaseModel):
    """Base schema for opportunity definition"""
    code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    type: str = Field("opportunity", description="Type: risk or opportunity")
    category: str = Field(..., max_length=50)
    # For opportunities: 'market', 'cost', 'strategic', 'talent', 'financial', 'innovation'
    subcategory: Optional[str] = Field(None, max_length=100)
    trigger_logic: Dict[str, Any]
    applicable_industries: Optional[List[str]] = None
    applicable_business_scales: Optional[List[str]] = None
    description_template: Optional[str] = None
    is_active: bool = True


class OpportunityDefinitionCreate(OpportunityDefinitionBase):
    """Schema for creating an opportunity definition"""
    pass


class OpportunityDefinition(OpportunityDefinitionBase):
    """Complete opportunity definition schema"""
    definition_id: int
    created_at: datetime
    updated_at: datetime
    version: int

    model_config = ConfigDict(from_attributes=True)


class DetectedOpportunity(BaseModel):
    """Schema for a detected opportunity (before storage)"""
    definition_id: Optional[int] = None
    opportunity_code: str
    company_id: str
    title: str
    description: str
    category: str

    # Scoring
    potential_value: Decimal = Field(..., ge=0, le=10, description="Potential value (0-10)")
    feasibility: Decimal = Field(..., ge=0, le=1, description="Feasibility (0-1)")
    timing_score: Decimal = Field(..., ge=0, le=1, description="Timing favorability (0-1)")
    strategic_fit: Decimal = Field(..., ge=0, le=1, description="Strategic alignment (0-1)")

    final_score: Decimal = Field(..., description="Final opportunity score (0-10)")
    priority_level: str = Field(..., description="high, medium, low")

    # Context
    triggering_indicators: Dict[str, Any]
    detection_method: str = Field(..., description="gap_analysis, trend_spotting, event_triggered")
    reasoning: Optional[str] = Field(None, description="Why is this an opportunity?")

    # Temporal
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    window_duration_days: Optional[int] = None

    # Feasibility factors
    required_resources: Optional[Dict[str, Any]] = None
    constraints: Optional[List[str]] = None


class OpportunityScoreBreakdown(BaseModel):
    """Detailed breakdown of opportunity score calculation"""
    potential_value: Decimal
    value_reasoning: str

    feasibility: Decimal
    feasibility_reasoning: str

    timing_score: Decimal
    timing_reasoning: str

    strategic_fit: Decimal
    fit_reasoning: str

    final_score: Decimal
    priority: str


class OpportunityWithScore(BaseModel):
    """Opportunity with detailed scoring information"""
    insight_id: int
    company_id: str
    title: str
    description: str
    category: str

    score_breakdown: OpportunityScoreBreakdown

    detected_at: datetime
    status: str

    triggering_indicators: Dict[str, Any]
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OpportunityCapture(BaseModel):
    """Schema for capturing/acting on an opportunity"""
    captured_by: str
    action_taken: str
    expected_benefit: str
    investment_required: Optional[Decimal] = None
    implementation_timeline: Optional[str] = None


class OpportunityOutcome(BaseModel):
    """Schema for recording opportunity outcome"""
    outcome_achieved: bool
    actual_benefit: str
    actual_investment: Optional[Decimal] = None
    lessons_learned: Optional[str] = None
    roi_estimate: Optional[Decimal] = None
