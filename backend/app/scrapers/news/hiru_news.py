"""
Hiru News Scraper

Scrapes news from hirunews.lk (Sinhala/English news)
"""

import httpx
from bs4 import BeautifulSoup
from typing import List
import logging
from datetime import datetime
import re

from app.scrapers.base import BaseScraper
from app.models.raw_article import RawArticle

logger = logging.getLogger(__name__)


class HiruNewsScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_id=3,
            source_name="Hiru News",
            base_url="https://hirunews.lk"  # Note: no www
        )
        # Correct URL pattern for news listing
        self.news_url = "https://hirunews.lk/news_listing.php?category=General"
    
    async def fetch_articles(self) -> List[RawArticle]:
        articles = []
        async with httpx.AsyncClient(follow_redirects=True) as client:
            logger.info(f"Fetching news list from {self.news_url}")
            try:
                response = await client.get(self.news_url, timeout=30.0)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Find article links - pattern: hirunews.lk/ARTICLE_ID/title
                news_links = set()
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    # Hiru News article pattern: https://hirunews.lk/123456/title-slug
                    if re.search(r'hirunews\.lk/\d+/', href):
                        news_links.add(href)
                    elif href.startswith('/') and re.match(r'/\d+/', href):
                        full_url = f"{self.source_info.url}{href}"
                        news_links.add(full_url)
                
                logger.info(f"Found {len(news_links)} potential article links")
                
                # Process first 15 articles
                for link in list(news_links)[:15]:
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
        title_tag = soup.find('h1') or soup.find('h2', class_='title')
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        
        # Extract Body
        body_content = ""
        # Try common Hiru News containers
        content_div = (
            soup.find('div', class_='news-content') or 
            soup.find('div', class_='article-content') or
            soup.find('div', class_='news-details') or
            soup.find('article')
        )
        if content_div:
            body_content = content_div.get_text(strip=True, separator='\n')
        else:
            # Fallback
            p_tags = soup.find_all('p')
            body_content = "\n".join([p.get_text(strip=True) for p in p_tags if len(p.get_text(strip=True)) > 30])
        
        # Extract Date
        publish_date = None
        date_tag = soup.find('span', class_='date') or soup.find('time')
        date_str = date_tag.get_text(strip=True) if date_tag else ""
        
        # Extract Images
        images = []
        img_tags = soup.find_all('img', src=True)
        for img in img_tags[:3]:
            src = img.get('src')
            if src and not ('logo' in src.lower() or 'icon' in src.lower()):
                if not src.startswith('http'):
                    src = f"{self.source_info.url}{src}"
                images.append({"url": src})
        
        # Extract ID from URL - pattern: hirunews.lk/123456/title
        article_id = "hirunews_unknown"
        match = re.search(r'hirunews\.lk/(\d+)', url)
        if match:
            article_id = f"hirunews_{match.group(1)}"
        
        return self.create_article(
            article_id=article_id,
            url=url,
            title=title,
            body=body_content,
            publish_date=publish_date,
            images=images,
            metadata={"original_date_str": date_str}
        )
