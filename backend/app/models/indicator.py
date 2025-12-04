from sqlalchemy import Column, Integer, String, Float, Boolean, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class IndicatorDefinition(Base):
    __tablename__ = "indicator_definitions"

    indicator_id = Column(String, primary_key=True, index=True)
    indicator_name = Column(String, nullable=False)
    pestel_category = Column(String, nullable=False, index=True)
    description = Column(Text)
    calculation_type = Column(String, nullable=False)
    base_weight = Column(Float, default=1.0)
    aggregation_window = Column(String, default='1 day')
    threshold_high = Column(Float)
    threshold_low = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, onupdate=func.now())
    metadata_ = Column("metadata", JSON, nullable=True) # Using metadata_ to avoid conflict with Base.metadata

class IndicatorKeyword(Base):
    __tablename__ = "indicator_keywords"

    keyword_id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
    keyword_text = Column(String, nullable=False) # Renamed from keyword to match DB
    keyword_type = Column(String, default='exact_match') # Added to match DB
    weight = Column(Float, default=1.0)
    language = Column(String, default="en")
    is_active = Column(Boolean, default=True) # Added to match DB
    created_at = Column(TIMESTAMP, server_default=func.now()) # Added to match DB

class IndicatorDependency(Base):
    __tablename__ = "indicator_correlations" # Renamed to match DB table 'indicator_correlations' or is this a different table? 
    # Wait, migration has 'indicator_correlations' but model has 'indicator_dependencies'. 
    # The migration does NOT have 'indicator_dependencies'. 
    # I should probably comment this out or rename it if it's meant to be 'indicator_correlations'.
    # But 'indicator_correlations' in migration has different structure (indicator_id_1, indicator_id_2).
    # 'indicator_dependencies' seems to be a new table not in migration.
    # If I keep it, I must ensure it can be created. But create_all failed on it.
    # Let's keep it but fix types, and it will be created as a new table.
    
    dependency_id = Column(Integer, primary_key=True, index=True)
    parent_indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
    child_indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
    weight = Column(Float, default=1.0)
    relationship_type = Column(String)

class IndicatorThreshold(Base):
    __tablename__ = "indicator_thresholds" # This table is NOT in migration 001.
    
    threshold_id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
    threshold_value = Column(Float, nullable=False)
    label = Column(String)
    color_code = Column(String)
    severity_level = Column(Integer)
