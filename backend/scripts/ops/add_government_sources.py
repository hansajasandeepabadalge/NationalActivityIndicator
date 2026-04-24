"""
Add essential government sources for economic indicators
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.agent_models import SourceConfig
from datetime import datetime


GOVERNMENT_SOURCES = [
    {
        "source_name": "export_dev_board",
        "base_url": "https://www.srilankabusiness.com",
        "source_type": "government",
        "language": "en",
        "country": "LK",
        "categories": ["trade", "exports", "economic"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 5,
        "rate_limit_period": 120,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.srilankabusiness.com/news/",
            "article_link_pattern": r"/news/[\w-]+",
            "article_link_selector": "h3 a, article a, div.news-item a",
            "title": ["h1.entry-title", "h1", "h2.post-title"],
            "body": ["div.entry-content", "article.content", "div.post-content"],
            "body_exclude": ".advertisement, .related, .sidebar",
            "date": [".entry-date", ".post-date", "time"],
            "image": ".entry-content img"
        },
        "config_metadata": {
            "display_name": "Export Development Board",
            "priority_level": "critical",
            "default_frequency_minutes": 720,
            "content_type": "trade_data",
            "notes": "Export statistics, trade data, market intelligence"
        }
    },

    {
        "source_name": "sltda",
        "base_url": "https://www.sltda.gov.lk",
        "source_type": "government",
        "language": "en",
        "country": "LK",
        "categories": ["tourism", "economic"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 5,
        "rate_limit_period": 120,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.sltda.gov.lk/en/news",
            "article_link_pattern": r"/en/(news|statistics|reports)/[\w-]+",
            "article_link_selector": "article a, h3 a, div.news-item a",
            "title": ["h1.page-title", "h1.entry-title", "h1"],
            "body": ["div.entry-content", "div.article-content", "article"],
            "body_exclude": ".sidebar, .related-posts",
            "date": [".entry-date", ".publish-date", "time"],
            "image": ".featured-image img, article img"
        },
        "config_metadata": {
            "display_name": "Sri Lanka Tourism Development Authority",
            "priority_level": "critical",
            "default_frequency_minutes": 360,
            "content_type": "tourism_statistics",
            "notes": "Tourist arrivals, tourism revenue, industry statistics"
        }
    }
]


def add_sources():
    """Add government sources to database."""
    db = SessionLocal()

    print("="*80)
    print("🏛️  ADDING ESSENTIAL GOVERNMENT SOURCES")
    print("="*80)

    try:
        for config_data in GOVERNMENT_SOURCES:
            source_name = config_data["source_name"]

            # Check if exists
            existing = db.query(SourceConfig).filter(
                SourceConfig.source_name == source_name
            ).first()

            if existing:
                print(f"\n⚠️  {source_name} already exists - updating...")
                for key, value in config_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                status = "UPDATED"
            else:
                print(f"\n✅ Adding {source_name}...")
                new_config = SourceConfig(**config_data)
                db.add(new_config)
                status = "ADDED"

            display = config_data["config_metadata"]["display_name"]
            print(f"   {status}: {display}")
            print(f"   URL: {config_data['base_url']}")
            print(f"   Category: {', '.join(config_data['categories'])}")

        db.commit()

        print("\n" + "="*80)
        print("✅ Successfully added 2 government sources")
        print("="*80)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_sources()
