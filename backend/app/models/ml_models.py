"""SQLAlchemy models for ML classification"""
from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from app.db.base_class import Base

class MLClassificationResult(Base):
    __tablename__ = 'ml_classification_results'

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    predicted_indicators = Column(ARRAY(String(50)), nullable=False)
    confidence_scores = Column(JSONB, nullable=False)
    classification_method = Column(String(50), default='hybrid')
    processing_time_ms = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    extra_metadata = Column(JSONB)
