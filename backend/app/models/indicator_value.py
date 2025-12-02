from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.base_class import Base

class IndicatorValue(Base):
    __tablename__ = "indicator_values"
    # This should be a TimescaleDB hypertable

    time = Column(TIMESTAMP, primary_key=True, nullable=False, index=True)
    indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"), primary_key=True, nullable=False)
    value = Column(Float, nullable=False)
    confidence_score = Column(Float)
    calculation_method = Column(String)
    
    # Metadata about the calculation source
    source_article_count = Column(Integer)
    
class IndicatorEvent(Base):
    __tablename__ = "indicator_events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"))
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    event_type = Column(String) # spike, drop, anomaly
    description = Column(Text)
    severity = Column(Float)

class IndicatorTrend(Base):
    __tablename__ = "indicator_trends"
    
    trend_id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"))
    date = Column(TIMESTAMP, nullable=False)
    trend_direction = Column(String) # rising, falling, stable
    trend_strength = Column(Float)
    moving_average_7d = Column(Float)
    moving_average_30d = Column(Float)
