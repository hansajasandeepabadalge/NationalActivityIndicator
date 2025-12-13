"""
Daily FT Scraper

Scrapes business and financial news from ft.lk
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


class DailyFTScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_id=2,
            source_name="Daily FT",
            base_url="https://www.ft.lk"
        )
        self.news_url = "https://www.ft.lk/news/56"
    
    async def fetch_articles(self) -> List[RawArticle]:
        articles = []
        async with httpx.AsyncClient(follow_redirects=True) as client:
            logger.info(f"Fetching news list from {self.news_url}")
            try:
                response = await client.get(self.news_url, timeout=30.0)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Find article links
                news_links = set()
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    # FT.lk article pattern: /category/id/title
                    if href.startswith('/') and re.search(r'/\d+/', href):
                        full_url = f"{self.base_url}{href}"
                        news_links.add(full_url)
                    elif 'ft.lk' in href and re.search(r'/\d+/', href):
                        news_links.add(href)
                
                logger.info(f"Found {len(news_links)} potential article links")
                
                # Process first 15 articles to avoid overloading
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
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        
        # Extract Body
        body_content = ""
        # Try common FT.lk containers
        content_div = soup.find('div', class_='inner-text') or soup.find('div', class_='news-content')
        if content_div:
            body_content = content_div.get_text(strip=True, separator='\n')
        else:
            # Fallback - get article paragraphs
            article_tag = soup.find('article')
            if article_tag:
                body_content = article_tag.get_text(strip=True, separator='\n')
            else:
                p_tags = soup.find_all('p')
                body_content = "\n".join([p.get_text(strip=True) for p in p_tags if len(p.get_text(strip=True)) > 50])
        
        # Extract Date
        publish_date = None
        date_tag = soup.find('span', class_='date') or soup.find('time')
        date_str = date_tag.get_text(strip=True) if date_tag else ""
        
        # Extract Images
        images = []
        img_tags = soup.find_all('img', src=True)
        for img in img_tags[:3]:  # Limit to 3 images
            src = img.get('src')
            if src and ('news' in src or 'article' in src):
                if not src.startswith('http'):
                    src = f"{self.base_url}{src}"
                images.append({"url": src})
        
        # Extract ID from URL
        article_id = "dailyft_unknown"
        match = re.search(r'/(\d+)/', url)
        if match:
            article_id = f"dailyft_{match.group(1)}"
        
        return self.create_article(
            article_id=article_id,
            url=url,
            title=title,
            body=body_content,
            publish_date=publish_date,
            images=images,
            metadata={"original_date_str": date_str}
        )
