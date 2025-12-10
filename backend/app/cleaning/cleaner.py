import ftfy
import re
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import Optional

from app.models.raw_article import RawArticle
from app.models.processed_article import ProcessedArticle, ProcessedContent, ExtractionMetadata, ProcessingPipelineStatus, QualityMetrics

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        # 1. Fix encoding issues (ftfy)
        text = ftfy.fix_text(text)
        
        # 2. Normalize whitespace
        text = " ".join(text.split())
        
        return text

    def clean_html(self, html_content: str) -> str:
        if not html_content:
            return ""
            
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'iframe', 'noscript', 'meta', 'link']):
            tag.decompose()
            
        # Get text
        text = soup.get_text(separator=' ')
        return self.clean_text(text)

    def process_article(self, raw_article: RawArticle) -> ProcessedArticle:
        logger.info(f"Cleaning article: {raw_article.article_id}")
        
        # Clean Title
        clean_title = self.clean_text(raw_article.raw_content.title)
        
        # Clean Body
        # If body is HTML, clean it. If it's already text (from scraper), just normalize.
        # Our Ada Derana scraper returns text in 'body', but let's be safe.
        clean_body = self.clean_text(raw_article.raw_content.body)
        
        # Create Processed Content
        content = ProcessedContent(
            title_original=clean_title,
            body_original=clean_body,
            language_original="en" # Defaulting to en for now, detection later
        )
        
        # Extraction Metadata
        extraction = ExtractionMetadata(
            publish_timestamp=raw_article.raw_content.publish_date,
            author=raw_article.raw_content.author
        )
        
        # Quality Metrics
        word_count = len(clean_body.split())
        quality = QualityMetrics(
            is_clean=True,
            credibility_score=1.0, # Placeholder
            quality_flags=[]
        )
        if word_count < 50:
            quality.quality_flags.append("short_content")
            
        # Pipeline Status
        pipeline = ProcessingPipelineStatus(
            stages_completed=["cleaning"],
            last_updated=datetime.utcnow(),
            processing_version="1.0.0"
        )
        
        return ProcessedArticle(
            article_id=raw_article.article_id,
            content=content,
            extraction=extraction,
            processing_pipeline=pipeline,
            quality=quality
        )
