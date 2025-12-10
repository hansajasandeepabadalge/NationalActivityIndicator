from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class IndustryTemplate(Base):
    __tablename__ = "industry_templates"
    
    industry_id = Column(String(50), primary_key=True)
    industry_name = Column(String(200), nullable=False)
    display_name = Column(String(200))
    parent_industry = Column(String(50))
    sensitivity_config = Column(JSONB, nullable=False)
    impact_lags = Column(JSONB)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    
    company_id = Column(String(50), primary_key=True)
    company_name = Column(String(200), nullable=False)
    industry_id = Column(String(50), ForeignKey("industry_templates.industry_id"))
    sub_industry = Column(String(100))
    business_scale = Column(String(20))
    employee_count = Column(Integer)
    annual_revenue = Column(Float)
    supply_chain_config = Column(JSONB)
    critical_dependencies = Column(JSONB)
    customer_profile = Column(JSONB)
    risk_profile = Column(JSONB)
    custom_weights = Column(JSONB)
    alert_thresholds = Column(JSONB)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    locations = relationship("CompanyLocation", back_populates="company")

class CompanyLocation(Base):
    __tablename__ = "company_locations"
    
    location_id = Column(String(50), primary_key=True)
    company_id = Column(String(50), ForeignKey("company_profiles.company_id"))
    location_name = Column(String(200), nullable=False)
    location_type = Column(String(50))
    city = Column(String(100))
    district = Column(String(100))
    province = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    size_category = Column(String(50))
    daily_capacity = Column(Integer)
    employee_count = Column(Integer)
    operating_hours = Column(JSONB)
    critical_services = Column(ARRAY(Text))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("CompanyProfile", back_populates="locations")

class OperationalIndicatorDefinition(Base):
    __tablename__ = "operational_indicator_definitions"
    
    operational_indicator_id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_code = Column(String(100), unique=True, nullable=False)
    indicator_name = Column(String(200), nullable=False)
    display_name = Column(String(200))
    indicator_type = Column(String(50))
    applicable_industries = Column(ARRAY(Text))
    calculation_method = Column(String(50))
    calculation_formula = Column(Text)
    input_indicators = Column(JSONB)
    value_type = Column(String(20))
    min_value = Column(Float)
    max_value = Column(Float)
    unit = Column(String(50))
    interpretation_levels = Column(JSONB)
    description = Column(Text)
    business_relevance = Column(Text)
    recommended_actions = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TranslationRule(Base):
    __tablename__ = "translation_rules"
    
    rule_id = Column(Integer, primary_key=True, autoincrement=True)
    national_indicator_code = Column(String(100), nullable=False)
    operational_indicator_code = Column(String(100), ForeignKey("operational_indicator_definitions.indicator_code"))
    applicable_industries = Column(ARRAY(Text))
    applicable_business_scales = Column(ARRAY(Text))
    rule_type = Column(String(50))
    rule_config = Column(JSONB, nullable=False)
    impact_lag_hours = Column(Integer, default=0)
    impact_duration_hours = Column(Integer)
    confidence_level = Column(Float)
    description = Column(Text)
    validation_notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RecommendationTemplate(Base):
    __tablename__ = "recommendation_templates"
    
    template_id = Column(Integer, primary_key=True, autoincrement=True)
    operational_indicator_code = Column(String(100))
    severity_level = Column(String(20))
    industry_id = Column(String(50))
    recommendation_title = Column(String(200))
    recommendation_text = Column(Text)
    action_items = Column(JSONB)
    rationale = Column(Text)
    estimated_cost_impact = Column(String(100))
    estimated_time_to_implement = Column(String(100))
    related_templates = Column(ARRAY(Integer))
    external_resources = Column(ARRAY(Text))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
