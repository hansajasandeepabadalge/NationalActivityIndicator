"""
Test Enhanced Scraping System

Tests the ConfigurableScraper with multiple new sources to verify:
1. Selector functionality (multi-path, meta tags, lazy images)
2. Data extraction quality
3. Database storage
4. Agent integration

Usage:
    cd backend
    python scripts/test_enhanced_scraping.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.scrapers.configurable_scraper import ConfigurableScraper
from app.models.agent_models import SourceConfig
from app.db.session import SessionLocal
from datetime import datetime


async def test_single_source(source_name: str):
    """Test scraping a single source."""
    print(f"\n{'='*80}")
    print(f"🔍 Testing: {source_name}")
    print('='*80)

    db = SessionLocal()
    try:
        # Get source config
        config = db.query(SourceConfig).filter(
            SourceConfig.source_name == source_name,
            SourceConfig.is_active == True
        ).first()

        if not config:
            print(f"❌ Source '{source_name}' not found or inactive")
            return None

        display_name = (config.config_metadata or {}).get('display_name', source_name)
        print(f"📰 Source: {display_name}")
        print(f"🌐 Base URL: {config.base_url}")
        print(f"🔧 Scraper: {config.scraper_class}")
        print(f"⚙️  List URL: {config.selectors.get('list_url', 'N/A')}")

        # Create scraper
        scraper = ConfigurableScraper(config)

        # Fetch articles
        print(f"\n⏳ Fetching articles...")
        start_time = datetime.utcnow()
        articles = await scraper.fetch_articles()
        elapsed = (datetime.utcnow() - start_time).total_seconds()

        print(f"\n✅ Scraped {len(articles)} articles in {elapsed:.2f}s")

        # Display article details
        if articles:
            print(f"\n📄 Article Samples:\n")
            for i, article in enumerate(articles[:3], 1):  # Show first 3
                print(f"  [{i}] {article.raw_content.title}")
                print(f"      URL: {article.raw_content.url}")
                print(f"      Author: {article.raw_content.author or 'N/A'}")
                print(f"      Date: {article.raw_content.publish_date or 'N/A'}")
                print(f"      Body length: {len(article.raw_content.body)} chars")
                print(f"      Images: {len(article.raw_content.images)}")
                print(f"      Valid: {article.validation.is_valid}")
                if not article.validation.is_valid:
                    print(f"      Errors: {article.validation.validation_errors}")
                print()

            # Statistics
            valid_count = sum(1 for a in articles if a.validation.is_valid)
            avg_body_length = sum(len(a.raw_content.body) for a in articles) / len(articles)
            articles_with_images = sum(1 for a in articles if a.raw_content.images)
            articles_with_dates = sum(1 for a in articles if a.raw_content.publish_date)

            print(f"📊 Statistics:")
            print(f"   - Valid articles: {valid_count}/{len(articles)} ({valid_count/len(articles)*100:.1f}%)")
            print(f"   - Avg body length: {avg_body_length:.0f} chars")
            print(f"   - Articles with images: {articles_with_images}/{len(articles)} ({articles_with_images/len(articles)*100:.1f}%)")
            print(f"   - Articles with dates: {articles_with_dates}/{len(articles)} ({articles_with_dates/len(articles)*100:.1f}%)")

        return {
            'source_name': source_name,
            'display_name': display_name,
            'article_count': len(articles),
            'valid_count': sum(1 for a in articles if a.validation.is_valid),
            'elapsed': elapsed,
            'success': len(articles) > 0
        }

    except Exception as e:
        print(f"\n❌ Error testing {source_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'source_name': source_name,
            'success': False,
            'error': str(e)
        }
    finally:
        db.close()


async def test_multiple_sources(source_names: list):
    """Test multiple sources in parallel."""
    print(f"\n🚀 Testing {len(source_names)} sources...\n")

    tasks = [test_single_source(name) for name in source_names]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Summary
    print(f"\n{'='*80}")
    print("📊 FINAL SUMMARY")
    print('='*80)

    success_count = 0
    total_articles = 0

    print(f"\n{'Source':<25} {'Status':<10} {'Articles':<10} {'Valid':<10} {'Time':<10}")
    print('-'*80)

    for result in results:
        if isinstance(result, dict):
            if result.get('success'):
                status = "✅ PASS"
                success_count += 1
                total_articles += result.get('article_count', 0)
                articles_str = str(result.get('article_count', 0))
                valid_str = str(result.get('valid_count', 0))
                time_str = f"{result.get('elapsed', 0):.1f}s"
            else:
                status = "❌ FAIL"
                articles_str = "-"
                valid_str = "-"
                time_str = "-"

            source = result.get('source_name', 'unknown')
            print(f"{source:<25} {status:<10} {articles_str:<10} {valid_str:<10} {time_str:<10}")
        else:
            print(f"{'error':<25} {'❌ FAIL':<10} {'-':<10} {'-':<10} {'-':<10}")

    print('-'*80)
    print(f"\n✅ Passed: {success_count}/{len(source_names)} sources")
    print(f"📰 Total articles: {total_articles}")
    print(f"📈 Success rate: {success_count/len(source_names)*100:.1f}%")


async def test_database_storage(source_name: str):
    """Test scraping and database storage."""
    print(f"\n{'='*80}")
    print(f"💾 Testing Database Storage: {source_name}")
    print('='*80)

    db = SessionLocal()
    try:
        # Import required models
        from app.integration.pipeline import IntegrationPipeline
        from app.db.models import ProcessedArticle

        # Get source config
        config = db.query(SourceConfig).filter(
            SourceConfig.source_name == source_name,
            SourceConfig.is_active == True
        ).first()

        if not config:
            print(f"❌ Source not found")
            return

        # Scrape articles
        scraper = ConfigurableScraper(config)
        articles = await scraper.fetch_articles()

        if not articles:
            print(f"⚠️  No articles scraped")
            return

        print(f"✅ Scraped {len(articles)} articles")

        # Store in database via pipeline
        print(f"\n💾 Storing articles in database...")
        pipeline = IntegrationPipeline()

        stored_count = 0
        for article in articles[:3]:  # Test with first 3 articles
            try:
                # Convert RawArticle to ProcessedArticle
                processed = pipeline.process_raw_article(article)
                if processed:
                    stored_count += 1
                    print(f"   ✅ Stored: {processed.title[:60]}...")
            except Exception as e:
                print(f"   ❌ Failed to store: {e}")

        print(f"\n✅ Successfully stored {stored_count}/{len(articles[:3])} articles")

        # Query stored articles
        stored_articles = db.query(ProcessedArticle).filter(
            ProcessedArticle.source == config.source_name
        ).order_by(ProcessedArticle.created_at.desc()).limit(5).all()

        print(f"\n📊 Last 5 stored articles from {source_name}:")
        for i, article in enumerate(stored_articles, 1):
            print(f"   [{i}] {article.title[:60]}...")
            print(f"       ID: {article.id}")
            print(f"       Source: {article.source}")
            print(f"       Created: {article.created_at}")

    except Exception as e:
        print(f"\n❌ Database storage test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


async def main():
    """Main test runner."""
    print("="*80)
    print("🧪 ENHANCED SCRAPING SYSTEM TEST")
    print("="*80)

    # Test sources (mix of news, government, research)
    test_sources = [
        # Newly activated
        'daily_mirror',
        'news_first',
        'cbsl',

        # New sources
        'sunday_observer',
        'the_island',
    ]

    # Check which sources are available
    print("\n🔍 Checking available sources...")
    db = SessionLocal()
    available_sources = db.query(SourceConfig).filter(
        SourceConfig.source_name.in_(test_sources),
        SourceConfig.is_active == True
    ).all()
    db.close()

    available_names = [s.source_name for s in available_sources]
    print(f"✅ Found {len(available_names)} active sources: {', '.join(available_names)}")

    if not available_names:
        print("\n⚠️  No test sources found. Please run:")
        print("   python scripts/populate_enhanced_sources.py")
        return

    # Test all sources
    await test_multiple_sources(available_names)

    # Test database storage with one source
    if available_names:
        print("\n" + "="*80)
        await test_database_storage(available_names[0])


if __name__ == "__main__":
    asyncio.run(main())
