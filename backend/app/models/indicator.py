from sqlalchemy import Column, Integer, String, Float, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class IndicatorDefinition(Base):
    __tablename__ = "indicator_definitions"

    indicator_id = Column(Integer, primary_key=True, index=True)
    indicator_code = Column(String, unique=True, nullable=False, index=True)
    indicator_name = Column(String, nullable=False)
    display_name = Column(String)
    pestel_category = Column(String, nullable=False, index=True)
    subcategory = Column(String)
    calculation_type = Column(String, nullable=False)
    value_type = Column(String)  # index, percent, currency
    min_value = Column(Float)
    max_value = Column(Float)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, onupdate=func.now())

class IndicatorKeyword(Base):
    __tablename__ = "indicator_keywords"

    keyword_id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"))
    keyword = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    language = Column(String, default="en")

class IndicatorDependency(Base):
    __tablename__ = "indicator_dependencies"

    dependency_id = Column(Integer, primary_key=True, index=True)
    parent_indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"))
    child_indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"))
    weight = Column(Float, default=1.0)
    relationship_type = Column(String)  # correlation, causal, composite

class IndicatorThreshold(Base):
    __tablename__ = "indicator_thresholds"

    threshold_id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"))
    threshold_value = Column(Float, nullable=False)
    label = Column(String)  # low, medium, high, critical
    color_code = Column(String)
    severity_level = Column(Integer)
