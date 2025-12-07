"""
Scraper Tools for AI Agents

LangChain tools that wrap existing scraper functionality.
The agents use these tools to execute scraping operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain.tools import Tool

from app.scrapers.base import BaseScraper
from app.scrapers.news.ada_derana import AdaDeranaScraper
from app.models.raw_article import RawArticle
from app.agents.tools.database_tools import update_scrape_result

logger = logging.getLogger(__name__)


# ============================================
# Scraper Registry
# ============================================

# Map source names to their scraper classes
SCRAPER_REGISTRY: Dict[str, type] = {
    "ada_derana": AdaDeranaScraper,
    # Add more scrapers as they are implemented:
    # "daily_mirror": DailyMirrorScraper,
    # "hiru_news": HiruNewsScraper,
    # "government_gazette": GovernmentGazetteScraper,
}


def get_available_scrapers() -> List[str]:
    """Get list of available scraper names."""
    return list(SCRAPER_REGISTRY.keys())


def get_scraper_instance(source_name: str) -> Optional[BaseScraper]:
    """
    Get a scraper instance for the given source.
    
    Args:
        source_name: Name of the source
        
    Returns:
        Scraper instance or None if not found
    """
    scraper_class = SCRAPER_REGISTRY.get(source_name)
    if scraper_class:
        return scraper_class()
    return None


# ============================================
# Scraper Tool Functions
# ============================================

async def _scrape_source_async(source_name: str) -> Dict[str, Any]:
    """
    Async implementation of scraping a source.
    
    Args:
        source_name: Name of the source to scrape
        
    Returns:
        Dict with scraping results
    """
    logger.info(f"Starting scrape for source: {source_name}")
    start_time = datetime.utcnow()
    
    try:
        # Get scraper instance
        scraper = get_scraper_instance(source_name)
        
        if not scraper:
            return {
                "success": False,
                "source_name": source_name,
                "error": f"No scraper found for source '{source_name}'",
                "available_scrapers": get_available_scrapers()
            }
        
        # Execute scraping
        articles = await scraper.fetch_articles()
        
        # Calculate duration
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Update database with scrape result
        update_scrape_result(
            source_name=source_name,
            articles_count=len(articles),
            success=True
        )
        
        # Convert articles to serializable format
        articles_data = []
        for article in articles:
            articles_data.append({
                "article_id": article.article_id,
                "title": article.raw_content.title,
                "url": str(article.source.url) if hasattr(article.source, 'url') else "",
                "publish_date": article.raw_content.publish_date.isoformat() if article.raw_content.publish_date else None,
                "word_count": article.validation.word_count
            })
        
        logger.info(f"Scrape complete for {source_name}: {len(articles)} articles in {duration_ms}ms")
        
        return {
            "success": True,
            "source_name": source_name,
            "articles_count": len(articles),
            "articles": articles_data,
            "duration_ms": duration_ms,
            "scraped_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error scraping {source_name}: {e}")
        
        # Update database with failure
        update_scrape_result(
            source_name=source_name,
            articles_count=0,
            success=False
        )
        
        return {
            "success": False,
            "source_name": source_name,
            "error": str(e),
            "duration_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000)
        }


def scrape_source(source_name: str) -> Dict[str, Any]:
    """
    Scrape a specific source (sync wrapper for async scraper).
    
    Args:
        source_name: Name of the source to scrape
        
    Returns:
        Dict with scraping results including articles found
    """
    try:
        # Run async scraper in event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, create new task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _scrape_source_async(source_name))
                return future.result()
        else:
            return asyncio.run(_scrape_source_async(source_name))
    except Exception as e:
        logger.error(f"Error in scrape_source for {source_name}: {e}")
        return {
            "success": False,
            "source_name": source_name,
            "error": str(e)
        }


async def scrape_multiple_sources(source_names: List[str]) -> Dict[str, Any]:
    """
    Scrape multiple sources in parallel.
    
    Args:
        source_names: List of source names to scrape
        
    Returns:
        Dict with results for each source
    """
    logger.info(f"Starting parallel scrape for {len(source_names)} sources")
    start_time = datetime.utcnow()
    
    # Create tasks for parallel execution
    tasks = [_scrape_source_async(name) for name in source_names]
    
    # Execute all in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful = []
    failed = []
    total_articles = 0
    
    for source_name, result in zip(source_names, results):
        if isinstance(result, Exception):
            failed.append({
                "source_name": source_name,
                "error": str(result)
            })
        elif result.get("success"):
            successful.append(result)
            total_articles += result.get("articles_count", 0)
        else:
            failed.append(result)
    
    duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    return {
        "total_sources": len(source_names),
        "successful": len(successful),
        "failed": len(failed),
        "total_articles": total_articles,
        "duration_ms": duration_ms,
        "results": successful,
        "failures": failed
    }


def check_breaking_signals() -> Dict[str, Any]:
    """
    Check for breaking news signals that require immediate scraping.
    
    This is a placeholder that can be extended to check:
    - Social media spikes
    - Alert systems
    - External monitoring services
    
    Returns:
        Dict with breaking news signals if any
    """
    # TODO: Implement actual breaking news detection
    # This could integrate with:
    # - Twitter/X API for trending topics
    # - Alert monitoring systems
    # - External news aggregators
    
    return {
        "breaking_detected": False,
        "signals": [],
        "priority_sources": [],
        "message": "No breaking news signals detected"
    }


def get_scraper_status() -> Dict[str, Any]:
    """
    Get status of all available scrapers.
    
    Returns:
        Dict with scraper availability and status
    """
    return {
        "available_scrapers": get_available_scrapers(),
        "total_scrapers": len(SCRAPER_REGISTRY),
        "status": "operational"
    }


# ============================================
# Create LangChain Tools
# ============================================

def get_scraper_tools() -> List[Tool]:
    """
    Get all scraper tools for AI agents.
    
    Returns:
        List of LangChain Tool objects
    """
    return [
        Tool(
            name="scrape_source",
            func=scrape_source,
            description=(
                "Execute scraping for a specific news source. "
                "Input: source_name (string, e.g., 'ada_derana'). "
                "Returns: List of articles found with titles and metadata. "
                "Use this when you decide a source should be scraped."
            )
        ),
        Tool(
            name="check_breaking_signals",
            func=lambda _: check_breaking_signals(),
            description=(
                "Check for breaking news signals that require immediate attention. "
                "No input required. "
                "Returns: Whether breaking news is detected and which sources to prioritize."
            )
        ),
        Tool(
            name="get_scraper_status",
            func=lambda _: get_scraper_status(),
            description=(
                "Get status of all available scrapers. "
                "No input required. "
                "Returns: List of available scrapers and their operational status."
            )
        ),
        Tool(
            name="get_available_scrapers",
            func=lambda _: {"scrapers": get_available_scrapers()},
            description=(
                "Get list of all available scraper names. "
                "No input required. "
                "Returns: List of source names that can be scraped."
            )
        ),
    ]
