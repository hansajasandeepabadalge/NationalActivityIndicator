"""
Company model for business client profiles.
"""
from datetime import datetime, timezone
from typing import Optional, List, Literal
from beanie import Document, Indexed
from pydantic import Field, BaseModel


class OperationalProfile(BaseModel):
    """Operational characteristics of the company."""
    import_dependency: float = Field(default=0, ge=0, le=100, description="Import dependency percentage")
    fuel_dependency: Literal["critical", "high", "medium", "low"] = Field(default="medium")
    workforce_provinces: List[str] = Field(default_factory=list)
    customer_base: List[Literal["b2c", "b2b", "export", "government"]] = Field(default_factory=list)


class RiskSensitivity(BaseModel):
    """Risk sensitivity profile of the company."""
    currency_sensitivity: int = Field(default=5, ge=1, le=10)
    power_cut_impact: Literal["critical", "high", "medium", "low"] = Field(default="medium")
    political_stability_impact: Literal["high", "medium", "low"] = Field(default="medium")
    supply_chain_sensitivity: Literal["high", "medium", "low"] = Field(default="medium")


class Company(Document):
    """
    Company document model for MongoDB.
    Stores business client profiles and operational data.
    """

    # Owner reference
    user_id: Indexed(str)  # type: ignore

    # Basic information
    company_name: str = Field(..., min_length=2, max_length=200)
    industry: str = Field(..., description="Industry category")
    business_scale: Literal["micro", "small", "medium", "large"] = Field(default="small")

    # Location
    location_province: Optional[str] = None
    location_city: Optional[str] = None

    # Company details
    num_employees: Optional[int] = Field(default=None, ge=1)
    year_established: Optional[int] = None
    annual_revenue_range: Optional[str] = None

    # Operational profile
    operational_profile: OperationalProfile = Field(default_factory=OperationalProfile)

    # Risk sensitivity
    risk_sensitivity: RiskSensitivity = Field(default_factory=RiskSensitivity)

    # Additional data (flexible storage)
    profile_data: dict = Field(default_factory=dict)

    # Computed scores (cached)
    health_score: Optional[float] = None
    last_health_calculation: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "companies"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "company_name": "ABC Retail Ltd",
                "industry": "retail",
                "business_scale": "medium",
                "location_province": "Western",
                "location_city": "Colombo",
                "num_employees": 150
            }
        }

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)


# Industry categories
INDUSTRIES = [
    "retail",
    "manufacturing",
    "logistics",
    "healthcare",
    "education",
    "technology",
    "finance",
    "agriculture",
    "construction",
    "hospitality",
    "real_estate",
    "energy",
    "telecommunications",
    "transportation",
    "food_beverage",
    "textiles",
    "automotive",
    "pharmaceuticals",
    "other"
]

# Sri Lankan provinces
PROVINCES = [
    "Western",
    "Central",
    "Southern",
    "Northern",
    "Eastern",
    "North Western",
    "North Central",
    "Uva",
    "Sabaragamuwa"
]