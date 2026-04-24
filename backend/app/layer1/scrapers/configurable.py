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

from app.scrapers.base import BaseScraper
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
        """
        Extract article links from list page.
        
        Uses article_link_selector if provided, otherwise falls back to
        pattern matching on all links.
        """
        links = set()
        
        # Method 1: Use CSS selector if provided
        link_selector = self.selectors.get('article_link_selector')
        if link_selector:
            for a in soup.select(link_selector):
                href = a.get('href')
                if href:
                    full_url = self._make_absolute_url(href, base_url)
                    if full_url:
                        links.add(full_url)
        
        # Method 2: Use pattern matching on all links
        pattern = self.selectors.get('article_link_pattern')
        if pattern and not links:
            regex = re.compile(pattern)
            for a in soup.find_all('a', href=True):
                href = a['href']
                if regex.search(href):
                    full_url = self._make_absolute_url(href, base_url)
                    if full_url:
                        links.add(full_url)
        
        # Method 3: Fallback - look for links with meaningful text
        if not links:
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                # Heuristic: links with 5+ word text are likely articles
                if len(text.split()) >= 5 and not any(x in href.lower() for x in ['login', 'signup', 'contact', 'about']):
                    full_url = self._make_absolute_url(href, base_url)
                    if full_url and self.config.base_url in full_url:
                        links.add(full_url)
        
        return list(links)

    def _make_absolute_url(self, href: str, base_url: str) -> Optional[str]:
        """Convert relative URL to absolute."""
        if not href:
            return None
            
        # Already absolute
        if href.startswith('http'):
            return href
            
        # Protocol-relative
        if href.startswith('//'):
            return 'https:' + href
            
        # Root-relative
        if href.startswith('/'):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{href}"
            
        # Relative
        return base_url.rstrip('/') + '/' + href.lstrip('/')

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
        """
        Extract text using CSS selector(s).

        Supports:
        - Single selector string: "h1.title"
        - Comma-separated selectors: "h1, .title, #heading"
        - List of selectors (priority order): ["h1.title", "h1", "meta[property='og:title']"]
        - Meta tag extraction: Automatically tries og:title, twitter:title as fallback
        """
        if not selector:
            return None

        # Convert to list for uniform processing
        selectors = []
        if isinstance(selector, list):
            selectors = selector
        elif isinstance(selector, str):
            # Split comma-separated selectors
            selectors = [s.strip() for s in selector.split(',')]
        else:
            return None

        # Try each selector in order
        for sel in selectors:
            try:
                # Check if it's a meta tag selector
                if sel.startswith('meta['):
                    meta = soup.select_one(sel)
                    if meta:
                        content = meta.get('content')
                        if content:
                            return content.strip()
                else:
                    element = soup.select_one(sel)
                    if element:
                        text = element.get_text(strip=True)
                        if text:
                            return text
            except Exception as e:
                logger.debug(f"Selector '{sel}' failed: {e}")

        # Fallback: Try common meta tags for title/description
        if 'title' in str(selector).lower():
            for meta_sel in ["meta[property='og:title']", "meta[name='twitter:title']", "title"]:
                try:
                    elem = soup.select_one(meta_sel)
                    if elem:
                        text = elem.get('content') if elem.name == 'meta' else elem.get_text(strip=True)
                        if text:
                            return text.strip()
                except:
                    pass

        return None

    def _extract_body(self, soup: BeautifulSoup) -> str:
        """
        Extract article body content with smart cleaning.

        Supports:
        - Multiple selector fallbacks (string or list)
        - Automatic removal of ads, scripts, styles
        - Paragraph-based text extraction
        - Meta description fallback
        """
        body_selector = self.selectors.get('body', 'article, .content, .article-body, main')
        exclude_selector = self.selectors.get('body_exclude')

        body_text = ""

        # Convert to list if needed
        selectors = [body_selector] if isinstance(body_selector, str) else body_selector

        # Try each selector
        for selector in selectors:
            for sel in (selector.split(',') if isinstance(selector, str) else [selector]):
                sel = sel.strip()
                try:
                    element = soup.select_one(sel)
                    if element:
                        # Clone to avoid modifying original
                        element = element.__copy__()

                        # Remove scripts, styles, ads
                        for tag in element.find_all(['script', 'style', 'noscript', 'iframe']):
                            tag.decompose()

                        # Remove excluded elements
                        if exclude_selector:
                            for excluded in element.select(exclude_selector):
                                excluded.decompose()

                        # Get text with paragraph separation
                        paragraphs = element.find_all(['p', 'div'])
                        if paragraphs:
                            body_text = '\n\n'.join([
                                p.get_text(strip=True)
                                for p in paragraphs
                                if len(p.get_text(strip=True)) > 20
                            ])
                        else:
                            body_text = element.get_text(strip=True, separator='\n')

                        if len(body_text) >= 100:
                            return body_text
                except Exception as e:
                    logger.debug(f"Body selector '{sel}' failed: {e}")

        # Fallback 1: Concatenate all meaningful paragraphs
        if len(body_text) < 100:
            all_paragraphs = soup.find_all('p')
            meaningful = [
                p.get_text(strip=True)
                for p in all_paragraphs
                if len(p.get_text(strip=True)) > 50
            ]
            body_text = '\n\n'.join(meaningful)

        # Fallback 2: Try meta description
        if len(body_text) < 100:
            meta_desc = soup.select_one("meta[property='og:description'], meta[name='description']")
            if meta_desc:
                body_text = meta_desc.get('content', '')

        return body_text

    def _extract_images(self, soup: BeautifulSoup) -> List[dict]:
        """
        Extract images from article with lazy-loading support.

        Supports:
        - Standard src attribute
        - Lazy loading: data-src, data-lazy-src, data-original
        - Srcset parsing
        - OpenGraph image fallback
        """
        images = []
        img_selector = self.selectors.get('image', 'article img, .content img')

        # Convert to list if needed
        selectors = [img_selector] if isinstance(img_selector, str) else img_selector

        try:
            for selector in selectors:
                for sel in (selector.split(',') if isinstance(selector, str) else [selector]):
                    for img in soup.select(sel.strip())[:5]:  # Limit to 5 images
                        # Try multiple src attributes (lazy loading support)
                        src = (img.get('src') or
                               img.get('data-src') or
                               img.get('data-lazy-src') or
                               img.get('data-original') or
                               img.get('data-lazy'))

                        # Try srcset if no src found
                        if not src:
                            srcset = img.get('srcset')
                            if srcset:
                                # Parse srcset and get first URL
                                src = srcset.split(',')[0].strip().split()[0]

                        if src and not src.startswith('data:'):  # Skip data URIs
                            # Make absolute URL
                            if not src.startswith('http'):
                                from urllib.parse import urljoin
                                src = urljoin(self.config.base_url, src)

                            images.append({
                                "url": src,
                                "alt": img.get('alt', '')
                            })

                    if images:  # Stop if we found images
                        break

                if images:
                    break

            # Fallback: Try OpenGraph image
            if not images:
                og_img = soup.select_one("meta[property='og:image']")
                if og_img:
                    src = og_img.get('content')
                    if src:
                        images.append({"url": src, "alt": "OpenGraph image"})

        except Exception as e:
            logger.debug(f"Image extraction failed: {e}")

        return images[:5]  # Final limit to 5

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime with enhanced format support.

        Supports:
        - Configured date format
        - ISO8601 / RFC2822
        - Relative dates ("2 hours ago", "yesterday")
        - Common date formats
        - Timezone handling
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Clean up common prefixes/suffixes
        date_str = re.sub(r'^(Published|Posted|Updated|Date|On):\s*', '', date_str, flags=re.IGNORECASE)
        date_str = re.sub(r'\s+(GMT|UTC|EST|PST).*$', '', date_str, flags=re.IGNORECASE)
        date_str = date_str.strip()

        # Handle relative dates
        relative_patterns = [
            (r'(\d+)\s*minutes?\s*ago', lambda m: datetime.utcnow() - __import__('datetime').timedelta(minutes=int(m.group(1)))),
            (r'(\d+)\s*hours?\s*ago', lambda m: datetime.utcnow() - __import__('datetime').timedelta(hours=int(m.group(1)))),
            (r'(\d+)\s*days?\s*ago', lambda m: datetime.utcnow() - __import__('datetime').timedelta(days=int(m.group(1)))),
            (r'yesterday', lambda m: datetime.utcnow() - __import__('datetime').timedelta(days=1)),
            (r'today', lambda m: datetime.utcnow()),
        ]

        for pattern, handler in relative_patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                try:
                    return handler(match)
                except:
                    pass

        # Try configured format first
        date_format = self.selectors.get('date_format')
        if date_format and date_format.lower() != 'iso8601':
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                pass

        # Try ISO8601 formats
        iso_formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",      # 2025-12-09T10:30:00.000Z
            "%Y-%m-%dT%H:%M:%SZ",         # 2025-12-09T10:30:00Z
            "%Y-%m-%dT%H:%M:%S",          # 2025-12-09T10:30:00
            "%Y-%m-%d %H:%M:%S",          # 2025-12-09 10:30:00
        ]

        for fmt in iso_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Try common formats
        common_formats = [
            "%B %d, %Y",              # December 9, 2025
            "%d %B %Y",               # 9 December 2025
            "%b %d, %Y",              # Dec 9, 2025
            "%d %b %Y",               # 9 Dec 2025
            "%Y-%m-%d",               # 2025-12-09
            "%d/%m/%Y",               # 09/12/2025
            "%m/%d/%Y",               # 12/09/2025
            "%B %d, %Y %I:%M %p",     # December 9, 2025 10:30 AM
            "%d-%m-%Y",               # 09-12-2025
            "%Y.%m.%d",               # 2025.12.09
            "%d.%m.%Y",               # 09.12.2025
        ]

        for fmt in common_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        logger.debug(f"Could not parse date: {date_str}")
        return None

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
