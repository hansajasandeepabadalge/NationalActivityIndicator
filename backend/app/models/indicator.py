"""
Developer B's additional indicator models.

NOTE: IndicatorDefinition and IndicatorKeyword are defined in indicator_models.py (Developer A).
This file only contains additional models not covered by Developer A.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.base_class import Base


class IndicatorDependency(Base):
    """
    Tracks dependencies between indicators (parent-child relationships).
    This is different from IndicatorCorrelation which tracks statistical correlations.
    """
    __tablename__ = "indicator_dependencies"  # Unique table name
    
    dependency_id = Column(Integer, primary_key=True, index=True)
    parent_indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
    child_indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
    weight = Column(Float, default=1.0)
    relationship_type = Column(String)  # e.g., 'derived_from', 'component_of', 'influenced_by'


class IndicatorThreshold(Base):
    """
    Custom thresholds for indicator alerts beyond the simple high/low in IndicatorDefinition.
    Supports multiple threshold levels with labels and severity.
    """
    __tablename__ = "indicator_thresholds"
    
    threshold_id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
    threshold_value = Column(Float, nullable=False)
    label = Column(String)  # e.g., 'critical', 'warning', 'normal'
    color_code = Column(String)  # e.g., '#ff0000'
    severity_level = Column(Integer)  # 1=lowest, 5=highest
