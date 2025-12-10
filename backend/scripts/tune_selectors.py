"""
Tune selectors for news_first and sunday_observer
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import httpx
from bs4 import BeautifulSoup
from app.models.agent_models import SourceConfig
from app.db.session import SessionLocal
from app.scrapers.configurable_scraper import ConfigurableScraper


async def inspect_site(url: str):
    """Fetch and analyze site HTML."""
    print(f"\n🔍 Inspecting: {url}")
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'lxml')

            # Find article links
            all_links = soup.find_all('a', href=True)
            article_links = [a['href'] for a in all_links if len(a.get_text(strip=True)) > 20][:10]

            print(f"✅ Found {len(all_links)} total links")
            print(f"📄 Sample article links:")
            for link in article_links[:5]:
                print(f"   {link}")

            return article_links
        except Exception as e:
            print(f"❌ Error: {e}")
            return []


async def test_source(source_name: str):
    """Test a source and show results."""
    print(f"\n{'='*80}")
    print(f"Testing: {source_name}")
    print('='*80)

    db = SessionLocal()
    config = db.query(SourceConfig).filter(
        SourceConfig.source_name == source_name
    ).first()

    if not config:
        print(f"❌ Not found")
        db.close()
        return

    print(f"Current selectors:")
    print(f"  list_url: {config.selectors.get('list_url')}")
    print(f"  article_link_pattern: {config.selectors.get('article_link_pattern')}")

    scraper = ConfigurableScraper(config)
    articles = await scraper.fetch_articles()

    print(f"\n✅ Scraped: {len(articles)} articles")
    if articles:
        for i, a in enumerate(articles[:3], 1):
            print(f"  [{i}] {a.raw_content.title[:60]}...")

    db.close()
    return len(articles)


async def update_selectors(source_name: str, new_selectors: dict):
    """Update source selectors."""
    db = SessionLocal()
    config = db.query(SourceConfig).filter(
        SourceConfig.source_name == source_name
    ).first()

    if config:
        current = config.selectors or {}
        current.update(new_selectors)
        config.selectors = current
        db.commit()
        print(f"✅ Updated {source_name} selectors")

    db.close()


async def main():
    print("="*80)
    print("🔧 SELECTOR TUNING: news_first & sunday_observer")
    print("="*80)

    # Test news_first
    count1 = await test_source('news_first')

    if count1 < 5:
        print(f"\n⚠️  news_first only got {count1} articles - updating selectors...")

        # Improved selectors for news_first
        await update_selectors('news_first', {
            'list_url': 'https://www.newsfirst.lk/',
            'article_link_pattern': r'/\d{4}/\d{2}/[\w-]+',
            'article_link_selector': 'h2.entry-title a, h3.entry-title a, div.td-module-title a',
        })

        print("🔄 Retesting with new selectors...")
        count1 = await test_source('news_first')

    # Test sunday_observer
    count2 = await test_source('sunday_observer')

    if count2 < 5:
        print(f"\n⚠️  sunday_observer only got {count2} articles - updating selectors...")

        # Improved selectors
        await update_selectors('sunday_observer', {
            'list_url': 'https://www.sundayobserver.lk/',
            'article_link_pattern': r'/(news|latest|article)/[\w-]+',
            'article_link_selector': 'h2 a, h3 a, div.article-title a, a.post-link',
        })

        print("🔄 Retesting...")
        count2 = await test_source('sunday_observer')

    # Summary
    print(f"\n{'='*80}")
    print("📊 RESULTS")
    print('='*80)
    print(f"news_first:       {count1} articles  {'✅ READY' if count1 >= 5 else '⚠️  NEEDS MORE WORK'}")
    print(f"sunday_observer:  {count2} articles  {'✅ READY' if count2 >= 5 else '⚠️  NEEDS MORE WORK'}")

    if count1 >= 5 and count2 >= 5:
        print(f"\n✅ Both sources ready for production!")
    else:
        print(f"\n⚠️  Further tuning needed")


if __name__ == "__main__":
    asyncio.run(main())
