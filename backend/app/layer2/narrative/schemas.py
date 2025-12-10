"""Pydantic schemas for narrative generation"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NarrativeText(BaseModel):
    """Generated narrative for an indicator"""
    article_id: str
    indicator_id: str
    headline: str  # "📈 Economic Activity Surging"
    summary: str   # 2-3 sentences explaining the change
    emoji: str     # "📈", "📉", "⚠️", "🔥"
    confidence: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "article_id": "ART_001",
                "indicator_id": "ECO_CURRENCY_STABILITY",
                "headline": "📈 Currency Stability Strengthening",
                "summary": "Multiple currency mentions detected with large transaction amounts exceeding Rs. 1 billion. Economic indicators show positive momentum with 3.5% growth signals.",
                "emoji": "📈",
                "confidence": 0.78,
                "generated_at": "2025-12-03T10:30:00Z"
            }
        }
    }
