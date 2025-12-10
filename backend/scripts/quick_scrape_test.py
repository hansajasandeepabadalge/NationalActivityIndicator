"""
Quick scrape test - verify scraping and database storage works

Tests 2-3 sources to verify the enhanced scraper works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.scrapers.configurable_scraper import ConfigurableScraper
from app.models.agent_models import SourceConfig
from app.db.session import SessionLocal


async def quick_test():
    """Quick test of scraping."""

    # Test sources
    test_sources = ['ada_derana', 'daily_ft', 'the_island']

    print("="*80)
    print("🧪 QUICK SCRAPE TEST")
    print("="*80)

    db = SessionLocal()

    for source_name in test_sources:
        print(f"\n{'='*80}")
        print(f"Testing: {source_name}")
        print('='*80)

        try:
            # Get config
            config = db.query(SourceConfig).filter(
                SourceConfig.source_name == source_name,
                SourceConfig.is_active == True
            ).first()

            if not config:
                print(f"❌ Source not found: {source_name}")
                continue

            print(f"✅ Found config")
            print(f"   Display: {(config.config_metadata or {}).get('display_name', source_name)}")
            print(f"   URL: {config.base_url}")
            print(f"   Scraper: {config.scraper_class}")

            # Create scraper
            if config.scraper_class == 'AdaDeranaScraper':
                from app.scrapers.news.ada_derana import AdaDeranaScraper
                scraper = AdaDeranaScraper()
            else:
                scraper = ConfigurableScraper(config)

            print(f"\n⏳ Scraping...")
            articles = await scraper.fetch_articles()

            print(f"✅ Scraped {len(articles)} articles")

            if articles:
                # Show first article details
                article = articles[0]
                print(f"\n📄 First Article:")
                print(f"   ID: {article.article_id}")
                print(f"   Title: {article.raw_content.title[:80]}...")
                print(f"   URL: {article.raw_content.url}")
                print(f"   Body: {len(article.raw_content.body)} chars")
                print(f"   Author: {article.raw_content.author or 'N/A'}")
                print(f"   Date: {article.raw_content.publish_date or 'N/A'}")
                print(f"   Images: {len(article.raw_content.images)}")
                print(f"   Valid: {article.validation.is_valid}")
                print(f"   Words: {article.validation.word_count}")

                # Validate article structure
                if article.raw_content.url and article.raw_content.title and len(article.raw_content.body) > 100:
                    print(f"\n✅ Article structure is valid")
                else:
                    print(f"\n⚠️  Article may have missing fields")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    db.close()

    print("\n" + "="*80)
    print("✅ Test complete")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(quick_test())
