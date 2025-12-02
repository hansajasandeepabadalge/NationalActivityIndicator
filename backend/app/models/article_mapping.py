from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base_class import Base

class ArticleIndicatorMapping(Base):
    __tablename__ = "article_indicator_mappings"

    mapping_id = Column(Integer, primary_key=True, index=True)
    article_id = Column(String, nullable=False, index=True) # References MongoDB or external ID
    indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"), nullable=False)
    match_confidence = Column(Float, nullable=False)
    match_type = Column(String) # keyword, ml, rule_based
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Optional: Store snippet or context that triggered the match
    match_context = Column(String)
