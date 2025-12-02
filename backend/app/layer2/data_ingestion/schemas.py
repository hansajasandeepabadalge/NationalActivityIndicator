"""Pydantic schemas for article validation and processing"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
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

    @validator('category')
    def validate_category(cls, v):
        """Ensure category is a valid PESTEL category"""
        valid = ['Political', 'Economic', 'Social', 'Technological', 'Environmental', 'Legal']
        if v not in valid:
            raise ValueError(f'Category must be one of {valid}')
        return v

    @validator('published_at', pre=True)
    def parse_datetime(cls, v):
        """Parse datetime string to datetime object"""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class ProcessedArticle(Article):
    """Article with additional processing metadata"""
    cleaned_content: str
    word_count: int
    sentiment_score: Optional[float] = None
    assigned_indicators: Optional[list] = []
