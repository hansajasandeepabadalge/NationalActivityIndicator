"""SQLAlchemy models for indicators"""
from sqlalchemy import Column, String, Float, Integer, Boolean, Text, TIMESTAMP, ForeignKey, Date
from sqlalchemy.dialects.postgresql import JSONB, ENUM, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class IndicatorDefinition(Base):
    __tablename__ = 'indicator_definitions'

    indicator_id = Column(String(50), primary_key=True)
    indicator_name = Column(String(200), nullable=False)
    pestel_category = Column(ENUM(
        'Political', 'Economic', 'Social', 'Technological', 'Environmental', 'Legal',
        name='pestel_category_enum', create_type=False
    ), nullable=False)
    description = Column(Text)
    calculation_type = Column(ENUM(
        'frequency_count', 'sentiment_aggregate', 'numeric_extraction',
        'composite', 'ratio', 'weighted_average',
        name='calculation_type_enum', create_type=False
    ), nullable=False)
    base_weight = Column(Float, default=1.0)
    aggregation_window = Column(String(20), default='1 day')
    threshold_high = Column(Float)
    threshold_low = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    extra_metadata = Column(JSONB)

    # Relationships
    keywords = relationship("IndicatorKeyword", back_populates="indicator", cascade="all, delete-orphan")
    values = relationship("IndicatorValue", back_populates="indicator", cascade="all, delete-orphan")
    events = relationship("IndicatorEvent", back_populates="indicator", cascade="all, delete-orphan")

class IndicatorKeyword(Base):
    __tablename__ = 'indicator_keywords'

    keyword_id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(String(50), ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), nullable=False)
    keyword_text = Column(String(200), nullable=False)
    keyword_type = Column(String(50), default='exact_match')
    weight = Column(Float, default=1.0)
    language = Column(String(10), default='en')
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    indicator = relationship("IndicatorDefinition", back_populates="keywords")

class IndicatorValue(Base):
    __tablename__ = 'indicator_values'

    indicator_id = Column(String(50), ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), primary_key=True)
    timestamp = Column(TIMESTAMP(timezone=True), primary_key=True)
    value = Column(Float, nullable=False)
    raw_count = Column(Integer, default=0)
    sentiment_score = Column(Float)
    confidence = Column(Float, default=1.0)
    source_count = Column(Integer, default=1)
    extra_metadata = Column(JSONB)

    # Relationships
    indicator = relationship("IndicatorDefinition", back_populates="values")

class IndicatorEvent(Base):
    __tablename__ = 'indicator_events'

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(String(50), ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    event_type = Column(ENUM(
        'threshold_breach', 'anomaly_detected', 'rapid_change',
        'correlation_break', 'data_quality_issue',
        name='event_type_enum', create_type=False
    ), nullable=False)
    severity = Column(String(20), default='medium')
    value_before = Column(Float)
    value_after = Column(Float)
    description = Column(Text)
    extra_metadata = Column(JSONB)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    indicator = relationship("IndicatorDefinition", back_populates="events")

class IndicatorCorrelation(Base):
    __tablename__ = 'indicator_correlations'

    correlation_id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id_1 = Column(String(50), ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), nullable=False)
    indicator_id_2 = Column(String(50), ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), nullable=False)
    correlation_coefficient = Column(Float, nullable=False)
    p_value = Column(Float)
    lag_days = Column(Integer, default=0)
    calculation_date = Column(Date, nullable=False)
    sample_size = Column(Integer, nullable=False)
    confidence_interval = Column(JSONB)
    is_significant = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
