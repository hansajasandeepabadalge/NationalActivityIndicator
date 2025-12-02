"""SQLAlchemy models for trend and correlation analysis"""
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.sql import func
from app.db.session import Base

class TrendAnalysis(Base):
    __tablename__ = 'trend_analysis'

    analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(String(50), ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), nullable=False)
    analysis_date = Column(Date, nullable=False)
    window_days = Column(Integer, default=30)
    trend_direction = Column(ENUM(
        'rising', 'falling', 'stable', 'volatile',
        name='trend_direction_enum', create_type=False
    ), nullable=False)
    slope = Column(Float)
    r_squared = Column(Float)
    volatility = Column(Float)
    change_percentage = Column(Float)
    forecast_7d = Column(Float)
    forecast_30d = Column(Float)
    confidence = Column(Float, default=0.5)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    metadata = Column(JSONB)
