"""SQLAlchemy model for article-indicator mappings"""

from sqlalchemy import Column, String, Integer, Float, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from app.db.session import Base


class ArticleIndicatorMapping(Base):
    """Maps articles to indicators with confidence scores from classification"""
    __tablename__ = 'article_indicator_mappings'

    mapping_id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(100), nullable=False, index=True)
    indicator_id = Column(String(50), ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), nullable=False)

    # Classification details
    match_confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    classification_method = Column(String(50), default='rule_based')  # rule_based, ml, hybrid
    matched_keywords = Column(ARRAY(String(200)))
    keyword_match_count = Column(Integer, default=0)

    # Context
    article_category = Column(String(50))  # Original PESTEL category
    article_published_at = Column(TIMESTAMP(timezone=True))

    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    extra_metadata = Column(JSONB)
