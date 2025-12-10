from sqlalchemy import Column, String, Float, Integer, Boolean, Text, TIMESTAMP, ForeignKey, Date
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class EntityMaster(Base):
    __tablename__ = 'entity_master'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    canonical_name = Column(String(200), unique=True, nullable=False)
    entity_type = Column(String(50))  # PERSON, ORG, LOC, etc.
    aliases = Column(ARRAY(String))
    description = Column(Text)
    mention_count = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    article_mentions = relationship("ArticleEntity", back_populates="entity")

class ArticleEntity(Base):
    __tablename__ = 'article_entities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(100), ForeignKey('processed_articles.article_id', ondelete='CASCADE'), nullable=False)
    entity_id = Column(Integer, ForeignKey('entity_master.id', ondelete='CASCADE'), nullable=False)
    
    context = Column(Text)
    sentiment = Column(String(20))
    importance_score = Column(Integer)  # 0-100
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("ProcessedArticleModel", back_populates="entities")
    entity = relationship("EntityMaster", back_populates="article_mentions")

class TopicTrend(Base):
    __tablename__ = 'topic_trends'
    
    topic_name = Column(String(200), primary_key=True)
    date = Column(Date, primary_key=True)
    mention_count = Column(Integer, default=0)
    velocity = Column(Float)
    is_trending = Column(Boolean, default=False)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
