"""
Layer 5: Company Profile Schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from decimal import Decimal


class CompanyProfileResponse(BaseModel):
    """Schema for company profile response"""
    company_id: str
    company_name: str
    display_name: Optional[str] = None
    
    # Classification
    industry: str
    sub_industry: Optional[str] = None
    business_scale: Optional[str] = None
    
    # Business details
    description: Optional[str] = None
    business_model: Optional[str] = None
    
    # Financial profile
    annual_revenue: Optional[Decimal] = None
    revenue_currency: str = "LKR"
    
    # Operational profile
    employee_count: Optional[int] = None
    primary_location: Optional[str] = None
    locations: Optional[List[str]] = None
    
    # Market position
    market_position: Optional[str] = None
    
    # Dependencies (simplified)
    supply_chain_profile: Optional[Dict[str, Any]] = None
    operational_dependencies: Optional[Dict[str, Any]] = None
    
    # Risk profile
    risk_tolerance: Optional[str] = None
    vulnerability_factors: Optional[Dict[str, Any]] = None
    
    # Strategic
    strategic_priorities: Optional[List[str]] = None
    growth_stage: Optional[str] = None
    
    class Config:
        from_attributes = True


class CompanyProfileUpdate(BaseModel):
    """Schema for updating company profile"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    business_model: Optional[str] = None
    
    # Financial
    annual_revenue: Optional[Decimal] = None
    revenue_currency: Optional[str] = None
    
    # Operational
    employee_count: Optional[int] = None
    primary_location: Optional[str] = None
    locations: Optional[List[str]] = None
    
    # Market
    market_position: Optional[str] = None
    
    # Dependencies
    supply_chain_profile: Optional[Dict[str, Any]] = None
    operational_dependencies: Optional[Dict[str, Any]] = None
    
    # Risk
    risk_tolerance: Optional[str] = None
    vulnerability_factors: Optional[Dict[str, Any]] = None
    
    # Strategic
    strategic_priorities: Optional[List[str]] = None
    growth_stage: Optional[str] = None


class CompanyCreate(BaseModel):
    """Schema for creating a new company profile"""
    company_id: str
    company_name: str
    industry: str
    sub_industry: Optional[str] = None
    business_scale: Optional[str] = "medium"
    description: Optional[str] = None
