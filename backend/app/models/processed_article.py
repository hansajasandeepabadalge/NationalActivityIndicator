from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

class ProcessedContent(BaseModel):
    title_original: str
    title_english: Optional[str] = None
    body_original: str
    body_english: Optional[str] = None
    summary: Optional[str] = None
    language_original: Optional[str] = None
    translation_confidence: Optional[float] = None

class ExtractionMetadata(BaseModel):
    publish_timestamp: Optional[datetime] = None
    author: Optional[str] = None
    keywords_extracted: List[str] = []
    entities: Dict[str, List[str]] = {}

class ProcessingPipelineStatus(BaseModel):
    stages_completed: List[str] = []
    last_updated: datetime
    processing_version: str

class QualityMetrics(BaseModel):
    credibility_score: Optional[float] = None
    bias_indicator: Optional[str] = None
    is_clean: bool
    quality_flags: List[str] = []

class ProcessedArticle(BaseModel):
    article_id: str
    content: ProcessedContent
    extraction: ExtractionMetadata
    processing_pipeline: ProcessingPipelineStatus
    quality: QualityMetrics
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
