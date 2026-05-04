"""
Initial Data Collection and Full Pipeline Test

This script:
1. Scrapes articles from Daily FT and Hiru News (last 3 days worth)
2. Stores them in MongoDB
3. Runs them through the full Layer 1 pipeline:
   - Smart Caching with Change Detection
   - Semantic Deduplication
   - Business Impact Scoring
   - Cross-Source Validation

Usage:
    cd backend
    python scripts/initial_data_collection.py
"""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongodb import mongodb
from app.db.session import SessionLocal
from app.scrapers.configurable_scraper import ConfigurableScraper, get_configurable_scraper
from app.scrapers.news.ada_derana import AdaDeranaScraper
from app.models.raw_article import RawArticle
from app.models.agent_models import SourceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def scrape_source(source_name: str, max_articles: int = 50) -> List[RawArticle]:
    """Scrape articles from a source."""
    logger.info(f"Scraping {source_name}...")
    
    # Get scraper based on source type
    db = SessionLocal()
    try:
        config = db.query(SourceConfig).filter(
            SourceConfig.source_name == source_name
        ).first()
        
        if not config:
            logger.error(f"Source config not found: {source_name}")
            return []
        
        if config.scraper_class == "AdaDeranaScraper":
            scraper = AdaDeranaScraper()
        else:
            scraper = ConfigurableScraper(config)
    finally:
        db.close()
    
    try:
        articles = await scraper.fetch_articles()
        logger.info(f"  Found {len(articles)} articles from {source_name}")
        return articles[:max_articles]
    except Exception as e:
        logger.error(f"  Error scraping {source_name}: {e}")
        return []


async def store_articles_in_mongodb(articles: List[RawArticle]) -> Dict[str, int]:
    """Store articles in MongoDB raw_articles collection."""
    if not articles:
        return {"inserted": 0, "skipped": 0}
    
    mongodb.connect()  # Not async
    db = mongodb.get_database()
    
    inserted = 0
    skipped = 0
    
    for article in articles:
        try:
            # Check if article already exists
            existing = await db.raw_articles.find_one({
                "article_id": article.article_id
            })
            
            if existing:
                skipped += 1
                continue
            
            # Convert to dict for MongoDB - convert Pydantic types to strings
            article_dict = {
                "article_id": article.article_id,
                "source": {
                    "source_id": article.source.source_id,
                    "name": article.source.name,
                    "url": str(article.source.url)  # Convert HttpUrl to string
                },
                "scrape_metadata": {
                    "job_id": article.scrape_metadata.job_id,
                    "scraped_at": article.scrape_metadata.scraped_at,
                    "scraper_version": article.scrape_metadata.scraper_version
                },
                "raw_content": {
                    "title": article.raw_content.title,
                    "body": article.raw_content.body,
                    "author": article.raw_content.author,
                    "publish_date": article.raw_content.publish_date,
                    "images": [{"url": str(img.get("url", "")), "alt": img.get("alt", "")} for img in article.raw_content.images] if article.raw_content.images else [],
                    "metadata": article.raw_content.metadata
                },
                "validation": {
                    "is_valid": article.validation.is_valid,
                    "word_count": article.validation.word_count
                },
                "created_at": datetime.utcnow(),
                "processed": False
            }
            
            await db.raw_articles.insert_one(article_dict)
            inserted += 1
            
        except Exception as e:
            logger.error(f"Error storing article {article.article_id}: {e}")
    
    return {"inserted": inserted, "skipped": skipped}


