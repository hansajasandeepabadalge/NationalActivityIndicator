"""
Test All Scrapers

Run this script to test scraping from all configured news sources:
    python scripts/test_all_scrapers.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_ada_derana():
    """Test Ada Derana scraper"""
    print("\n" + "=" * 60)
    print("📰 TESTING: Ada Derana")
    print("=" * 60)
    
    try:
        from app.scrapers.news.ada_derana import AdaDeranaScraper
        
        scraper = AdaDeranaScraper()
        print(f"Connecting to {scraper.source_info.url}...")
        
        articles = await scraper.fetch_articles()
        
        if articles:
            print(f"✅ SUCCESS: Scraped {len(articles)} articles")
            print(f"   Sample: {articles[0].raw_content.title[:50]}...")
            return True, len(articles)
        else:
            print("❌ FAILED: No articles found")
            return False, 0
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, 0


async def test_daily_ft():
    """Test Daily FT scraper"""
    print("\n" + "=" * 60)
    print("📰 TESTING: Daily FT")
    print("=" * 60)
    
    try:
        from app.scrapers.news.daily_ft import DailyFTScraper
        
        scraper = DailyFTScraper()
        print(f"Connecting to {scraper.source_info.url}...")
        
        articles = await scraper.fetch_articles()
        
        if articles:
            print(f"✅ SUCCESS: Scraped {len(articles)} articles")
            print(f"   Sample: {articles[0].raw_content.title[:50]}...")
            return True, len(articles)
        else:
            print("❌ FAILED: No articles found")
            return False, 0
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, 0


async def test_hiru_news():
    """Test Hiru News scraper"""
    print("\n" + "=" * 60)
    print("📰 TESTING: Hiru News")
    print("=" * 60)
    
    try:
        from app.scrapers.news.hiru_news import HiruNewsScraper
        
        scraper = HiruNewsScraper()
        print(f"Connecting to {scraper.source_info.url}...")
        
        articles = await scraper.fetch_articles()
        
        if articles:
            print(f"✅ SUCCESS: Scraped {len(articles)} articles")
            print(f"   Sample: {articles[0].raw_content.title[:50]}...")
            return True, len(articles)
        else:
            print("❌ FAILED: No articles found")
            return False, 0
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, 0


async def main():
    print("\n" + "=" * 60)
    print("         ALL SCRAPERS TEST")
    print("=" * 60)
    
    results = {}
    
    # Test each scraper
    results["Ada Derana"] = await test_ada_derana()
    results["Daily FT"] = await test_daily_ft()
    results["Hiru News"] = await test_hiru_news()
    
    # Summary
    print("\n" + "=" * 60)
    print("         SUMMARY")
    print("=" * 60)
    
    total_articles = 0
    passed = 0
    
    for name, (success, count) in results.items():
        icon = "✅" if success else "❌"
        print(f"   {icon} {name}: {'PASS' if success else 'FAIL'} ({count} articles)")
        if success:
            passed += 1
            total_articles += count
    
    print(f"\n   Total: {passed}/3 scrapers working")
    print(f"   Total articles: {total_articles}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
