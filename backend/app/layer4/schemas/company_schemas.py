"""
Layer 4: Company Profile Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal


class SupplyChainProfile(BaseModel):
    """Supply chain dependency profile"""
    import_dependency: float = Field(..., ge=0, le=1, description="Import dependency (0-1)")
    key_suppliers: List[str] = Field(default_factory=list)
    supplier_concentration: str = Field(..., description="low, medium, high")
    average_lead_time_days: int


class OperationalDependencies(BaseModel):
    """Operational dependency assessment"""
    power_dependency: str = Field(..., description="low, medium, high, critical")
    transport_dependency: str = Field(..., description="low, medium, high, critical")
    workforce_dependency: str = Field(..., description="low, medium, high, critical")
    digital_dependency: str = Field(..., description="low, medium, high, critical")


class GeographicExposure(BaseModel):
    """Geographic risk exposure"""
    regions: List[str] = Field(..., description="Regions where business operates")
    concentration: str = Field(..., description="concentrated, regional, diversified")
    export_percentage: float = Field(..., ge=0, le=1, description="Export as % of revenue")


class VulnerabilityFactors(BaseModel):
    """Business vulnerability assessment"""
    currency_exposure: str = Field(..., description="low, medium, high")
    regulatory_exposure: str = Field(..., description="low, medium, high")
    commodity_price_sensitivity: str = Field(..., description="low, medium, high")
    seasonality_impact: str = Field(..., description="low, medium, high")


class AlertPreferences(BaseModel):
    """User alert preferences"""
    critical_threshold: float = Field(40.0, description="Score threshold for critical alerts")
    notification_channels: List[str] = Field(default_factory=lambda: ["email", "dashboard"])
    quiet_hours: Optional[Dict[str, str]] = None  # {"start": "20:00", "end": "08:00"}
    categories_to_watch: List[str] = Field(default_factory=list)


class InsightCustomization(BaseModel):
    """Customization for insight generation"""
    focus_areas: List[str] = Field(default_factory=list)
    ignore_categories: List[str] = Field(default_factory=list)
    custom_thresholds: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    """
    Example:
    {
        "RISK_SUPPLY_CHAIN": {"probability": 0.5, "impact": 6.0}
    }
    """


class CompanyProfileBase(BaseModel):
    """Base schema for company profile"""
    company_name: str = Field(..., max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)

    industry: str = Field(..., max_length=100)
    sub_industry: Optional[str] = Field(None, max_length=100)
    business_scale: str = Field(..., description="small, medium, large, enterprise")

    description: Optional[str] = None
    business_model: Optional[str] = Field(None, description="B2B, B2C, B2B2C, marketplace, etc.")

    # Financial profile
    annual_revenue: Optional[Decimal] = None
    revenue_currency: str = Field("LKR", max_length=10)
    cash_reserves: Optional[Decimal] = None
    debt_level: Optional[str] = Field(None, description="low, moderate, high")

    # Operational profile
    employee_count: Optional[int] = None
    locations: Optional[List[str]] = None
    primary_location: Optional[str] = Field(None, max_length=100)

    # Market position
    market_position: Optional[str] = Field(None, description="leader, challenger, follower, niche")
    market_share_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    key_competitors: Optional[List[str]] = None

    # Risk profile
    risk_tolerance: str = Field("moderate", description="conservative, moderate, aggressive")
    strategic_priorities: Optional[List[str]] = None
    growth_stage: Optional[str] = Field(None, description="startup, growth, mature, decline, turnaround")

    # Contact
    primary_contact_name: Optional[str] = Field(None, max_length=100)
    primary_contact_email: Optional[EmailStr] = None
    ownership_type: Optional[str] = Field(None, description="private, public, state_owned, family_business")

    # Notes
    notes: Optional[str] = None


class CompanyProfileCreate(CompanyProfileBase):
    """Schema for creating a company profile"""
    company_id: str = Field(..., max_length=50, description="Unique company identifier")

    # Complex nested fields (optional on create)
    supply_chain_profile: Optional[SupplyChainProfile] = None
    operational_dependencies: Optional[OperationalDependencies] = None
    geographic_exposure: Optional[GeographicExposure] = None
    vulnerability_factors: Optional[VulnerabilityFactors] = None
    alert_preferences: Optional[AlertPreferences] = None
    insight_customization: Optional[InsightCustomization] = None

    is_active: bool = True
    onboarding_completed: bool = False


class CompanyProfileUpdate(BaseModel):
    """Schema for updating a company profile"""
    company_name: Optional[str] = None
    display_name: Optional[str] = None
    industry: Optional[str] = None
    business_scale: Optional[str] = None

    annual_revenue: Optional[Decimal] = None
    cash_reserves: Optional[Decimal] = None
    employee_count: Optional[int] = None

    supply_chain_profile: Optional[Dict[str, Any]] = None
    operational_dependencies: Optional[Dict[str, Any]] = None
    geographic_exposure: Optional[Dict[str, Any]] = None
    vulnerability_factors: Optional[Dict[str, Any]] = None

    alert_preferences: Optional[Dict[str, Any]] = None
    insight_customization: Optional[Dict[str, Any]] = None

    risk_tolerance: Optional[str] = None
    strategic_priorities: Optional[List[str]] = None

    is_active: Optional[bool] = None
    onboarding_completed: Optional[bool] = None
    notes: Optional[str] = None


class CompanyProfile(CompanyProfileBase):
    """Complete company profile schema"""
    company_id: str

    # Complex nested fields (stored as JSONB)
    supply_chain_profile: Optional[Dict[str, Any]] = None
    operational_dependencies: Optional[Dict[str, Any]] = None
    geographic_exposure: Optional[Dict[str, Any]] = None
    vulnerability_factors: Optional[Dict[str, Any]] = None
    alert_preferences: Optional[Dict[str, Any]] = None
    insight_customization: Optional[Dict[str, Any]] = None

    is_active: bool
    onboarding_completed: bool

    created_at: datetime
    updated_at: datetime
    last_insight_generated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CompanyProfileSummary(BaseModel):
    """Lightweight company profile summary"""
    company_id: str
    company_name: str
    industry: str
    business_scale: str
    market_position: Optional[str] = None
    is_active: bool
    last_insight_generated: Optional[datetime] = None


class CompanyVulnerabilityAssessment(BaseModel):
    """Vulnerability assessment result"""
    company_id: str
    company_name: str

    overall_vulnerability_score: Decimal = Field(..., ge=0, le=100)

    supply_chain_vulnerability: Decimal
    financial_vulnerability: Decimal
    operational_vulnerability: Decimal
    geographic_vulnerability: Decimal
    competitive_vulnerability: Decimal

    top_vulnerabilities: List[str]
    mitigation_priority_areas: List[str]

    assessed_at: datetime
