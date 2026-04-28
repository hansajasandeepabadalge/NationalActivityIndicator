"""Pydantic schemas for article validation and processing"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class ArticleMetadata(BaseModel):
    """Metadata associated with an article"""
    word_count: int
    reading_time_minutes: int
    has_images: bool
    view_count: int


class Article(BaseModel):
    """Base article schema matching mock data structure"""
    article_id: str
    title: str
    content: str
    summary: Optional[str] = None
    category: str  # PESTEL category
    source: str
    author: str
    published_at: datetime
    language: str = "en"
    url: str
    metadata: ArticleMetadata

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid = ['Political', 'Economic', 'Social', 'Technological', 'Environmental', 'Legal']
        if v not in valid:
            raise ValueError(f'Category must be one of {valid}')
        return v

    @field_validator('published_at', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class ProcessedArticle(Article):
    """Article with additional processing metadata"""
    cleaned_content: str
    word_count: int
    sentiment_score: Optional[float] = None
    assigned_indicators: Optional[List[str]] = Field(default_factory=list)
