from datetime import datetime, timezone
from typing import Optional, List, Literal
from beanie import Document, Indexed
from pydantic import Field, BaseModel


class Recommendation(BaseModel):
    title: str
    description: str
    priority: Literal["high", "medium", "low"] = "medium"
    action_type: Optional[str] = None
    estimated_effort: Optional[str] = None
    potential_impact: Optional[str] = None


class RelatedIndicator(BaseModel):
    indicator_name: str
    indicator_type: Literal["national", "operational"]
    contribution_weight: Optional[float] = None


class BusinessInsight(Document):

    company_id: Indexed(str)  # type: ignore
    type: Literal["risk", "opportunity"]
    severity: Literal["critical", "high", "medium", "low"]

    # Content
    title: str
    description: str
    summary: Optional[str] = None

    # Scoring
    impact_score: int = Field(..., ge=1, le=10)
    probability: int = Field(..., ge=1, le=10)
    risk_score: Optional[float] = None  # For risks: impact * probability
    potential_value: Optional[float] = None  # For opportunities
    feasibility: Optional[int] = Field(default=None, ge=1, le=10)

    # Classification
    category: Optional[str] = None  # e.g., "supply_chain", "financial", "market"
    tags: List[str] = Field(default_factory=list)

    # Recommendations
    recommendations: List[Recommendation] = Field(default_factory=list)

    # Related indicators
    related_indicators: List[RelatedIndicator] = Field(default_factory=list)

    # Time horizon
    time_horizon: Optional[str] = None  # "immediate", "short_term", "long_term"

    # Status
    active: bool = Field(default=True)
    acknowledged: bool = Field(default=False)
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "business_insights"
        use_state_management = True

    def calculate_risk_score(self) -> float:
        return (self.impact_score * self.probability) / 10

    def acknowledge(self, user_id: str) -> None:
        self.acknowledged = True
        self.acknowledged_at = datetime.now(timezone.utc)
        self.acknowledged_by = user_id
        self.updated_at = datetime.now(timezone.utc)

    def resolve(self) -> None:
        self.resolved = True
        self.resolved_at = datetime.now(timezone.utc)
        self.active = False
        self.updated_at = datetime.now(timezone.utc)