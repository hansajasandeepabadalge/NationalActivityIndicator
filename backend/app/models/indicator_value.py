"""
Developer B's additional indicator value models.

NOTE: IndicatorValue and IndicatorEvent are defined in indicator_models.py (Developer A).
This file only contains additional/alternative models.

For IndicatorTrend, use TrendAnalysis from analysis_models.py instead.
"""
from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.base_class import Base


# IndicatorTrend is an alias to TrendAnalysis for backward compatibility
# Import the canonical version from analysis_models
try:
    from app.models.analysis_models import TrendAnalysis as IndicatorTrend
except ImportError:
    # Fallback definition if analysis_models not available
    class IndicatorTrend(Base):
        """
        Alias for TrendAnalysis - use TrendAnalysis from analysis_models.py instead.
        """
        __tablename__ = "trend_analysis"
        __table_args__ = {'extend_existing': True}  # Allow if already defined
        
        analysis_id = Column(Integer, primary_key=True, index=True)
        indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
        analysis_date = Column(TIMESTAMP, nullable=False)
        trend_direction = Column(String)  # rising, falling, stable
