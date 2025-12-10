"""
Layer 4: Recommendation and Action Planning Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class RecommendationBase(BaseModel):
    """Base schema for recommendation"""
    insight_id: int
    category: str = Field(..., description="immediate, short_term, medium_term, long_term")
    priority: int = Field(..., ge=1, le=10, description="1 = highest priority")

    action_title: str = Field(..., max_length=200)
    action_description: str

    responsible_role: Optional[str] = Field(None, max_length=100)
    estimated_effort: Optional[str] = Field(None, description="Low, Medium, High")
    estimated_cost: Optional[str] = None
    estimated_timeframe: Optional[str] = Field(None, description="e.g., '24 hours', 'This week'")

    expected_benefit: Optional[str] = None
    success_metrics: Optional[List[str]] = None
    required_resources: Optional[Dict[str, Any]] = None


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation"""
    status: str = "pending"


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation"""
    status: Optional[str] = None  # pending, in_progress, completed, dismissed
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    implementation_notes: Optional[str] = None
    outcome_achieved: Optional[bool] = None
    actual_benefit: Optional[str] = None


class Recommendation(RecommendationBase):
    """Complete recommendation schema"""
    recommendation_id: int

    status: str
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    implementation_notes: Optional[str] = None
    outcome_achieved: Optional[bool] = None
    actual_benefit: Optional[str] = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionPlanStep(BaseModel):
    """Individual action step in a plan"""
    step_number: int
    action: str
    category: str = Field(..., description="immediate, short_term, medium_term")
    timeframe: str

    responsible: str
    resources: Dict[str, Any] = Field(default_factory=dict)
    success_metric: str

    dependencies: Optional[List[int]] = Field(None, description="Step numbers that must complete first")
    risk_factors: Optional[List[str]] = None


class ActionPlan(BaseModel):
    """Complete action plan for an insight"""
    insight_id: int
    insight_title: str
    plan_title: str

    action_items: List[ActionPlanStep]

    total_estimated_cost: Optional[Decimal] = None
    total_estimated_duration: Optional[str] = None
    total_personnel_required: Optional[int] = None

    risk_factors: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    alternatives: Optional[List[str]] = None

    created_at: datetime
    created_by: Optional[str] = None


class RecommendationTemplate(BaseModel):
    """Template for generating recommendations"""
    template_id: str
    template_name: str
    applicable_to: List[str] = Field(..., description="List of risk/opportunity codes")

    situation_template: str
    immediate_actions: List[str]
    short_term_actions: List[str]
    medium_term_actions: Optional[List[str]] = None

    resource_estimates: Dict[str, Any]
    success_metrics_template: List[str]


class ScenarioSimulationCreate(BaseModel):
    """Schema for creating a scenario simulation"""
    company_id: str
    scenario_name: str
    scenario_description: str

    assumptions: Dict[str, Any] = Field(..., description="What-if assumptions")


class ScenarioSimulationResult(BaseModel):
    """Result of a scenario simulation"""
    simulation_id: int
    company_id: str
    scenario_name: str
    scenario_description: str

    assumptions: Dict[str, Any]

    predicted_risks: List[Dict[str, Any]]
    predicted_opportunities: List[Dict[str, Any]]

    estimated_impact: Dict[str, Any]
    """
    Example:
    {
        "revenue_impact": -250000,
        "cost_impact": 75000,
        "operational_disruption_days": 10,
        "market_share_impact": -2.5
    }
    """

    recommended_contingencies: List[Dict[str, Any]]
    preparation_actions: List[Dict[str, Any]]

    status: str
    created_by: Optional[str] = None
    created_at: datetime
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class NarrativeContent(BaseModel):
    """Generated narrative content for an insight"""
    insight_id: int
    insight_type: str

    emoji: str = Field(..., description="Visual indicator emoji")
    headline: str = Field(..., description="Attention-grabbing headline")
    summary: str = Field(..., description="2-3 sentence executive summary")

    situation: str = Field(..., description="What's happening?")
    why_it_matters: str = Field(..., description="Business context and importance")
    what_to_do: str = Field(..., description="High-level action guidance")

    urgency_indicator: str = Field(..., description="NOW, TODAY, THIS WEEK, THIS MONTH")
    confidence_statement: str = Field(..., description="How certain we are")

    generated_at: datetime


class InsightWithRecommendations(BaseModel):
    """Complete insight with recommendations"""
    insight: Dict[str, Any]  # BusinessInsight
    recommendations: List[Recommendation]
    action_plan: Optional[ActionPlan] = None
    narrative: Optional[NarrativeContent] = None
    related_competitive_intel: Optional[List[Dict[str, Any]]] = None