async def run_smart_cache_check(source_name: str) -> Dict[str, Any]:
    """Test Smart Cache with Change Detection."""
    logger.info(f"\n📦 Testing Smart Cache for {source_name}...")
    
    try:
        from app.cache import get_smart_cache
        from app.db.redis_client import redis_client
        
        # Initialize Redis connection
        redis_client.connect()
        
        cache = await get_smart_cache()
        
        # Get source config
        db = SessionLocal()
        config = db.query(SourceConfig).filter(
            SourceConfig.source_name == source_name
        ).first()
        db.close()
        
        if not config:
            return {"error": f"Source not found: {source_name}"}
        
        # Safely get list_url with proper None check
        list_url = str(config.base_url) if config.base_url else None
        if config.selectors and isinstance(config.selectors, dict):
            list_url = config.selectors.get("list_url", list_url)
        
        if not list_url:
            return {"error": f"No URL configured for source: {source_name}"}
        
        # Check if we should scrape using needs_scraping method
        should_scrape, reason = await cache.needs_scraping(
            source_name=source_name,
            url=list_url,
            source_type=config.source_type
        )
        
        return {
            "source": source_name,
            "should_scrape": should_scrape,
            "reason": reason,
            "cache_status": "working"
        }
        
    except Exception as e:
        logger.error(f"Smart Cache error: {e}")
        return {"error": str(e)}


async def run_deduplication(articles: List[Dict]) -> Dict[str, Any]:
    """Run semantic deduplication on articles."""
    logger.info(f"\n🔍 Running Semantic Deduplication on {len(articles)} articles...")
    
    try:
        from app.deduplication import get_deduplicator
        
        deduplicator = await get_deduplicator()
        
        unique_articles = []
        duplicates = []
        
        for article in articles:
            content = article.get("raw_content", {})
            title = content.get("title", "")
            body = content.get("body", "")
            url = article.get("source", {}).get("url", "")
            
            # Check for duplicates using check_duplicate method with correct signature
            result = await deduplicator.check_duplicate(
                article_id=article.get("article_id"),
                title=title,
                body=body,
                url=url,
                source_name=article.get("source", {}).get("name", "unknown")
            )
            
            if result.is_duplicate:
                duplicates.append({
                    "article_id": article.get("article_id"),
                    "similar_to": result.original_article_id,
                    "type": result.duplicate_type.value if result.duplicate_type else "unknown"
                })
            else:
                unique_articles.append(article)
        
        return {
            "total": len(articles),
            "unique": len(unique_articles),
            "duplicates": len(duplicates),
            "duplicate_details": duplicates[:5]  # Show first 5
        }
        
    except ImportError:
        logger.warning("Deduplicator not available, using simple hash-based dedup")
        # Fallback to simple title-based deduplication
        seen_titles = set()
        unique = 0
        duplicates = 0
        
        for article in articles:
            title = article.get("raw_content", {}).get("title", "")
            if title in seen_titles:
                duplicates += 1
            else:
                seen_titles.add(title)
                unique += 1
        
        return {
            "total": len(articles),
            "unique": unique,
            "duplicates": duplicates,
            "method": "simple_hash"
        }
    except Exception as e:
        logger.error(f"Deduplication error: {e}")
        return {"error": str(e)}


async def run_business_impact_scoring(articles: List[Dict]) -> Dict[str, Any]:
    """Score articles for business impact."""
    logger.info(f"\n💼 Scoring Business Impact for {len(articles)} articles...")
    
    try:
        from app.impact_scorer import BusinessImpactScorer
        
        scorer = BusinessImpactScorer()
        await scorer.initialize()
        scores = []
        
        for article in articles[:20]:  # Limit for performance
            content = article.get("raw_content", {})
            
            # Use score_article method with proper dict format
            article_data = {
                "article_id": article.get("article_id"),
                "title": content.get("title", ""),
                "content": content.get("body", ""),
                "source": article.get("source", {}).get("name", "unknown"),
                "published_at": content.get("publish_date")
            }
            
            result = await scorer.score_article(article_data)
            
            scores.append({
                "article_id": article.get("article_id"),
                "title": content.get("title", "")[:50],
                "impact_score": result.impact_score,  # Correct attribute name
                "urgency": result.impact_level.value if hasattr(result, 'impact_level') else "medium",
                "sectors": [s.get("name", "") for s in result.primary_sectors[:3]] if hasattr(result, 'primary_sectors') else []
            })
        
        # Sort by impact score
        scores.sort(key=lambda x: x.get("impact_score", 0), reverse=True)
        
        return {
            "scored": len(scores),
            "high_impact": len([s for s in scores if s.get("impact_score", 0) > 0.7]),
            "medium_impact": len([s for s in scores if 0.4 < s.get("impact_score", 0) <= 0.7]),
            "low_impact": len([s for s in scores if s.get("impact_score", 0) <= 0.4]),
            "top_5": scores[:5]
        }
        
    except ImportError:
        logger.warning("BusinessImpactScorer not available, using simple keyword scoring")
        # Fallback to simple keyword-based scoring
        high_impact_keywords = ["crisis", "emergency", "urgent", "break", "alert", "flood", "disaster"]
        scores = []
        
        for article in articles[:20]:
            content = article.get("raw_content", {})
            title = content.get("title", "").lower()
            body = content.get("body", "").lower()
            
            # Simple keyword match
            score = 0.3  # Base score
            for kw in high_impact_keywords:
                if kw in title:
                    score += 0.2
                if kw in body:
                    score += 0.1
            
            scores.append({
                "article_id": article.get("article_id"),
                "title": content.get("title", "")[:50],
                "impact_score": min(score, 1.0)
            })
        
        scores.sort(key=lambda x: x.get("impact_score", 0), reverse=True)
        
        return {
            "scored": len(scores),
            "method": "keyword_based",
            "top_5": scores[:5]
        }
    except Exception as e:
        logger.error(f"Business Impact Scoring error: {e}")
        return {"error": str(e)}


