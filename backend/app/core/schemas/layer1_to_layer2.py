"""
Cross-Layer Data Contracts for Layer 1 -> Layer 2 Interoperability

This module enforces strict data schemas that outputting agents in Layer 1
must adhere to, and data ingestion processes in Layer 2 must receive.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProcessedArticleContract(BaseModel):
    """
    STRICT Data Contract: Ensures Layer 1 output aligns exactly with Layer 2 expectations.
    
    Any article fetched from MongoDB (Layer 1's output store) must deserialize into this
    safely without errors. If it fails, there is an integration mismatch!
    """
    article_id: str = Field(..., description="Unique identifier for the scraped article")
    title: str = Field(..., min_length=5, description="Article heading (Must not be empty)")
    body: str = Field(..., min_length=20, description="Main text body (Must not be empty)")
    source: str = Field(..., description="Source origin (e.g., Ada Derana)")
    url: str = Field(..., description="Original URL")
    
    # Normalizations
    published_at: Optional[datetime] = Field(None, description="ISO-8601 formatted date")
    language: str = Field(default="en", description="ISO 639-1 language code")
    
    # Layer 1 Metrics explicitly carried over
    layer1_quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    layer1_categories: List[str] = Field(default_factory=list)
    layer1_entities: List[str] = Field(default_factory=list)

    model_config = ConfigDict(
        # We can accept extra fields without crashing, but only explicitly defined ones
        # are mapped cleanly for Layer 2. Strip excess.
        extra="ignore"
    )

    @field_validator("title", "body", mode="before")
    @classmethod
    def prevent_empty_strings(cls, v: Any) -> Any:
        """Double-check that critical strings aren't functionally empty blanks"""
        if isinstance(v, str) and not v.strip():
            raise ValueError("Field cannot be solely whitespace.")
        return v
