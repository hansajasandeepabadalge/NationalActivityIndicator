"""
Universal Configurable Scraper

A flexible scraper that reads CSS selectors from the database (SourceConfig)
and can scrape any website without writing custom code.

Usage:
    1. Add a SourceConfig row with selectors JSON
    2. The scraper automatically uses those selectors to extract content

Selectors JSON format:
{
    "list_url": "https://example.com/news",           # Page with article links
    "article_link_pattern": "/news/\\d+",             # Regex to match article URLs
    "article_link_selector": "a.article-link",        # CSS selector for article links (optional)
    "title": "h1.article-title",                      # CSS selector for title
    "body": "div.article-content",                    # CSS selector for body
    "body_exclude": ".advertisement, .related-news",  # Exclude these from body (optional)
    "date": "span.publish-date",                      # CSS selector for date
    "date_format": "%B %d, %Y",                       # Date format (optional)
    "author": "span.author-name",                     # CSS selector for author (optional)
    "image": "div.article-content img",               # CSS selector for images (optional)
    "pagination": "a.next-page"                       # Pagination selector (optional)
}
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import re
import asyncio

from app.layer1.scrapers.base import BaseScraper
from app.layer1.scrapers.parsers import (
    extract_article_links, make_absolute_url,
    extract_text, extract_body,
    parse_date, extract_images,
)
from app.models.raw_article import RawArticle
from app.models.agent_models import SourceConfig
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class ConfigurableScraper(BaseScraper):
    """
    Universal scraper that reads configuration from database.
    
    Can scrape any website by providing CSS selectors in the
    SourceConfig.selectors JSONB field.
    """
    
    def __init__(self, source_config: SourceConfig):
        """
        Initialize with a SourceConfig object from the database.
        
        Args:
            source_config: SourceConfig model instance with selectors
        """
        super().__init__(
            source_id=source_config.id,
            source_name=source_config.display_name or source_config.name,
            base_url=source_config.base_url
        )
        
        self.config = source_config
        self.selectors = source_config.get_selectors()
        self.rate_limit = source_config.rate_limit_requests or 10
        self.rate_period = source_config.rate_limit_period or 60
        
        # Request tracking for rate limiting
        self._request_times: List[float] = []
        
        logger.info(f"ConfigurableScraper initialized for {source_config.name}")
        logger.debug(f"Selectors: {self.selectors}")

    @classmethod
    def from_source_name(cls, source_name: str) -> Optional['ConfigurableScraper']:
        """
        Create scraper from source name by looking up database config.
        
        Args:
            source_name: The source_name field in source_configs table
            
        Returns:
            ConfigurableScraper instance or None if not found
        """
        try:
            db = SessionLocal()
            config = db.query(SourceConfig).filter(
                SourceConfig.source_name == source_name,
                SourceConfig.is_active == True
            ).first()
            db.close()
            
            if config:
                return cls(config)
            else:
                logger.warning(f"No active SourceConfig found for: {source_name}")
                return None
        except Exception as e:
            logger.error(f"Error loading config for {source_name}: {e}")
            return None

    async def _rate_limit_wait(self):
        """Implement rate limiting."""
        now = datetime.utcnow().timestamp()
        
        # Remove old request times
        self._request_times = [
            t for t in self._request_times 
            if now - t < self.rate_period
        ]
        
        # Check if we need to wait
        if len(self._request_times) >= self.rate_limit:
            oldest = min(self._request_times)
            wait_time = self.rate_period - (now - oldest)
            if wait_time > 0:
                logger.debug(f"Rate limiting: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self._request_times.append(now)

    async def fetch_articles(self) -> List[RawArticle]:
        """
        Fetch articles using configurable selectors.
        
        Returns:
            List of RawArticle objects
        """
        articles = []
        list_url = self.selectors.get('list_url') or self.config.base_url
        
        logger.info(f"Fetching articles from {list_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        async with httpx.AsyncClient(
            follow_redirects=True, 
            headers=headers,
            timeout=30.0
        ) as client:
            try:
                await self._rate_limit_wait()
                response = await client.get(list_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Find article links
                article_links = self._extract_article_links(soup, list_url)
                logger.info(f"Found {len(article_links)} article links")
                
                # Process each article
                for link in article_links[:20]:  # Limit to 20 articles per run
                    try:
                        await self._rate_limit_wait()
                        article = await self._process_article(client, link)
                        if article:
                            articles.append(article)
                    except Exception as e:
                        logger.error(f"Failed to process {link}: {e}")
                        
            except Exception as e:
                logger.error(f"Error fetching article list from {list_url}: {e}")
                
        logger.info(f"Successfully scraped {len(articles)} articles from {self.config.name}")
        return articles

    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Delegate to parsers.link_extractor."""
        return extract_article_links(soup, base_url, self.selectors, self.config.base_url)

    def _make_absolute_url(self, href: str, base_url: str) -> Optional[str]:
        """Delegate to parsers.link_extractor."""
        return make_absolute_url(href, base_url)

    async def _process_article(self, client: httpx.AsyncClient, url: str) -> Optional[RawArticle]:
        """
        Process individual article page.
        
        Args:
            client: HTTP client
            url: Article URL
            
        Returns:
            RawArticle or None if extraction fails
        """
        logger.debug(f"Processing article: {url}")
        
        try:
            response = await client.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract title
        title = self._extract_text(soup, self.selectors.get('title', 'h1'))
        if not title:
            logger.warning(f"No title found for {url}")
            title = "No Title"
        
        # Extract body
        body = self._extract_body(soup)
        if not body or len(body) < 100:
            logger.warning(f"Insufficient body content for {url}")
            return None
        
        # Extract date
        date_str = self._extract_text(soup, self.selectors.get('date'))
        publish_date = self._parse_date(date_str)
        
        # Extract author
        author = self._extract_text(soup, self.selectors.get('author'))
        
        # Extract images
        images = self._extract_images(soup)
        
        # Generate article ID
        article_id = self._generate_article_id(url)
        
        return self.create_article(
            article_id=article_id,
            url=url,
            title=title,
            body=body,
            publish_date=publish_date,
            author=author,
            images=images,
            metadata={
                "original_date_str": date_str,
                "source_config": self.config.name,
                "language": self.config.language
            }
        )

    def _extract_text(self, soup: BeautifulSoup, selector: Optional[str | list]) -> Optional[str]:
        """Delegate to parsers.content_parser."""
        return extract_text(soup, selector)

    def _extract_body(self, soup: BeautifulSoup) -> str:
        """Delegate to parsers.content_parser."""
        return extract_body(soup, self.selectors)

    def _extract_images(self, soup: BeautifulSoup) -> List[dict]:
        """Delegate to parsers.image_extractor."""
        return extract_images(soup, self.selectors, self.config.base_url)

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Delegate to parsers.date_parser."""
        return parse_date(date_str, self.selectors)

    def _generate_article_id(self, url: str) -> str:
        """Generate unique article ID from URL."""
        import hashlib
        
        # Try to extract numeric ID from URL
        numeric_match = re.search(r'/(\d{4,})', url)
        if numeric_match:
            return f"{self.config.name}_{numeric_match.group(1)}"
        
        # Fallback to URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"{self.config.name}_{url_hash}"


# ==============================================
# Factory function for easy instantiation
# ==============================================

def get_configurable_scraper(source_name: str) -> Optional[ConfigurableScraper]:
    """
    Get a ConfigurableScraper for the given source name.
    
    Args:
        source_name: Name of the source in source_configs table
        
    Returns:
        ConfigurableScraper instance or None
    """
    return ConfigurableScraper.from_source_name(source_name)


def get_all_configurable_sources() -> List[str]:
    """
    Get list of all source names that use ConfigurableScraper.
    
    Returns:
        List of source names
    """
    try:
        db = SessionLocal()
        configs = db.query(SourceConfig).filter(
            SourceConfig.is_active == True,
            SourceConfig.scraper_class == 'ConfigurableScraper'
        ).all()
        db.close()
        return [c.source_name for c in configs]
    except Exception as e:
        logger.error(f"Error getting configurable sources: {e}")
        return []
