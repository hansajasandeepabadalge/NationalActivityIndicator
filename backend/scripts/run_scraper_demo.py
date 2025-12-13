"""
Ada Derana Scraper Demo

Run this script to see the web scraper in action:
    python scripts/run_scraper_demo.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.news.ada_derana import AdaDeranaScraper


async def main():
    print("\n" + "=" * 60)
    print("         ADA DERANA WEB SCRAPER DEMO")
    print("=" * 60)
    print("\nConnecting to adaderana.lk...")
    
    scraper = AdaDeranaScraper()
    articles = await scraper.fetch_articles()
    
    print(f"\n✅ Scraped {len(articles)} articles!\n")
    print("=" * 60)
    
    # Show first 10 articles
    for i, article in enumerate(articles[:10], 1):
        print(f"\n{'─' * 50}")
        print(f"📰 Article {i}")
        print(f"{'─' * 50}")
        print(f"ID:    {article.article_id}")
        print(f"Title: {article.raw_content.title}")
        print(f"URL:   {article.raw_content.url}")
        
        # Show body preview (first 200 chars)
        body = article.raw_content.body
        if body and len(body) > 200:
            body = body[:200] + "..."
        print(f"\nContent Preview:\n{body}")
    
    print("\n" + "=" * 60)
    print(f"Total articles scraped: {len(articles)}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
