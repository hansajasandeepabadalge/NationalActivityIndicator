"""
Populate Multilingual and Financial Source Configurations

Adds Sinhala, Tamil, and Financial news sources to expand coverage
from 19 to 27+ sources.

Usage:
    cd backend
    python scripts/populate_multilingual_sources.py
    python scripts/populate_multilingual_sources.py --list
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
# Multilingual & Financial Source Configurations
# ==============================================

MULTILINGUAL_SOURCES = [
    # ============================================
    # Lankadeepa - Sinhala (Priority 1)
    # ============================================
    {
        "source_name": "lankadeepa",
        "base_url": "https://www.lankadeepa.lk",
        "source_type": "news",
        "language": "si",
        "country": "LK",
        "categories": ["general", "breaking"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "requires_javascript": False,
        "is_active": True,
        "selectors": {
            # Main news listing
            "list_url": "https://www.lankadeepa.lk/latest_news",
            
            # Article link patterns
            "article_link_pattern": r"/article/",
            "article_link_selector": "a.article-link, a[href*='/article/']",
            
            # Content extraction
            "title": ["h1.article-title", "h1", "meta[property='og:title']"],
            "body": ["div.article-content", "div.article-body", "article", ".content-area"],
            "body_exclude": ".advertisement, .related-articles, .social-share, .comments",
            
            # Metadata
            "date": [".article-date", "time", ".publish-date", "span.date"],
            "date_format": "%Y-%m-%d",
            "author": [".author-name", ".byline", ".article-author"],
            "image": [".article-content img", ".featured-image img", "img[src*='article']"]
        },
        "config_metadata": {
            "display_name": "Lankadeepa (ලංකාදීප)",
            "priority_level": "high",
            "default_frequency_minutes": 45,
            "notes": "Major Sinhala newspaper. Translation required for Layer 2 processing."
        }
    },
    
    # ============================================
    # Divaina - Sinhala (Priority 1)
    # ============================================
    {
        "source_name": "divaina",
        "base_url": "https://www.divaina.com",
        "source_type": "news",
        "language": "si",
        "country": "LK",
        "categories": ["general", "political", "economic"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.divaina.com/category/news",
            "article_link_pattern": r"/\d{4}/\d{2}/\d{2}/",
            "article_link_selector": "a[href*='/category/'], a.post-link",
            
            "title": ["h1.entry-title", "h1.post-title", "h1", "meta[property='og:title']"],
            "body": ["div.entry-content", "div.post-content", "article", ".content"],
            "body_exclude": ".advertisement, .ads, .related-posts, .social-buttons",
            
            "date": ["time.entry-date", ".post-date", "meta[property='article:published_time']"],
            "author": [".author-name", ".entry-author"],
            "image": [".entry-content img", ".post-thumbnail img"]
        },
        "config_metadata": {
            "display_name": "Divaina (දිවයින)",
            "priority_level": "high",
            "default_frequency_minutes": 45,
            "notes": "Established Sinhala daily newspaper"
        }
    },
    
    # ============================================
    # Dinamina - Sinhala Government-aligned (Priority 1)
    # ============================================
    {
        "source_name": "dinamina",
        "base_url": "https://www.dinamina.lk",
        "source_type": "news",
        "language": "si",
        "country": "LK",
        "categories": ["general", "political", "government"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.dinamina.lk/category/news",
            "article_link_selector": "a.article-link, a[href*='/article/']",
            
            "title": ["h1.article-title", "h1", "meta[property='og:title']"],
            "body": ["div.article-body", "div.content", "article"],
            "body_exclude": ".ads, .related, .comments",
            
            "date": [".date", "time", ".publish-time"],
            "author": [".author", ".byline"],
            "image": [".article-body img", ".featured-img"]
        },
        "config_metadata": {
            "display_name": "Dinamina (දිනමිණ)",
            "priority_level": "medium",
            "default_frequency_minutes": 60,
            "notes": "Government-aligned Sinhala newspaper"
        }
    },
    
    # ============================================
    # Thinakaran - Tamil (Priority 1)
    # ============================================
    {
        "source_name": "thinakaran",
        "base_url": "https://www.thinakaran.lk",
        "source_type": "news",
        "language": "ta",
        "country": "LK",
        "categories": ["general", "breaking"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.thinakaran.lk/category/news",
            "article_link_pattern": r"/\d{4}/\d{2}/",
            "article_link_selector": "a.article-link, a[href*='/category/']",
            
            "title": ["h1.post-title", "h1", "meta[property='og:title']"],
            "body": ["div.post-content", "div.entry-content", "article"],
            "body_exclude": ".advertisement, .related-posts, .social-share",
            
            "date": [".post-date", "time", ".entry-date"],
            "author": [".author-name", ".entry-author"],
            "image": [".post-content img", ".post-thumbnail"]
        },
        "config_metadata": {
            "display_name": "Thinakaran (தினகரன்)",
            "priority_level": "high",
            "default_frequency_minutes": 45,
            "notes": "Major Tamil newspaper. Translation required."
        }
    },
    
    # ============================================
    # Virakesari - Tamil (Priority 1)
    # ============================================
    {
        "source_name": "virakesari",
        "base_url": "https://www.virakesari.lk",
        "source_type": "news",
        "language": "ta",
        "country": "LK",
        "categories": ["general", "political", "economic"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.virakesari.lk/article",
            "article_link_selector": "a.article-link, a[href*='/article/']",
            
            "title": ["h1.article-title", "h1", "meta[property='og:title']"],
            "body": ["div.article-content", "article", ".content"],
            "body_exclude": ".advertisement, .related, .social-buttons",
            
            "date": [".article-date", "time", ".date"],
            "author": [".author", ".byline"],
            "image": [".article-content img", ".featured-image"]
        },
        "config_metadata": {
            "display_name": "Virakesari (வீரகேசரி)",
            "priority_level": "high",
            "default_frequency_minutes": 45,
            "notes": "Established Tamil daily newspaper"
        }
    },
]

FINANCIAL_SOURCES = [
    # ============================================
    # EconomyNext - Economic Analysis (Priority 2)
    # ============================================
    {
        "source_name": "economynext",
        "base_url": "https://economynext.com",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["economic", "financial", "business"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://economynext.com/category/news/",
            "article_link_pattern": r"/\d{4}/\d{2}/",
            "article_link_selector": "a.article-link, h2.entry-title a",
            
            "title": ["h1.entry-title", "h1.article-title", "h1", "meta[property='og:title']"],
            "body": ["div.entry-content", "div.article-body", "article"],
            "body_exclude": ".advertisement, .related-articles, .social-share",
            
            "date": ["time.entry-date", ".published", "meta[property='article:published_time']"],
            "author": [".author-name", ".entry-author", ".byline"],
            "image": [".entry-content img", ".featured-image img"]
        },
        "config_metadata": {
            "display_name": "EconomyNext",
            "priority_level": "high",
            "default_frequency_minutes": 30,
            "notes": "Premier economic and financial news source. High priority for economic indicators."
        }
    },
    
    # ============================================
    # Lanka Business Online (Priority 2)
    # ============================================
    {
        "source_name": "lbo",
        "base_url": "https://www.lankabusinessonline.com",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["economic", "business", "financial"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.lankabusinessonline.com/news/",
            "article_link_selector": "a.article-title, h3.entry-title a",
            
            "title": ["h1.entry-title", "h1", "meta[property='og:title']"],
            "body": ["div.entry-content", "div.article-content", "article"],
            "body_exclude": ".advertisement, .related-content, .social-share",
            
            "date": [".entry-date", "time", ".publish-date"],
            "author": [".author-name", ".entry-author"],
            "image": [".entry-content img", ".post-thumbnail"]
        },
        "config_metadata": {
            "display_name": "Lanka Business Online (LBO)",
            "priority_level": "high",
            "default_frequency_minutes": 30,
            "notes": "Business and economic news with market focus"
        }
    },
    
    # ============================================
    # Newswire.lk - Comprehensive Coverage (Priority 3)
    # ============================================
    {
        "source_name": "newswire",
        "base_url": "https://www.newswire.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general", "breaking"],
        "reliability_tier": "standard",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.newswire.lk/",
            "article_link_selector": "a.post-link, a[href*='/news/']",
            
            "title": ["h1.post-title", "h1", "meta[property='og:title']"],
            "body": ["div.post-content", "article", ".content"],
            "body_exclude": ".ads, .related-posts",
            
            "date": [".post-date", "time", ".date"],
            "author": [".author", ".byline"],
            "image": [".post-content img", ".featured-image"]
        },
        "config_metadata": {
            "display_name": "Newswire.lk",
            "priority_level": "medium",
            "default_frequency_minutes": 60,
            "notes": "Comprehensive news coverage"
        }
    },
]

# Combine all sources
ALL_NEW_SOURCES = MULTILINGUAL_SOURCES + FINANCIAL_SOURCES


def populate_sources():
    """Insert or update source configurations in the database."""
    db = SessionLocal()
    
    try:
        inserted = 0
        updated = 0
        
        print("=" * 60)
        print("POPULATING MULTILINGUAL & FINANCIAL SOURCES")
        print("=" * 60)
        print()
        
        for config_data in ALL_NEW_SOURCES:
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
                print(f"  ✓ Updated: {config_data['source_name']} ({config_data['config_metadata']['display_name']})")
            else:
                # Insert new configuration
                new_config = SourceConfig(**config_data)
                db.add(new_config)
                inserted += 1
                print(f"  + Inserted: {config_data['source_name']} ({config_data['config_metadata']['display_name']})")
        
        db.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Successfully processed {inserted + updated} source configs")
        print(f"   - Inserted: {inserted}")
        print(f"   - Updated: {updated}")
        print("=" * 60)
        
        # Show summary by language
        print()
        print("📊 LANGUAGE DISTRIBUTION:")
        sinhala = len([s for s in ALL_NEW_SOURCES if s['language'] == 'si'])
        tamil = len([s for s in ALL_NEW_SOURCES if s['language'] == 'ta'])
        english = len([s for s in ALL_NEW_SOURCES if s['language'] == 'en'])
        print(f"   - Sinhala (si): {sinhala} sources")
        print(f"   - Tamil (ta): {tamil} sources")
        print(f"   - English (en): {english} sources")
        
        # Show all active sources
        active_sources = db.query(SourceConfig).filter(
            SourceConfig.is_active == True
        ).all()
        
        print()
        print(f"📰 TOTAL ACTIVE SOURCES: {len(active_sources)}")
        print()
        
        # Group by language
        by_language = {}
        for source in active_sources:
            lang = source.language
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(source)
        
        for lang, sources in sorted(by_language.items()):
            lang_name = {"en": "English", "si": "Sinhala", "ta": "Tamil"}.get(lang, lang)
            print(f"  {lang_name} ({len(sources)}):")
            for source in sources:
                display = source.config_metadata.get('display_name', source.source_name) if source.config_metadata else source.source_name
                print(f"    - {source.source_name} ({display})")
        
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
        configs = db.query(SourceConfig).order_by(
            SourceConfig.language, 
            SourceConfig.source_name
        ).all()
        
        print(f"\n📋 ALL SOURCE CONFIGURATIONS ({len(configs)}):\n")
        print(f"{'Name':<20} {'Display Name':<35} {'Lang':<6} {'Type':<12} {'Active':<8}")
        print("-" * 90)
        
        for config in configs:
            active = "✅" if config.is_active else "❌"
            display = config.config_metadata.get('display_name', '')[:33] if config.config_metadata else ''
            print(f"{config.source_name:<20} {display:<35} {config.language:<6} {config.source_type:<12} {active:<8}")
            
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage multilingual source configurations")
    parser.add_argument("--list", action="store_true", help="List all source configs")
    parser.add_argument("--populate", action="store_true", help="Populate/update source configs")
    
    args = parser.parse_args()
    
    if args.list:
        list_source_configs()
    elif args.populate:
        populate_sources()
    else:
        # Default: populate then list
        populate_sources()
        print("\n" + "=" * 60)
        list_source_configs()
