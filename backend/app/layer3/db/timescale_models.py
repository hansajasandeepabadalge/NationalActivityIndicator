from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Text, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OperationalIndicatorValue(Base):
    __tablename__ = "operational_indicator_values"
    
    time = Column(DateTime(timezone=True), nullable=False)
    company_id = Column(String(50), nullable=False)
    operational_indicator_code = Column(String(100), nullable=False)
    location_id = Column(String(50), default='')
    
    value = Column(Float, nullable=False)
    normalized_value = Column(Float)
    calculation_method = Column(String(50))
    confidence_score = Column(Float)
    input_national_indicators = Column(JSONB)
    previous_value = Column(Float)
    change_percentage = Column(Float)
    industry_average = Column(Float)
    deviation_from_average = Column(Float)
    quality_flags = Column(ARRAY(Text))
    
    __table_args__ = (
        PrimaryKeyConstraint('time', 'company_id', 'operational_indicator_code', 'location_id'),
    )

class OperationalAlert(Base):
    __tablename__ = "operational_alerts"
    
    time = Column(DateTime(timezone=True), nullable=False)
    alert_id = Column(String(50), nullable=False)
    company_id = Column(String(50), nullable=False)
    
    operational_indicator_code = Column(String(100))
    location_id = Column(String(50))
    alert_type = Column(String(50))
    severity = Column(String(20))
    current_value = Column(Float)
    threshold_value = Column(Float)
    previous_value = Column(Float)
    trigger_condition = Column(Text)
    affected_operations = Column(ARRAY(Text))
    recommendations = Column(JSONB)
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(ARRAY(Text))
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        PrimaryKeyConstraint('time', 'alert_id'),
    )
