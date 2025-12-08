"""
Company schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


class OperationalProfileSchema(BaseModel):
    """Schema for operational profile."""
    import_dependency: float = Field(default=0, ge=0, le=100)
    fuel_dependency: Literal["critical", "high", "medium", "low"] = "medium"
    workforce_provinces: List[str] = Field(default_factory=list)
    customer_base: List[Literal["b2c", "b2b", "export", "government"]] = Field(default_factory=list)


class RiskSensitivitySchema(BaseModel):
    """Schema for risk sensitivity."""
    currency_sensitivity: int = Field(default=5, ge=1, le=10)
    power_cut_impact: Literal["critical", "high", "medium", "low"] = "medium"
    political_stability_impact: Literal["high", "medium", "low"] = "medium"
    supply_chain_sensitivity: Literal["high", "medium", "low"] = "medium"


class CompanyCreate(BaseModel):
    """Schema for creating a company profile."""
    company_name: str = Field(..., min_length=2, max_length=200)
    industry: str
    business_scale: Literal["micro", "small", "medium", "large"] = "small"
    location_province: Optional[str] = None
    location_city: Optional[str] = None
    num_employees: Optional[int] = Field(default=None, ge=1)
    year_established: Optional[int] = Field(default=None, ge=1800, le=2100)
    annual_revenue_range: Optional[str] = None
    operational_profile: Optional[OperationalProfileSchema] = None
    risk_sensitivity: Optional[RiskSensitivitySchema] = None
    profile_data: Optional[Dict[str, Any]] = None


class CompanyUpdate(BaseModel):
    """Schema for updating a company profile."""
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    industry: Optional[str] = None
    business_scale: Optional[Literal["micro", "small", "medium", "large"]] = None
    location_province: Optional[str] = None
    location_city: Optional[str] = None
    num_employees: Optional[int] = Field(default=None, ge=1)
    year_established: Optional[int] = Field(default=None, ge=1800, le=2100)
    annual_revenue_range: Optional[str] = None
    operational_profile: Optional[OperationalProfileSchema] = None
    risk_sensitivity: Optional[RiskSensitivitySchema] = None
    profile_data: Optional[Dict[str, Any]] = None


class CompanyResponse(BaseModel):
    """Schema for company response."""
    id: str
    user_id: str
    company_name: str
    industry: str
    business_scale: str
    location_province: Optional[str] = None
    location_city: Optional[str] = None
    num_employees: Optional[int] = None
    year_established: Optional[int] = None
    annual_revenue_range: Optional[str] = None
    operational_profile: OperationalProfileSchema
    risk_sensitivity: RiskSensitivitySchema
    profile_data: Dict[str, Any]
    health_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyListItem(BaseModel):
    """Schema for company list item (admin view)."""
    id: str
    company_name: str
    industry: str
    business_scale: str
    location_province: Optional[str] = None
    health_score: Optional[float] = None
    risk_count: int = 0
    critical_risks: int = 0

    class Config:
        from_attributes = True


class IndustryAggregation(BaseModel):
    """Schema for industry-level aggregation."""
    industry: str
    company_count: int
    avg_health_score: Optional[float] = None
    avg_indicators: Dict[str, float] = Field(default_factory=dict)
    companies_at_risk: int = 0
    companies_healthy: int = 0