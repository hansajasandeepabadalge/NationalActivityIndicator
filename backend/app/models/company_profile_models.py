"""
Layer 4: Company Profile Models
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.session import Base


class CompanyProfile(Base):
    """Business profile data for contextual insights"""
    __tablename__ = "company_profiles"

    company_id = Column(String(50), primary_key=True)

    # Basic information
    company_name = Column(String(200), nullable=False)
    display_name = Column(String(200))

    # Classification
    industry = Column(String(100), nullable=False, index=True)
    sub_industry = Column(String(100))
    business_scale = Column(String(50))  # 'small', 'medium', 'large', 'enterprise'

    # Business details
    description = Column(Text)
    business_model = Column(String(100))  # 'B2B', 'B2C', 'B2B2C', 'marketplace', etc.

    # Financial profile
    annual_revenue = Column(DECIMAL(15, 2))
    revenue_currency = Column(String(10), default='LKR')
    cash_reserves = Column(DECIMAL(15, 2))
    debt_level = Column(String(50))  # 'low', 'moderate', 'high'

    # Operational profile
    employee_count = Column(Integer)
    locations = Column(ARRAY(Text))
    primary_location = Column(String(100))

    # Dependencies
    supply_chain_profile = Column(JSONB)
    """
    Structure:
    {
        "import_dependency": 0.7,  # 0-1 scale
        "key_suppliers": ["supplier1", "supplier2"],
        "supplier_concentration": "high",  # low, medium, high
        "average_lead_time_days": 30
    }
    """

    operational_dependencies = Column(JSONB)
    """
    Structure:
    {
        "power_dependency": "high",
        "transport_dependency": "critical",
        "workforce_dependency": "medium",
        "digital_dependency": "high"
    }
    """

    # Market position
    market_position = Column(String(50))  # 'leader', 'challenger', 'follower', 'niche'
    market_share_percentage = Column(DECIMAL(5, 2))
    key_competitors = Column(ARRAY(Text))

    # Geographic exposure
    geographic_exposure = Column(JSONB)
    """
    Structure:
    {
        "regions": ["Western", "Central", "Southern"],
        "concentration": "diversified",  # concentrated, regional, diversified
        "export_percentage": 0.20
    }
    """

    # Risk profile
    risk_tolerance = Column(String(50))  # 'conservative', 'moderate', 'aggressive'
    vulnerability_factors = Column(JSONB)
    """
    Structure:
    {
        "currency_exposure": "high",
        "regulatory_exposure": "medium",
        "commodity_price_sensitivity": "high",
        "seasonality_impact": "medium"
    }
    """

    # Strategic priorities
    strategic_priorities = Column(ARRAY(Text))
    # ['growth', 'cost_reduction', 'risk_mitigation', 'innovation', 'market_expansion']

    growth_stage = Column(String(50))  # 'startup', 'growth', 'mature', 'decline', 'turnaround'

    # Contact and ownership
    primary_contact_name = Column(String(100))
    primary_contact_email = Column(String(100))
    ownership_type = Column(String(50))  # 'private', 'public', 'state_owned', 'family_business'

    # Layer 4 specific settings
    alert_preferences = Column(JSONB)
    """
    Structure:
    {
        "critical_threshold": 40,
        "notification_channels": ["email", "dashboard"],
        "quiet_hours": {"start": "20:00", "end": "08:00"},
        "categories_to_watch": ["operational", "financial"]
    }
    """

    insight_customization = Column(JSONB)
    """
    Structure:
    {
        "focus_areas": ["supply_chain", "cost_management"],
        "ignore_categories": [],
        "custom_thresholds": {
            "RISK_SUPPLY_CHAIN": {"probability": 0.5, "impact": 6.0}
        }
    }
    """

    # Status
    is_active = Column(Boolean, default=True, index=True)
    onboarding_completed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_insight_generated = Column(TIMESTAMP)

    # Notes
    notes = Column(Text)
