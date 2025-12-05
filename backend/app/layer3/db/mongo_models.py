from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class CalculationDetail(BaseModel):
    method: str
    inputs: List[Dict[str, Any]]
    base_calculation: float
    adjustments: List[Dict[str, Any]]
    final_value: float
    rounded_value: float
    confidence: float

class CalculationContext(BaseModel):
    industry_average: Optional[float] = None
    deviation_from_average: Optional[float] = None
    company_rank_percentile: Optional[float] = None
    trend_direction: Optional[str] = None
    compared_to_yesterday: Optional[float] = None

class CalculationInterpretation(BaseModel):
    level: str
    severity_score: float
    status_label: str
    requires_attention: bool

class OperationalCalculation(BaseModel):
    company_id: str
    operational_indicator_code: str
    calculation_timestamp: datetime
    calculation_details: CalculationDetail
    context: CalculationContext
    interpretation: CalculationInterpretation

class RecommendationAction(BaseModel):
    action: str
    responsible: str
    timeline: str

class RecommendationImpact(BaseModel):
    cost_savings: Optional[str] = None
    revenue_loss: Optional[str] = None
    staff_impact: Optional[str] = None
    cost_increase: Optional[str] = None
    risk_mitigation: Optional[str] = None

class RecommendationItem(BaseModel):
    priority: str
    category: str
    title: str
    description: str
    actions: List[RecommendationAction]
    expected_impact: RecommendationImpact
    confidence: float
    related_indicators: List[str]

class ScenarioAnalysis(BaseModel):
    if_conditions_worsen: Dict[str, Any]
    if_conditions_improve: Dict[str, Any]

class ValidityPeriod(BaseModel):
    start: datetime
    end: datetime
    reason: str

class OperationalRecommendation(BaseModel):
    company_id: str
    generated_at: datetime
    trigger: Dict[str, Any]
    recommendations: List[RecommendationItem]
    scenario_analysis: Optional[ScenarioAnalysis] = None
    validity_period: ValidityPeriod