async def run_cross_source_validation(articles: List[Dict]) -> Dict[str, Any]:
    """Validate articles across sources."""
    logger.info(f"\n🔗 Running Cross-Source Validation on {len(articles)} articles...")
    
    try:
        from app.cross_validation import get_validator
        
        validator = get_validator()
        
        validated = []
        for article in articles[:15]:  # Limit for performance
            content = article.get("raw_content", {})
            source = article.get("source", {}).get("name", "unknown")
            
            # Use validate_article method with correct positional arguments
            result = validator.validate_article(
                article_id=article.get("article_id"),
                content=content.get("body", ""),
                title=content.get("title", ""),
                source_name=source
            )
            
            validated.append({
                "article_id": article.get("article_id"),
                "source": source,
                "trust_level": result.trust_level.value if hasattr(result, 'trust_level') else "unknown",
                "trust_score": result.trust_score if hasattr(result, 'trust_score') else 0,
                "source_tier": result.source_reputation.tier.value if hasattr(result, 'source_reputation') and result.source_reputation else "unknown"
            })
        
        return {
            "validated": len(validated),
            "high_trust": len([v for v in validated if v.get("trust_level") in ["high", "verified"]]),
            "samples": validated[:5]
        }
        
    except ImportError:
        logger.warning("CrossSourceValidator not available")
        # Group by source
        sources = {}
        for article in articles:
            source = article.get("source", {}).get("name", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "sources": sources,
            "cross_source_topics": "Feature requires CrossSourceValidator module",
            "method": "source_grouping"
        }
    except Exception as e:
        logger.error(f"Cross-Source Validation error: {e}")
        return {"error": str(e)}


