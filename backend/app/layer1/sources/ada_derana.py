import httpx
from bs4 import BeautifulSoup
from typing import List
import logging
from datetime import datetime
import re

from app.scrapers.base import BaseScraper
from app.models.raw_article import RawArticle

logger = logging.getLogger(__name__)

class AdaDeranaScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_id=1, # Assuming 1 for Ada Derana based on blueprint
            source_name="Ada Derana",
            base_url="http://www.adaderana.lk"
        )
        self.news_url = "https://www.adaderana.lk/hot-news/"

    async def fetch_articles(self) -> List[RawArticle]:
        articles = []
        async with httpx.AsyncClient(follow_redirects=True) as client:
            logger.info(f"Fetching news list from {self.news_url}")
            try:
                response = await client.get(self.news_url, timeout=30.0)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Find news items - typically in 'news-story' divs or similar
                # Inspecting typical structure (based on blueprint knowledge/assumption)
                # Blueprint says: "div.news-item" or similar. 
                # Let's try a generic approach for the list if exact selector isn't known, 
                # but usually it's .news-story or .story-text
                
                # Looking for links that look like news articles
                # Pattern: http://www.adaderana.lk/news/(\d+)/...
                
                news_links = set()
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '/news/' in href and 'adaderana.lk' in href:
                         news_links.add(href)
                    elif href.startswith('news.php?nid='): # Old style or internal
                         news_links.add(f"{self.base_url}/{href}")

                logger.info(f"Found {len(news_links)} potential article links")
                
                # Process all found articles
                for link in list(news_links):
                    try:
                        article = await self._process_article(client, link)
                        if article:
                            articles.append(article)
                    except Exception as e:
                        logger.error(f"Failed to process {link}: {e}")
                        
            except Exception as e:
                logger.error(f"Error fetching news list: {e}")
                
        return articles

    async def _process_article(self, client: httpx.AsyncClient, url: str) -> RawArticle:
        logger.info(f"Processing article: {url}")
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract Title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        
        # Extract Body
        # Try common containers
        body_content = ""
        news_content_div = soup.find('div', class_='news-content') # Common in Ada Derana
        if news_content_div:
            body_content = news_content_div.get_text(strip=True, separator='\n')
        else:
            # Fallback
            p_tags = soup.find_all('p')
            body_content = "\n".join([p.get_text(strip=True) for p in p_tags if len(p.get_text(strip=True)) > 50])

        # Extract Date
        # Usually in <p class="news-date"> or similar
        publish_date = None
        date_str = ""
        date_tag = soup.find('p', class_='news-datestamp')
        if date_tag:
            date_str = date_tag.get_text(strip=True)
            # Parse date if possible, e.g., "November 29, 2025 10:30 am"
            try:
                # Cleanup "Published: " prefix if exists
                date_str = date_str.replace("Published:", "").strip()
                # Simple parser or just keep string for now in metadata if parsing fails
                # publish_date = datetime.strptime(date_str, "%B %d, %Y %I:%M %p") 
                pass
            except:
                pass

        # Extract Images
        images = []
        if news_content_div:
            img_tags = news_content_div.find_all('img')
            for img in img_tags:
                src = img.get('src')
                if src:
                    images.append({"url": src})

        # Extract ID from URL
        # http://www.adaderana.lk/news/103986/sri-lanka-to...
        article_id = "adaderana_unknown"
        match = re.search(r'news/(\d+)', url)
        if match:
            article_id = f"adaderana_{match.group(1)}"
        
        return self.create_article(
            article_id=article_id,
            url=url,
            title=title,
            body=body_content,
            publish_date=publish_date, # Can be None
            images=images,
            metadata={"original_date_str": date_str}
        )
