from sqlalchemy import Column, String, Float, Integer, Boolean, Text, TIMESTAMP, ForeignKey, Date
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class ProcessedArticleModel(Base):
    """
    SQLAlchemy model for processed articles (Layer 2).
    Enables structured storage of AI enrichments.
    """
    __tablename__ = 'processed_articles'

    article_id = Column(String(100), primary_key=True)
    title = Column(Text)
    source = Column(String(100))
    publish_date = Column(TIMESTAMP(timezone=True))
    
    # Layer 2 AI Enrichments
    classification_confidence = Column(Float)
    primary_category = Column(String(50))
    secondary_categories = Column(ARRAY(String))
    sub_themes = Column(ARRAY(String))
    urgency_level = Column(String(20))
    business_relevance = Column(Integer)
    classification_reasoning = Column(Text)
    
    sentiment_overall = Column(String(20))
    sentiment_score = Column(Float)
    business_confidence_impact = Column(Integer)
    public_mood = Column(Integer)
    economic_sentiment = Column(Integer)
    sentiment_drivers = Column(ARRAY(String))
    
    overall_quality_score = Column(Float)
    quality_band = Column(String(20))
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    entities = relationship("ArticleEntity", back_populates="article", cascade="all, delete-orphan")
