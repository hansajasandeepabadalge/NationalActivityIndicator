import ftfy
import re
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import Optional, TYPE_CHECKING

from app.models.raw_article import RawArticle
from app.models.processed_article import ProcessedArticle, ProcessedContent, ExtractionMetadata, ProcessingPipelineStatus, QualityMetrics

# Import reputation tracker for credibility scoring
try:
    from app.cross_validation.source_reputation import SourceReputationTracker
    HAS_REPUTATION_TRACKER = True
except ImportError:
    HAS_REPUTATION_TRACKER = False
    SourceReputationTracker = None

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Data cleaning pipeline for Layer 1.
    
    Cleans raw articles and calculates quality metrics including:
    - Credibility scoring using SourceReputationTracker
    - Content quality based on structure and completeness
    - Word count validation
    """
    
    def __init__(self, reputation_tracker: Optional['SourceReputationTracker'] = None):
        """
        Initialize DataCleaner with optional reputation tracker.
        
        Args:
            reputation_tracker: Optional SourceReputationTracker for credibility scoring.
                               If not provided, a new instance is created when available.
        """
        if reputation_tracker is not None:
            self.reputation_tracker = reputation_tracker
        elif HAS_REPUTATION_TRACKER:
            self.reputation_tracker = SourceReputationTracker()
        else:
            self.reputation_tracker = None
            logger.warning("SourceReputationTracker not available - using default credibility scores")

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
    
    def _calculate_content_quality_score(
        self, 
        title: str, 
        body: str, 
        author: Optional[str] = None,
        publish_date: Optional[datetime] = None
    ) -> float:
        """
        Calculate content quality score based on structure and completeness.
        
        Based on blueprint's Content Quality Score formula:
        - Word count (longer = more detailed): sigmoid(word_count / 500)
        - Structure completeness bonuses
        
        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        
        # Word count score using sigmoid function
        word_count = len(body.split())
        # sigmoid: 1 / (1 + exp(-x)) normalized around 500 words
        import math
        word_score = 1 / (1 + math.exp(-(word_count - 250) / 100))
        score += word_score * 0.40  # Weight: 40%
        
        # Structure completeness bonuses (max 0.45)
        structure_score = 0.0
        if title and len(title) > 10:  # Has headline
            structure_score += 0.15
        if author:  # Has byline
            structure_score += 0.10
        if publish_date:  # Has timestamp
            structure_score += 0.10
        if word_count >= 100:  # Has substantial content
            structure_score += 0.10
        score += structure_score
        
        # Ensure score is between 0 and 1
        return min(1.0, max(0.0, score))
    
    def _calculate_credibility_score(
        self, 
        source_name: str, 
        content_quality_score: float
    ) -> float:
        """
        Calculate final credibility score using multi-factor scoring.
        
        Based on blueprint formula:
        Final_Credibility_Score = 
            (Source_Base_Score × 0.40) +
            (Content_Quality_Score × 0.25) +
            (Cross_Verification_Score × 0.20) +
            (Author_Reputation_Score × 0.10) +
            (Timeliness_Score × 0.05)
        
        For Iteration 1, we implement:
        - Source Base Score (from reputation tracker)
        - Content Quality Score (calculated above)
        
        Returns:
            Score from 0.0 to 1.0
        """
        # Get source reputation score
        if self.reputation_tracker:
            reputation_score = self.reputation_tracker.get_reputation_score(source_name)
            source_base_score = reputation_score / 100.0  # Normalize to 0-1
        else:
            # Default to Tier 2 baseline (0.75) if no tracker
            source_base_score = 0.75
        
        # Apply simplified weighting for Iteration 1
        # (Cross-verification, author reputation, timeliness = placeholders)
        credibility = (
            source_base_score * 0.50 +        # Source reputation
            content_quality_score * 0.35 +     # Content quality
            0.75 * 0.15                         # Placeholder for other factors
        )
        
        return min(1.0, max(0.0, credibility))

    def process_article(self, raw_article: RawArticle) -> ProcessedArticle:
        logger.info(f"Cleaning article: {raw_article.article_id}")
        
        # Clean Title
        clean_title = self.clean_text(raw_article.raw_content.title)
        
        # Clean Body
        # If body is HTML, clean it. If it's already text (from scraper), just normalize.
        clean_body = self.clean_text(raw_article.raw_content.body)
        
        # Detect language (basic detection for now)
        language = "en"  # Default to English
        try:
            # Try to detect if primarily Sinhala or Tamil characters
            sinhala_range = range(0x0D80, 0x0DFF)
            tamil_range = range(0x0B80, 0x0BFF)
            text_sample = (clean_title + " " + clean_body[:200])
            
            sinhala_count = sum(1 for c in text_sample if ord(c) in sinhala_range)
            tamil_count = sum(1 for c in text_sample if ord(c) in tamil_range)
            
            if sinhala_count > len(text_sample) * 0.1:
                language = "si"
            elif tamil_count > len(text_sample) * 0.1:
                language = "ta"
        except Exception:
            pass  # Keep default English
        
        # Create Processed Content
        content = ProcessedContent(
            title_original=clean_title,
            body_original=clean_body,
            language_original=language
        )
        
        # Extraction Metadata
        extraction = ExtractionMetadata(
            publish_timestamp=raw_article.raw_content.publish_date,
            author=raw_article.raw_content.author
        )
        
        # Calculate quality scores
        word_count = len(clean_body.split())
        content_quality = self._calculate_content_quality_score(
            title=clean_title,
            body=clean_body,
            author=raw_article.raw_content.author,
            publish_date=raw_article.raw_content.publish_date
        )
        
        # Get source name for credibility calculation
        source_name = raw_article.source.name if hasattr(raw_article.source, 'name') else "Unknown"
        credibility = self._calculate_credibility_score(source_name, content_quality)
        
        # Build quality flags
        quality_flags = []
        if word_count < 50:
            quality_flags.append("short_content")
        if not raw_article.raw_content.author:
            quality_flags.append("missing_author")
        if credibility < 0.5:
            quality_flags.append("low_credibility")
        
        # Quality Metrics with calculated credibility
        quality = QualityMetrics(
            is_clean=True,
            credibility_score=round(credibility, 3),
            quality_flags=quality_flags
        )
            
        # Pipeline Status
        pipeline = ProcessingPipelineStatus(
            stages_completed=["cleaning"],
            last_updated=datetime.utcnow(),
            processing_version="1.1.0"  # Updated version
        )
        
        logger.debug(
            f"Article {raw_article.article_id}: "
            f"source={source_name}, credibility={credibility:.3f}, "
            f"content_quality={content_quality:.3f}, word_count={word_count}"
        )
        
        return ProcessedArticle(
            article_id=raw_article.article_id,
            content=content,
            extraction=extraction,
            processing_pipeline=pipeline,
            quality=quality
        )

