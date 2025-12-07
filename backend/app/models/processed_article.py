"""
Processed Article Models

These models represent articles after they have been cleaned and processed
by the data cleaning pipeline. They are the output of Layer 1 processing
and the input for Layer 2+ analysis.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ProcessedContent(BaseModel):
    """Cleaned and normalized content from an article."""
    title_original: str = ""
    title_translated: Optional[str] = None
    body_original: str = ""
    body_translated: Optional[str] = None
    language_original: str = "en"
    language_detected: Optional[str] = None
    summary: Optional[str] = None


class ExtractionMetadata(BaseModel):
    """Metadata extracted during processing."""
    publish_timestamp: Optional[datetime] = None
    author: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    entities: Dict[str, List[str]] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)


class ProcessingPipelineStatus(BaseModel):
    """Tracks the status of processing through the pipeline."""
    stages_completed: List[str] = Field(default_factory=list)
    stages_failed: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    processing_version: str = "1.0.0"
    error_messages: List[str] = Field(default_factory=list)


class QualityMetrics(BaseModel):
    """Quality metrics for processed content."""
    is_clean: bool = True
    credibility_score: float = 1.0
    quality_flags: List[str] = Field(default_factory=list)
    word_count: Optional[int] = None
    reading_time_minutes: Optional[float] = None
    duplicate_score: Optional[float] = None
    duplicate_of: Optional[str] = None


class ProcessedArticle(BaseModel):
    """
    A fully processed article ready for Layer 2+ analysis.
    
    This represents the output of Layer 1 (AI Agents) processing
    and serves as the input for subsequent layers.
    """
    article_id: str
    content: ProcessedContent
    extraction: ExtractionMetadata = Field(default_factory=ExtractionMetadata)
    processing_pipeline: ProcessingPipelineStatus = Field(default_factory=ProcessingPipelineStatus)
    quality: QualityMetrics = Field(default_factory=QualityMetrics)
    
    # Optional cross-layer metadata
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    scraped_at: Optional[datetime] = None
    
    # Layer 2+ enrichment fields (populated by downstream processing)
    sentiment_score: Optional[float] = None
    indicator_mappings: List[str] = Field(default_factory=list)
    priority_score: Optional[float] = None
    business_impact_score: Optional[float] = None

    model_config = {
        "populate_by_name": True,
    }
