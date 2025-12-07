from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import logging

from app.models.raw_article import RawArticle, SourceInfo, ScrapeMetadata, RawContent, ValidationStatus

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, source_id: int, source_name: str, base_url: str):
        self.source_info = SourceInfo(
            source_id=source_id,
            name=source_name,
            url=base_url
        )

    @abstractmethod
    async def fetch_articles(self) -> List[RawArticle]:
        """
        Fetch articles from the source.
        Returns a list of RawArticle objects.
        """
        pass

    def create_article(self, 
                       article_id: str, 
                       url: str, 
                       title: str, 
                       body: str, 
                       publish_date: Optional[datetime] = None,
                       author: Optional[str] = None,
                       images: List[dict] = [],
                       metadata: dict = {}) -> RawArticle:
        """
        Helper to create a RawArticle object with standard metadata.
        """
        return RawArticle(
            article_id=article_id,
            source=self.source_info,
            scrape_metadata=ScrapeMetadata(
                job_id=0,  # Placeholder, should be passed from job context
                scraped_at=datetime.utcnow(),
                scraper_version="1.0.0"
            ),
            raw_content=RawContent(
                html=None,
                title=title,
                body=body,
                author=author,
                publish_date=publish_date,
                images=images,
                metadata=metadata
            ),
            validation=ValidationStatus(
                is_valid=True, # Default to true, validate later
                word_count=len(body.split()) if body else 0
            )
        )

    async def run(self):
        """
        Main execution method.
        """
        logger.info(f"Starting scrape for {self.source_info.name}")
        try:
            articles = await self.fetch_articles()
            logger.info(f"Found {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"Error scraping {self.source_info.name}: {e}")
            raise
