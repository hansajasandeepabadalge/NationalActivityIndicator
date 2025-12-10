"""
Test Universal Configurable Scraper

Tests the ConfigurableScraper with Daily FT and Hiru News.

Usage:
    cd backend
    python scripts/test_configurable_scraper.py
    python scripts/test_configurable_scraper.py --source daily_ft
    python scripts/test_configurable_scraper.py --source hiru_news
"""

import sys
import os
import asyncio
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.configurable_scraper import ConfigurableScraper, get_configurable_scraper, get_all_configurable_sources
from app.db.session import SessionLocal
from app.models.agent_models import SourceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_scraper(source_name: str, max_articles: int = 5):
    """Test scraping a single source."""
    print(f"\n{'='*60}")
    print(f"Testing: {source_name}")
    print(f"{'='*60}")
    
    # Get scraper
    scraper = get_configurable_scraper(source_name)
    
    if not scraper:
        print(f"❌ Could not create scraper for '{source_name}'")
        print("   Make sure the source config exists in the database.")
        print("   Run: python scripts/populate_source_configs.py")
        return False
    
    print(f"✅ Scraper created: {scraper.source_info.name}")
    print(f"   Base URL: {scraper.config.base_url}")
    print(f"   Selectors: {list(scraper.selectors.keys())}")
    
    # Run scraper
    print(f"\n📰 Fetching articles...")
    try:
        articles = await scraper.fetch_articles()
        
        print(f"\n✅ Found {len(articles)} articles")
        
        # Show sample articles
        for i, article in enumerate(articles[:max_articles]):
            print(f"\n--- Article {i+1} ---")
            print(f"ID: {article.article_id}")
            print(f"Title: {article.raw_content.title[:80]}..." if len(article.raw_content.title) > 80 else f"Title: {article.raw_content.title}")
            print(f"Body Length: {len(article.raw_content.body)} chars")
            print(f"Word Count: {article.validation.word_count}")
            if article.raw_content.author:
                print(f"Author: {article.raw_content.author}")
            if article.raw_content.publish_date:
                print(f"Date: {article.raw_content.publish_date}")
            print(f"Images: {len(article.raw_content.images)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_all_active_sources():
    """Test all active configurable sources."""
    print("\n" + "="*60)
    print("Testing All Active Configurable Sources")
    print("="*60)
    
    # Get all active sources using ConfigurableScraper
    db = SessionLocal()
    try:
        sources = db.query(SourceConfig).filter(
            SourceConfig.is_active == True,
            SourceConfig.scraper_class == 'ConfigurableScraper'
        ).all()
        
        print(f"\nFound {len(sources)} active configurable sources:")
        for s in sources:
            print(f"  - {s.source_name} ({s.display_name})")
        
    finally:
        db.close()
    
    # Test each source
    results = {}
    for source in sources:
        try:
            success = await test_scraper(source.source_name, max_articles=3)
            results[source.source_name] = "✅ Success" if success else "❌ Failed"
        except Exception as e:
            results[source.source_name] = f"❌ Error: {e}"
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for source, result in results.items():
        print(f"  {source}: {result}")


def show_source_info():
    """Show all source configurations."""
    db = SessionLocal()
    try:
        sources = db.query(SourceConfig).all()
        
        print("\n📋 All Source Configurations:\n")
        for source in sources:
            status = "🟢 Active" if source.is_active else "🔴 Inactive"
            print(f"{source.source_name}: {source.display_name or 'N/A'}")
            print(f"  Status: {status}")
            print(f"  Scraper: {source.scraper_class or 'ConfigurableScraper'}")
            print(f"  Categories: {source.categories}")
            print(f"  Tier: {source.reliability_tier}")
            if source.selectors:
                print(f"  Selectors: {list(source.selectors.keys())}")
            print()
            
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Universal Configurable Scraper")
    parser.add_argument("--source", help="Source name to test (e.g., daily_ft, hiru_news)")
    parser.add_argument("--all", action="store_true", help="Test all active configurable sources")
    parser.add_argument("--info", action="store_true", help="Show source configuration info")
    parser.add_argument("--max", type=int, default=5, help="Max articles to show per source")
    
    args = parser.parse_args()
    
    if args.info:
        show_source_info()
    elif args.all:
        asyncio.run(test_all_active_sources())
    elif args.source:
        asyncio.run(test_scraper(args.source, args.max))
    else:
        # Default: show info and test all
        show_source_info()
        print("\nRun with --source <name> to test a specific source")
        print("Run with --all to test all active configurable sources")
