"""SQLAlchemy model for article-indicator mappings - Integrated version"""

from sqlalchemy import Column, String, Integer, Float, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func

from app.db.base_class import Base


class ArticleIndicatorMapping(Base):
    """
    Maps articles to indicators with confidence scores from classification.
    
    Combines features from both Developer A (comprehensive) and Developer B (simpler).
    """
    __tablename__ = 'article_indicator_mappings'

    mapping_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    article_id = Column(String(100), nullable=False, index=True)  # References MongoDB or external ID
    indicator_id = Column(String(50), ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), nullable=False)

    # Classification details (Developer A)
    match_confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    classification_method = Column(String(50), default='rule_based')  # rule_based, ml, hybrid (Developer A: classification_method)
    match_type = Column(String(50))  # keyword, ml, rule_based (Developer B: match_type - for backward compat)
    
    # Keyword matching details (Developer A)
    matched_keywords = Column(ARRAY(String(200)))
    keyword_match_count = Column(Integer, default=0)

    # Context fields
    article_category = Column(String(50))  # Original PESTEL category (Developer A)
    article_published_at = Column(TIMESTAMP(timezone=True))  # (Developer A)
    match_context = Column(Text)  # Snippet or context that triggered match (Developer B)

    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    extra_metadata = Column(JSONB)
