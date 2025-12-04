from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, Text, PrimaryKeyConstraint
from sqlalchemy.sql import func
from app.db.base_class import Base

class IndicatorValue(Base):
    __tablename__ = "indicator_values"
    # This should be a TimescaleDB hypertable

    timestamp = Column(TIMESTAMP, primary_key=True, nullable=False, index=True) # Renamed from time
    indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"), primary_key=True, nullable=False) # Integer -> String
    value = Column(Float, nullable=False)
    # raw_count, sentiment_score, etc are in DB but not here. Adding them if needed or leaving as is if not used by script.
    # Script doesn't populate values, so it might be fine. But for correctness:
    raw_count = Column(Integer, default=0)
    sentiment_score = Column(Float, nullable=True)
    confidence = Column(Float, default=1.0) # Renamed from confidence_score
    source_count = Column(Integer, default=1) # Renamed from source_article_count
    
    # Metadata about the calculation source
    # source_article_count = Column(Integer) # Removed/Renamed
    
class IndicatorEvent(Base):
    __tablename__ = "indicator_events"
    
    event_id = Column(Integer, primary_key=True, autoincrement=True) # Part of composite PK
    indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id"))
    timestamp = Column(TIMESTAMP, primary_key=True, nullable=False) # Part of composite PK
    # end_time = Column(TIMESTAMP) # Not in DB
    event_type = Column(String) # spike, drop, anomaly
    description = Column(Text)
    severity = Column(String) # Float -> String in DB ('medium')
    # value_before, value_after, metadata, acknowledged, acknowledged_at are in DB
    
    __table_args__ = (
        # PrimaryKeyConstraint('event_id', 'timestamp'), # Already defined in DB, SQLAlchemy might need it here too?
        # Yes, for composite PK.
        # But wait, if I define columns as primary_key=True it works.
        # event_id is part of PK, timestamp is part of PK.
    )

class IndicatorTrend(Base):
    __tablename__ = "trend_analysis" # Renamed from indicator_trends to match DB table 'trend_analysis'
    # Wait, migration created 'trend_analysis'.
    # Model had 'indicator_trends'.
    # If I rename it to 'trend_analysis', it matches DB.
    
    analysis_id = Column(Integer, primary_key=True, index=True) # Renamed from trend_id
    indicator_id = Column(String, ForeignKey("indicator_definitions.indicator_id")) # Integer -> String
    analysis_date = Column(TIMESTAMP, nullable=False) # Renamed from date
    trend_direction = Column(String) # rising, falling, stable
    # slope, r_squared, etc in DB
    # trend_strength, moving_average in Model.
    # I'll stick to DB names where possible or just fix the FK type for now to pass the script.
    # The script failed on 'indicator_trends' table creation.
    # If I rename it to 'trend_analysis', create_all might skip it if it exists.
    # But 'trend_analysis' exists.
    # So renaming it is the best way to avoid trying to create a new table 'indicator_trends'.