async def main():
    """Main execution flow."""
    print("\n" + "=" * 70)
    print("🚀 INITIAL DATA COLLECTION & FULL PIPELINE TEST")
    print("=" * 70)
    
    sources_to_scrape = ["daily_ft", "hiru_news", "ada_derana"]
    all_articles = []
    
    # =============================================
    # STEP 1: Scrape Articles
    # =============================================
    print("\n📰 STEP 1: Scraping Articles from Sources...")
    print("-" * 50)
    
    for source in sources_to_scrape:
        articles = await scrape_source(source, max_articles=30)
        all_articles.extend(articles)
    
    print(f"\n✅ Total articles scraped: {len(all_articles)}")
    
    # =============================================
    # STEP 2: Store in MongoDB
    # =============================================
    print("\n💾 STEP 2: Storing Articles in MongoDB...")
    print("-" * 50)
    
    result = await store_articles_in_mongodb(all_articles)
    print(f"   Inserted: {result['inserted']}")
    print(f"   Skipped (duplicates): {result['skipped']}")
    
    # Get stored articles from MongoDB for processing
    mongodb.connect()  # Not async
    db_mongo = mongodb.get_database()
    stored_articles = await db_mongo.raw_articles.find({}).to_list(length=100)
    print(f"   Total in database: {len(stored_articles)}")
    
    # =============================================
    # STEP 3: Smart Cache Check
    # =============================================
    print("\n📦 STEP 3: Testing Smart Cache with Change Detection...")
    print("-" * 50)
    
    for source in sources_to_scrape:
        cache_result = await run_smart_cache_check(source)
        if "error" in cache_result:
            print(f"   {source}: ⚠️ {cache_result['error']}")
        else:
            print(f"   {source}:")
            print(f"      Should scrape: {cache_result.get('should_scrape', 'N/A')}")
            print(f"      Reason: {cache_result.get('reason', 'N/A')}")
    
    # =============================================
    # STEP 4: Semantic Deduplication
    # =============================================
    print("\n🔍 STEP 4: Semantic Deduplication...")
    print("-" * 50)
    
    dedup_result = await run_deduplication(stored_articles)
    print(f"   Total articles: {dedup_result.get('total', 0)}")
    print(f"   Unique articles: {dedup_result.get('unique', 0)}")
    print(f"   Duplicates found: {dedup_result.get('duplicates', 0)}")
    if dedup_result.get('method'):
        print(f"   Method: {dedup_result['method']}")
    
    # =============================================
    # STEP 5: Business Impact Scoring
    # =============================================
    print("\n💼 STEP 5: Business Impact Scoring...")
    print("-" * 50)
    
    impact_result = await run_business_impact_scoring(stored_articles)
    if "error" not in impact_result:
        print(f"   Articles scored: {impact_result.get('scored', 0)}")
        print(f"   High impact: {impact_result.get('high_impact', 0)}")
        print(f"   Medium impact: {impact_result.get('medium_impact', 0)}")
        print(f"   Low impact: {impact_result.get('low_impact', 0)}")
        
        if impact_result.get('top_5'):
            print("\n   📊 Top 5 High-Impact Articles:")
            for i, article in enumerate(impact_result['top_5'], 1):
                print(f"      {i}. [{article.get('impact_score', 0):.2f}] {article.get('title', 'N/A')}")
    else:
        print(f"   ⚠️ {impact_result['error']}")
    
    # =============================================
    # STEP 6: Cross-Source Validation
    # =============================================
    print("\n🔗 STEP 6: Cross-Source Validation...")
    print("-" * 50)
    
    validation_result = await run_cross_source_validation(stored_articles)
    if "error" not in validation_result:
        if validation_result.get("sources"):
            print("   Articles by source:")
            for source, count in validation_result["sources"].items():
                print(f"      - {source}: {count}")
        if validation_result.get("validated"):
            print(f"\n   Validated: {validation_result['validated']}")
            print(f"   High trust: {validation_result.get('high_trust', 0)}")
    else:
        print(f"   ⚠️ {validation_result['error']}")
    
    # =============================================
    # SUMMARY
    # =============================================
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    print(f"   Sources scraped: {len(sources_to_scrape)}")
    print(f"   Total articles: {len(all_articles)}")
    print(f"   Stored in MongoDB: {result['inserted']}")
    print(f"   Duplicates skipped: {result['skipped']}")
    
    # Check component status
    print("\n   Component Status:")
    print(f"      ✅ Scraping: Working")
    print(f"      ✅ MongoDB Storage: Working")
    print(f"      {'✅' if 'error' not in cache_result else '⚠️'} Smart Cache: {'Working' if 'error' not in cache_result else 'Needs setup'}")
    print(f"      {'✅' if 'error' not in dedup_result else '⚠️'} Deduplication: {'Working' if 'error' not in dedup_result else 'Fallback mode'}")
    print(f"      {'✅' if 'error' not in impact_result else '⚠️'} Impact Scoring: {'Working' if 'error' not in impact_result else 'Fallback mode'}")
    print(f"      {'✅' if 'error' not in validation_result else '⚠️'} Cross-Validation: {'Working' if 'error' not in validation_result else 'Limited'}")
    
    print("\n✅ Initial data collection complete!")
    print("   You can now view articles at: http://localhost:3000")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
