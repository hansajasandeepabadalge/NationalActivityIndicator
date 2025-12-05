"""
Layer 4: Risk Detection Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class TriggerCondition(BaseModel):
    """Individual trigger condition for risk detection"""
    indicator: str = Field(..., description="Operational indicator code")
    operator: str = Field(..., description="Comparison operator: <, >, ==, !=, >=, <=")
    threshold: float = Field(..., description="Threshold value")
    weight: Optional[float] = Field(0.5, description="Weight in combined logic (0-1)")


class TriggerLogic(BaseModel):
    """Complete trigger logic for risk/opportunity"""
    conditions: List[TriggerCondition]
    logic: str = Field("AND", description="Combination logic: AND or OR")
    confidence_threshold: float = Field(0.6, description="Minimum confidence to trigger")


class RiskDefinitionBase(BaseModel):
    """Base schema for risk definition"""
    code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    type: str = Field("risk", description="Type: risk or opportunity")
    category: str = Field(..., max_length=50)
    subcategory: Optional[str] = Field(None, max_length=100)
    trigger_logic: Dict[str, Any]
    default_impact: Optional[Decimal] = Field(None, ge=0, le=10)
    default_probability: Optional[Decimal] = Field(None, ge=0, le=1)
    default_urgency: Optional[int] = Field(None, ge=1, le=5)
    applicable_industries: Optional[List[str]] = None
    applicable_business_scales: Optional[List[str]] = None
    description_template: Optional[str] = None
    is_active: bool = True


class RiskDefinitionCreate(RiskDefinitionBase):
    """Schema for creating a risk definition"""
    pass


class RiskDefinitionUpdate(BaseModel):
    """Schema for updating a risk definition"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    category: Optional[str] = None
    trigger_logic: Optional[Dict[str, Any]] = None
    default_impact: Optional[Decimal] = None
    default_probability: Optional[Decimal] = None
    is_active: Optional[bool] = None


class RiskDefinition(RiskDefinitionBase):
    """Complete risk definition schema with database fields"""
    definition_id: int
    created_at: datetime
    updated_at: datetime
    version: int

    model_config = ConfigDict(from_attributes=True)


class DetectedRisk(BaseModel):
    """Schema for a detected risk (before storage)"""
    definition_id: Optional[int] = None
    risk_code: str
    company_id: str
    title: str
    description: str
    category: str

    # Scoring
    probability: Decimal = Field(..., ge=0, le=1, description="Probability (0-1)")
    impact: Decimal = Field(..., ge=0, le=10, description="Impact (0-10)")
    urgency: int = Field(..., ge=1, le=5, description="Urgency (1-5)")
    confidence: Decimal = Field(..., ge=0, le=1, description="Confidence (0-1)")

    final_score: Decimal = Field(..., description="Final risk score")
    severity_level: str = Field(..., description="critical, high, medium, low")

    # Context
    triggering_indicators: Dict[str, Any]
    detection_method: str = Field(..., description="rule_based, pattern, ml")
    reasoning: Optional[str] = Field(None, description="Why was this risk detected?")

    # Temporal
    expected_impact_time: Optional[datetime] = None
    expected_duration_hours: Optional[int] = None

    # Priority
    is_urgent: bool = False
    requires_immediate_action: bool = False


class RiskScoreBreakdown(BaseModel):
    """Detailed breakdown of risk score calculation"""
    probability: Decimal
    probability_reasoning: str

    impact: Decimal
    impact_reasoning: str

    urgency: int
    urgency_reasoning: str

    confidence: Decimal
    confidence_source: str

    final_score: Decimal
    severity: str


class RiskWithScore(BaseModel):
    """Risk with detailed scoring information"""
    insight_id: int
    company_id: str
    title: str
    description: str
    category: str

    score_breakdown: RiskScoreBreakdown

    detected_at: datetime
    status: str

    triggering_indicators: Dict[str, Any]
    affected_operations: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class RiskAcknowledgement(BaseModel):
    """Schema for acknowledging a risk"""
    acknowledged_by: str
    notes: Optional[str] = None


class RiskResolution(BaseModel):
    """Schema for resolving a risk"""
    resolution_notes: str
    actual_impact: Optional[str] = None
    actual_outcome: Optional[str] = None
    lessons_learned: Optional[str] = None
