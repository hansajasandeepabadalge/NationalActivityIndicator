from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class SourceInfo(BaseModel):
    source_id: int
    name: str
    url: HttpUrl

class ScrapeMetadata(BaseModel):
    job_id: int
    scraped_at: datetime
    scraper_version: str

class RawContent(BaseModel):
    html: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    images: List[Dict[str, str]] = []
    metadata: Dict[str, Any] = {}

class ValidationStatus(BaseModel):
    is_valid: bool
    validation_errors: List[str] = []
    word_count: Optional[int] = None

class RawArticle(BaseModel):
    article_id: str
    source: SourceInfo
    scrape_metadata: ScrapeMetadata
    raw_content: RawContent
    validation: ValidationStatus

    model_config = {
        "populate_by_name": True,
    }
