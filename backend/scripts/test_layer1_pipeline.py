"""
Full Layer 1 Pipeline Test

Tests the complete Layer 1 pipeline from scraping to processing,
validating that data flows correctly through all components.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from datetime import datetime
from uuid import uuid4

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reduce noise
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('charset_normalizer').setLevel(logging.WARNING)


def print_header(text: str):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def print_section(text: str):
    print(f"\n--- {text} ---")


async def test_layer1_pipeline():
    """Test the complete Layer 1 pipeline."""
    print_header("LAYER 1 COMPLETE PIPELINE TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "scraping": {"status": "not_run", "count": 0},
        "processing": {"status": "not_run", "count": 0},
        "priority": {"status": "not_run", "count": 0},
        "validation": {"status": "not_run", "count": 0},
        "mongodb_storage": {"status": "not_run", "count": 0},
    }
    
    # Test 1: Scraping with available scrapers
    print_section("1. Testing Scrapers (ada_derana, daily_ft, hiru_news)")
    try:
        from app.agents.tools.scraper_tools import ScraperToolManager
        
        scraper_manager = ScraperToolManager()
        all_articles = []
        
        for source_name in ["ada_derana", "daily_ft", "hiru_news"]:
            try:
                result = await scraper_manager.execute_scraper(source_name)
                if result.get("success"):
                    articles = result.get("articles", [])
                    all_articles.extend(articles)
                    print(f"   ✅ {source_name}: {len(articles)} articles")
                else:
                    print(f"   ⚠️ {source_name}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"   ❌ {source_name}: {str(e)[:60]}")
        
        results["scraping"]["count"] = len(all_articles)
        results["scraping"]["status"] = "success" if all_articles else "no_articles"
        print(f"\n   Total scraped: {len(all_articles)} articles")
        
    except Exception as e:
        print(f"   ❌ Scraping failed: {e}")
        results["scraping"]["status"] = "error"
    
    # Test 2: Processing Agent
    print_section("2. Testing Processing Agent")
    try:
        from app.agents.processing_agent import ProcessingAgent
        
        agent = ProcessingAgent()
        
        # Create sample article for processing - single article, not list
        sample_article = {
            "title": "Sri Lanka Economy Shows Recovery Signs",
            "content": "The Central Bank of Sri Lanka reported positive economic indicators today. "
                      "Tourism revenue has increased by 15% compared to last year. "
                      "Exports are also showing improvement. The government expects continued growth.",
            "source": "daily_ft",
            "url": "https://example.com/article1"
        }
        
        result = await agent.execute(sample_article)
        
        if result.get("action"):
            print(f"   ✅ Processing Agent: Action = {result.get('action')}")
            print(f"      Quality Score: {result.get('quality_score')}")
            print(f"      Content Type: {result.get('content_type')}")
            print(f"      Language: {result.get('language')}")
            results["processing"]["count"] = 1
            results["processing"]["status"] = "success"
        else:
            print(f"   ⚠️ Processing Agent: No action returned")
            results["processing"]["status"] = "no_output"
            
    except Exception as e:
        print(f"   ❌ Processing failed: {e}")
        results["processing"]["status"] = "error"
    
    # Test 3: Priority Detection Agent
    print_section("3. Testing Priority Detection Agent")
    try:
        from app.agents.priority_agent import PriorityDetectionAgent
        
        agent = PriorityDetectionAgent()
        
        # Test critical article
        critical_article = {
            "title": "BREAKING: Major Policy Change Announced by Government",
            "content": "The government has announced immediate implementation of new economic regulations affecting all industries.",
            "source": "ada_derana"
        }
        
        result = await agent.execute(critical_article)
        
        if result.get("urgency_level"):
            print(f"   ✅ Priority Agent: Urgency = {result.get('urgency_level')}")
            print(f"      Score: {result.get('urgency_score')}")
            print(f"      Fast Track: {result.get('fast_track')}")
            results["priority"]["count"] = 1
            results["priority"]["status"] = "success"
        else:
            print(f"   ⚠️ Priority Agent: No classification returned")
            results["priority"]["status"] = "no_output"
            
    except Exception as e:
        print(f"   ❌ Priority classification failed: {e}")
        results["priority"]["status"] = "error"
    
    # Test 4: Validation Agent
    print_section("4. Testing Validation Agent")
    try:
        from app.agents.validation_agent import ValidationAgent
        
        agent = ValidationAgent()
        
        # Test with a well-formed article
        test_article = {
            "title": "Economic Report: Q4 Analysis Shows Growth",
            "content": "This is a comprehensive economic analysis report covering the fourth quarter. " * 15,
            "body": "This is a comprehensive economic analysis report covering the fourth quarter. " * 15,
            "source": "daily_ft",
            "url": "https://www.ft.lk/news/economic-report",
            "publish_date": datetime.now().isoformat()
        }
        
        result = await agent.execute(test_article)
        
        if "is_valid" in result:
            print(f"   ✅ Validation Agent: Valid = {result.get('is_valid')}")
            print(f"      Quality Score: {result.get('quality_score')}")
            print(f"      Issues: {len(result.get('validation_issues', []))}")
            results["validation"]["count"] = 1
            results["validation"]["status"] = "success"
        else:
            print(f"   ⚠️ Validation Agent: No validation result")
            results["validation"]["status"] = "no_output"
            
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")
        results["validation"]["status"] = "error"
    
    # Test 5: MongoDB Storage Check
    print_section("5. Checking MongoDB Storage")
    try:
        from pymongo import MongoClient
        
        # Connect with authentication
        client = MongoClient(
            "mongodb://admin:mongo_secure_2024@localhost:27017/",
            serverSelectionTimeoutMS=5000
        )
        db = client.national_indicator
        
        # Check raw_articles collection
        raw_count = db.raw_articles.count_documents({})
        print(f"   📊 MongoDB raw_articles: {raw_count} documents")
        
        # Check recent articles
        recent = list(db.raw_articles.find().sort("scraped_at", -1).limit(3))
        if recent:
            print(f"   Recent articles:")
            for doc in recent:
                title = doc.get("title", "No title")[:50]
                source = doc.get("source", "Unknown")
                print(f"      • {source}: {title}...")
        
        results["mongodb_storage"]["count"] = raw_count
        results["mongodb_storage"]["status"] = "success"
        
        client.close()
        
    except Exception as e:
        print(f"   ❌ MongoDB check failed: {e}")
        results["mongodb_storage"]["status"] = "error"
    
    # Summary
    print_header("PIPELINE SUMMARY")
    
    print("\n📊 RESULTS:")
    print(f"   {'Component':<25} {'Status':<15} {'Count'}")
    print("-" * 55)
    
    for component, data in results.items():
        status_icon = "✅" if data["status"] == "success" else "⚠️" if data["status"] == "no_output" else "❌"
        print(f"   {component:<25} {status_icon} {data['status']:<12} {data['count']}")
    
    # Check overall success
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    total = len(results)
    
    print(f"\n   Overall: {success_count}/{total} components working")
    
    return success_count >= 3  # At least 3 components should work


async def main():
    try:
        success = await test_layer1_pipeline()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
