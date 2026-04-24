"""
Populate Source Configurations for Universal Scraper

This script adds source configurations to the database with CSS selectors
for the Universal Configurable Scraper.

Usage:
    cd backend
    python scripts/populate_source_configs.py

The selectors were determined by inspecting each website's HTML structure.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.agent_models import SourceConfig
from datetime import datetime


# ==============================================
# Source Configurations with CSS Selectors
# ==============================================

SOURCE_CONFIGS = [
    # ============================================
    # Ada Derana - English (already has custom scraper, but add config for reference)
    # ============================================
    {
        "source_name": "ada_derana",
        "base_url": "https://www.adaderana.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general", "breaking"],
        "reliability_tier": "trusted",
        "scraper_class": "AdaDeranaScraper",  # Uses custom scraper
        "is_active": True,
        "selectors": {
            "list_url": "https://www.adaderana.lk/hot-news/",
            "article_link_pattern": r"/news/\d+",
            "title": "h1",
            "body": "div.news-content",
            "date": "p.news-datestamp",
            "image": "div.news-content img"
        },
        "config_metadata": {
            "display_name": "Ada Derana",
            "priority_level": "high",
            "default_frequency_minutes": 30,
            "notes": "Primary English news source with custom scraper"
        }
    },
    
    # ============================================
    # Daily FT - Financial Times (Business/Economic)
    # ============================================
    {
        "source_name": "daily_ft",
        "base_url": "https://www.ft.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["economic", "business", "financial"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "requires_javascript": False,
        "is_active": True,
        "selectors": {
            # Main news listing page
            "list_url": "https://www.ft.lk/",
            
            # Pattern to identify article links
            "article_link_pattern": r"/\d+-[a-zA-Z]",
            "article_link_selector": "a.main-headline, div.row a[href*='/']",
            
            # Title extraction (h1 or headline class)
            "title": "h1.main-headline, h1.article-headline, h1, .headline h1",
            
            # Body content (main article container)
            "body": "div.article-content, div.article-body, article, .content-area",
            "body_exclude": ".advertisement, .related-articles, .social-share, .comments",
            
            # Date extraction
            "date": "span.date, .article-date, time, .publish-date",
            "date_format": "%B %d, %Y",
            
            # Author
            "author": ".author-name, .byline, .article-author",
            
            # Images
            "image": ".article-content img, .article-image img"
        },
        "config_metadata": {
            "display_name": "Daily FT (Financial Times)",
            "priority_level": "high",
            "default_frequency_minutes": 60,
            "notes": "Premier business and economic news source. High priority for economic indicators."
        }
    },
    
    # ============================================
    # Hiru News - English
    # ============================================
    {
        "source_name": "hiru_news",
        "base_url": "https://www.hirunews.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general", "breaking"],
        "reliability_tier": "standard",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "requires_javascript": False,
        "is_active": True,
        "selectors": {
            # English news section
            "list_url": "https://www.hirunews.lk/english/",
            
            # Article link pattern
            "article_link_pattern": r"/english/\d+",
            "article_link_selector": "a.news-item, div.news-block a, a[href*='/english/']",
            
            # Title
            "title": "h1.news-heading, h1, .article-title",
            
            # Body
            "body": "div.news-content, div.article-content, .news-body, article",
            "body_exclude": ".advertisement, .related-news, .social-buttons",
            
            # Date
            "date": ".news-date, span.date, .publish-time, time",
            
            # Author
            "author": ".author, .reporter-name",
            
            # Images
            "image": ".news-content img, .featured-image img"
        },
        "config_metadata": {
            "display_name": "Hiru News English",
            "priority_level": "medium",
            "default_frequency_minutes": 45,
            "notes": "Popular Sinhala/English news channel. Good for general news coverage."
        }
    },
    
    # ============================================
    # Daily Mirror (Future - Placeholder)
    # ============================================
    {
        "source_name": "daily_mirror",
        "base_url": "https://www.dailymirror.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general"],
        "reliability_tier": "standard",
        "scraper_class": "ConfigurableScraper",
        "is_active": False,  # Disabled until selectors are verified
        "selectors": {
            "list_url": "https://www.dailymirror.lk/breaking-news",
            "article_link_pattern": r"/breaking-news/\d+",
            "title": "h1.title",
            "body": "div.body-text",
            "date": ".date",
            "author": ".author"
        },
        "config_metadata": {
            "display_name": "Daily Mirror",
            "priority_level": "medium",
            "notes": "Placeholder - Enable after verifying selectors"
        }
    },
    
    # ============================================
    # News First (Future - Placeholder)
    # ============================================
    {
        "source_name": "news_first",
        "base_url": "https://www.newsfirst.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general"],
        "reliability_tier": "standard",
        "scraper_class": "ConfigurableScraper",
        "is_active": False,  # Disabled until selectors are verified
        "selectors": {
            "list_url": "https://www.newsfirst.lk/category/latest-news/",
            "article_link_pattern": r"/\d{4}/\d{2}/\d{2}/",
            "title": "h1.entry-title",
            "body": "div.entry-content",
            "date": ".entry-date",
            "author": ".author"
        },
        "config_metadata": {
            "display_name": "News First",
            "priority_level": "medium",
            "notes": "Placeholder - Enable after verifying selectors"
        }
    },
    
    # ============================================
    # Central Bank of Sri Lanka (Government - Economic)
    # ============================================
    {
        "source_name": "cbsl",
        "base_url": "https://www.cbsl.gov.lk",
        "source_type": "government",
        "language": "en",
        "country": "LK",
        "categories": ["economic", "financial", "government"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "is_active": False,  # Disabled - government sites may need special handling
        "selectors": {
            "list_url": "https://www.cbsl.gov.lk/en/news",
            "article_link_pattern": r"/en/news/",
            "title": "h1.page-title",
            "body": "div.content-area",
            "date": ".date"
        },
        "config_metadata": {
            "display_name": "Central Bank of Sri Lanka",
            "priority_level": "critical",
            "default_frequency_minutes": 240,
            "notes": "Critical source for monetary policy, interest rates. May need special handling."
        }
    }
]


def populate_source_configs():
    """Insert or update source configurations in the database."""
    db = SessionLocal()
    
    try:
        inserted = 0
        updated = 0
        
        for config_data in SOURCE_CONFIGS:
            # Check if source already exists
            existing = db.query(SourceConfig).filter(
                SourceConfig.source_name == config_data["source_name"]
            ).first()
            
            if existing:
                # Update existing configuration
                for key, value in config_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                updated += 1
                print(f"  Updated: {config_data['source_name']}")
            else:
                # Insert new configuration
                new_config = SourceConfig(**config_data)
                db.add(new_config)
                inserted += 1
                print(f"  Inserted: {config_data['source_name']}")
        
        db.commit()
        print(f"\n✅ Successfully processed {inserted + updated} source configs")
        print(f"   - Inserted: {inserted}")
        print(f"   - Updated: {updated}")
        
        # Show active sources
        active_sources = db.query(SourceConfig).filter(
            SourceConfig.is_active == True
        ).all()
        
        print(f"\n📰 Active Sources ({len(active_sources)}):")
        for source in active_sources:
            scraper = source.scraper_class or "ConfigurableScraper"
            print(f"   - {source.source_name} ({source.display_name}) - {scraper}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


def list_source_configs():
    """List all source configurations."""
    db = SessionLocal()
    
    try:
        configs = db.query(SourceConfig).order_by(SourceConfig.reliability_tier, SourceConfig.source_name).all()
        
        print(f"\n📋 Source Configurations ({len(configs)}):\n")
        print(f"{'Name':<20} {'Display Name':<30} {'Type':<12} {'Tier':<12} {'Active':<8} {'Scraper'}")
        print("-" * 120)
        
        for config in configs:
            active = "✅" if config.is_active else "❌"
            scraper = config.scraper_class or "ConfigurableScraper"
            print(f"{config.source_name:<20} {config.display_name[:28]:<30} {config.source_type:<12} {config.reliability_tier:<12} {active:<8} {scraper}")
            
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage source configurations")
    parser.add_argument("--list", action="store_true", help="List all source configs")
    parser.add_argument("--populate", action="store_true", help="Populate/update source configs")
    
    args = parser.parse_args()
    
    if args.list:
        list_source_configs()
    elif args.populate:
        print("🔧 Populating source configurations...\n")
        populate_source_configs()
    else:
        # Default: populate
        print("🔧 Populating source configurations...\n")
        populate_source_configs()
        print("\n" + "=" * 50)
        list_source_configs()
