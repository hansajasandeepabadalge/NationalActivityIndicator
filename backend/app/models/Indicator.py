"""
Indicator models for national and operational indicators.
"""
from datetime import datetime, timezone
from typing import Optional, Literal, List
from beanie import Document, Indexed
from pydantic import Field, BaseModel


class IndicatorHistory(BaseModel):
    """Historical data point for an indicator."""
    value: float
    recorded_at: datetime


class NationalIndicator(Document):
    """
    National indicator document model.
    Represents country-level indicators from Layer 2.
    """

    indicator_name: Indexed(str, unique=True)  # type: ignore
    category: Literal["political", "economic", "social", "infrastructure"]

    # Current value
    value: float = Field(..., ge=0, le=100)
    trend: Literal["up", "down", "stable"] = Field(default="stable")
    trend_change: Optional[float] = None  # Change from last period

    # Display properties
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None  # Icon identifier

    # Thresholds for color coding
    threshold_good: float = Field(default=70)
    threshold_warning: float = Field(default=40)

    # Historical data (last 30 days)
    history: List[IndicatorHistory] = Field(default_factory=list)

    # Metadata
    data_source: Optional[str] = None
    calculation_method: Optional[str] = None

    # Timestamps
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "national_indicators"
        use_state_management = True

    @property
    def status(self) -> str:
        """Get status based on value thresholds."""
        if self.value >= self.threshold_good:
            return "good"
        elif self.value >= self.threshold_warning:
            return "warning"
        return "critical"

    @property
    def status_color(self) -> str:
        """Get color based on status."""
        status_colors = {
            "good": "green",
            "warning": "yellow",
            "critical": "red"
        }
        return status_colors.get(self.status, "gray")


class OperationalIndicatorValue(Document):
    """
    Operational indicator value document model.
    Company-specific indicators from Layer 3.
    """

    company_id: Indexed(str)  # type: ignore
    indicator_name: str

    # Current value
    value: float = Field(..., ge=0, le=100)
    trend: Literal["up", "down", "stable"] = Field(default="stable")
    trend_change: Optional[float] = None

    # Display properties
    display_name: Optional[str] = None

    # Thresholds (can be customized per company)
    threshold_good: float = Field(default=70)
    threshold_warning: float = Field(default=40)

    # Contributing factors
    contributing_factors: List[str] = Field(default_factory=list)

    # Historical data
    history: List[IndicatorHistory] = Field(default_factory=list)

    # Timestamps
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "operational_indicator_values"
        indexes = [
            [("company_id", 1), ("indicator_name", 1)],
        ]

    @property
    def status(self) -> str:
        """Get status based on value thresholds."""
        if self.value >= self.threshold_good:
            return "good"
        elif self.value >= self.threshold_warning:
            return "warning"
        return "critical"


# Default operational indicators
OPERATIONAL_INDICATORS = [
    {
        "name": "supply_chain_health",
        "display_name": "Supply Chain Health",
        "description": "Overall health of supply chain operations"
    },
    {
        "name": "workforce_readiness",
        "display_name": "Workforce Readiness",
        "description": "Workforce availability and capability"
    },
    {
        "name": "financial_stability",
        "display_name": "Financial Stability",
        "description": "Financial health and cash flow status"
    },
    {
        "name": "operational_readiness",
        "display_name": "Operational Readiness",
        "description": "Overall operational capability"
    },
    {
        "name": "market_conditions",
        "display_name": "Market Conditions",
        "description": "Current market demand and competition"
    }
]

# Default national indicators by category
NATIONAL_INDICATORS = {
    "political": [
        {"name": "political_stability", "display_name": "Political Stability Index"},
        {"name": "government_effectiveness", "display_name": "Government Effectiveness"},
        {"name": "policy_consistency", "display_name": "Policy Consistency"},
        {"name": "regulatory_quality", "display_name": "Regulatory Quality"},
        {"name": "public_protests", "display_name": "Public Protests Level"}
    ],
    "economic": [
        {"name": "economic_health", "display_name": "Economic Health Index"},
        {"name": "inflation_pressure", "display_name": "Inflation Pressure"},
        {"name": "currency_stability", "display_name": "Currency Stability"},
        {"name": "import_dependency", "display_name": "Import Dependency"},
        {"name": "business_confidence", "display_name": "Business Confidence"}
    ],
    "social": [
        {"name": "social_unrest", "display_name": "Social Unrest Index"},
        {"name": "public_mood", "display_name": "Public Mood"},
        {"name": "labor_market_health", "display_name": "Labor Market Health"},
        {"name": "education_quality", "display_name": "Education Quality"},
        {"name": "healthcare_access", "display_name": "Healthcare Access"}
    ],
    "infrastructure": [
        {"name": "transport_reliability", "display_name": "Transport Reliability"},
        {"name": "power_availability", "display_name": "Power Availability"},
        {"name": "communication_infra", "display_name": "Communication Infrastructure"},
        {"name": "supply_chain_health", "display_name": "Supply Chain Health"},
        {"name": "port_customs_efficiency", "display_name": "Port/Customs Efficiency"}
    ]
}