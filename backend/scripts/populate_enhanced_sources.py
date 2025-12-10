"""
Enhanced Source Configuration - Add 15+ News & Government Sites

This script expands the scraping coverage to include:
- Additional Sri Lankan news sources
- International news (BBC, Reuters, Al Jazeera)
- Government/Official sources (CBSL, Statistics, Finance Ministry)
- Specialized sources (Think tanks, research institutes)

Usage:
    cd backend
    python scripts/populate_enhanced_sources.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.agent_models import SourceConfig
from datetime import datetime


ENHANCED_SOURCE_CONFIGS = [
    # ============================================
    # ACTIVATE EXISTING PLACEHOLDERS
    # ============================================

    {
        "source_name": "daily_mirror",
        "base_url": "https://www.dailymirror.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general", "business", "sports"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.dailymirror.lk/breaking-news",
            "article_link_pattern": r"/-\d+",
            "article_link_selector": "div.article-list a, h3.entry-title a",
            "title": ["h1.entry-title", "h1.title", "h1"],
            "body": "div.entry-content, div.article-body, div.body-text",
            "body_exclude": ".advertisement, .related-articles, .social-share, .author-box",
            "date": ["time.entry-date", "span.date", ".posted-on"],
            "date_format": "%Y-%m-%d",
            "author": [".author-name", ".byline", "span.author"],
            "image": "div.entry-content img, img.featured-image"
        },
        "config_metadata": {
            "display_name": "Daily Mirror",
            "priority_level": "high",
            "default_frequency_minutes": 30,
            "notes": "Major English daily newspaper"
        }
    },

    {
        "source_name": "news_first",
        "base_url": "https://www.newsfirst.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general", "breaking"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.newsfirst.lk/category/latest-news/",
            "article_link_pattern": r"/\d{4}/\d{2}/\d{2}/[\w-]+",
            "article_link_selector": "h3.entry-title a, article a",
            "title": ["h1.entry-title", "h1.post-title", "h1"],
            "body": "div.entry-content, div.post-content, article.post",
            "body_exclude": ".advertisement, .related, .comments, .social-share",
            "date": ["time.entry-date", "span.posted-on", ".date"],
            "date_format": "%B %d, %Y",
            "author": ".author vcard, .author-name",
            "image": "div.entry-content img, img.attachment-large"
        },
        "config_metadata": {
            "display_name": "News First",
            "priority_level": "high",
            "default_frequency_minutes": 30,
            "notes": "Leading 24/7 news channel"
        }
    },

    {
        "source_name": "cbsl",
        "base_url": "https://www.cbsl.gov.lk",
        "source_type": "government",
        "language": "en",
        "country": "LK",
        "categories": ["economic", "financial", "government", "monetary_policy"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 5,
        "rate_limit_period": 120,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.cbsl.gov.lk/en/news",
            "article_link_pattern": r"/en/(news|press-releases|announcements)",
            "article_link_selector": "div.news-item a, h3 a, article a",
            "title": ["h1.page-title", "h1.entry-title", "h1"],
            "body": ["div.field-name-body, div.content-area, article.content"],
            "body_exclude": ".menu, .sidebar, .footer",
            "date": [".field-name-post-date", ".date", "time"],
            "date_format": "%d %B %Y",
            "image": ".field-name-field-image img, article img"
        },
        "config_metadata": {
            "display_name": "Central Bank of Sri Lanka",
            "priority_level": "critical",
            "default_frequency_minutes": 240,
            "content_type": "official_announcement",
            "notes": "Critical for monetary policy, interest rates, economic indicators. May include PDF reports."
        }
    },

    # ============================================
    # NEW SRI LANKAN NEWS SOURCES
    # ============================================

    {
        "source_name": "sunday_observer",
        "base_url": "https://www.sundayobserver.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general", "analysis", "opinion"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.sundayobserver.lk/news",
            "article_link_pattern": r"/news/[\w-]+",
            "article_link_selector": "h2.entry-title a, div.article-list a",
            "title": ["h1.entry-title", "h1"],
            "body": "div.entry-content, div.article-content",
            "body_exclude": ".advertisement, .related",
            "date": ["time.entry-date", ".date"],
            "author": ".author-name"
        },
        "config_metadata": {
            "display_name": "Sunday Observer",
            "priority_level": "medium",
            "default_frequency_minutes": 120,
            "notes": "Government-owned weekly with in-depth analysis"
        }
    },

    {
        "source_name": "the_island",
        "base_url": "https://island.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general", "politics", "business"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://island.lk/category/latest-news/",
            "article_link_pattern": r"/[\w-]+/$",
            "article_link_selector": "h2.entry-title a",
            "title": ["h1.entry-title", "h1"],
            "body": "div.entry-content",
            "body_exclude": ".advertisement, .related-posts",
            "date": "time.entry-date",
            "author": ".author"
        },
        "config_metadata": {
            "display_name": "The Island",
            "priority_level": "medium",
            "default_frequency_minutes": 60,
            "notes": "Independent English daily"
        }
    },

    {
        "source_name": "ceylon_today",
        "base_url": "https://ceylontoday.lk",
        "source_type": "news",
        "language": "en",
        "country": "LK",
        "categories": ["general", "politics"],
        "reliability_tier": "standard",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://ceylontoday.lk/news",
            "article_link_pattern": r"/news/[\w-]+",
            "article_link_selector": "h2 a, div.post a",
            "title": "h1",
            "body": "div.content, div.article-body",
            "body_exclude": ".ads, .related",
            "date": ".date, time",
            "author": ".author"
        },
        "config_metadata": {
            "display_name": "Ceylon Today",
            "priority_level": "medium",
            "default_frequency_minutes": 90,
            "notes": "General news coverage"
        }
    },

    # ============================================
    # INTERNATIONAL NEWS SOURCES
    # ============================================

    {
        "source_name": "bbc_asia",
        "base_url": "https://www.bbc.com",
        "source_type": "news",
        "language": "en",
        "country": "GB",
        "categories": ["international", "asia", "sri_lanka"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 5,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.bbc.com/news/world/asia",
            "article_link_pattern": r"/news/[\w-]+-\d+",
            "article_link_selector": "a.gs-c-promo-heading",
            "title": ["h1#main-heading", "h1.story-headline", "h1"],
            "body": ["article[role='article']", "div.story-body", "div.article__body"],
            "body_exclude": ".media-placeholder, .related-topics, .story-promo",
            "date": ["time.date", "time", ".date"],
            "date_format": "%Y-%m-%d",
            "image": "figure.image img, div.article__image img"
        },
        "config_metadata": {
            "display_name": "BBC News - Asia",
            "priority_level": "high",
            "default_frequency_minutes": 60,
            "notes": "International perspective on regional news"
        }
    },

    {
        "source_name": "reuters_sri_lanka",
        "base_url": "https://www.reuters.com",
        "source_type": "news",
        "language": "en",
        "country": "US",
        "categories": ["international", "business", "sri_lanka"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 5,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.reuters.com/world/asia-pacific/",
            "article_link_pattern": r"/world/[\w-]+/[\w-]+-\d{4}-\d{2}-\d{2}/",
            "article_link_selector": "a[data-testid='Heading']",
            "title": ["h1[data-testid='Heading']", "h1"],
            "body": ["div.article-body__content__17Yit", "div.StandardArticleBody_body"],
            "body_exclude": ".Slideshow, .RelatedArticles",
            "date": ["time[datetime]", "time"],
            "date_format": "iso8601",
            "image": "div.article-body img"
        },
        "config_metadata": {
            "display_name": "Reuters - Sri Lanka",
            "priority_level": "high",
            "default_frequency_minutes": 90,
            "notes": "Financial and business news focus"
        }
    },

    {
        "source_name": "aljazeera_asia",
        "base_url": "https://www.aljazeera.com",
        "source_type": "news",
        "language": "en",
        "country": "QA",
        "categories": ["international", "asia"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.aljazeera.com/asia/",
            "article_link_pattern": r"/news/\d{4}/\d{1,2}/\d{1,2}/",
            "article_link_selector": "h3 a, article a",
            "title": ["h1.article-heading", "h1"],
            "body": ["div.wysiwyg", "div.article-body"],
            "body_exclude": ".ad, .related-articles",
            "date": ["span.date-simple", ".date"],
            "author": ".author-name",
            "image": "figure.article-featured-image img"
        },
        "config_metadata": {
            "display_name": "Al Jazeera - Asia",
            "priority_level": "medium",
            "default_frequency_minutes": 120,
            "notes": "International coverage with Middle East perspective"
        }
    },

    # ============================================
    # GOVERNMENT & OFFICIAL SOURCES
    # ============================================

    {
        "source_name": "dept_census_stats",
        "base_url": "http://www.statistics.gov.lk",
        "source_type": "government",
        "language": "en",
        "country": "LK",
        "categories": ["statistics", "economic", "demographic"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 3,
        "rate_limit_period": 120,
        "is_active": True,
        "selectors": {
            "list_url": "http://www.statistics.gov.lk/LatestReports",
            "article_link_pattern": r"/(Reports|LatestReports)",
            "article_link_selector": "div.report-item a, table a",
            "title": ["h1.report-title", "h1", "h2"],
            "body": ["div.report-content", "div.content", "table"],
            "date": [".release-date", ".date"],
            "date_format": "%Y-%m-%d"
        },
        "config_metadata": {
            "display_name": "Department of Census & Statistics",
            "priority_level": "critical",
            "default_frequency_minutes": 360,
            "content_type": "statistical_report",
            "document_formats": ["html", "pdf", "xlsx"],
            "notes": "Official statistics - inflation, GDP, employment, trade. Often PDF reports."
        }
    },

    {
        "source_name": "ministry_finance",
        "base_url": "https://www.treasury.gov.lk",
        "source_type": "government",
        "language": "en",
        "country": "LK",
        "categories": ["economic", "fiscal_policy", "government"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 3,
        "rate_limit_period": 120,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.treasury.gov.lk/news-and-media/press-releases",
            "article_link_pattern": r"/(press-releases|announcements)",
            "article_link_selector": "div.press-release a, article a",
            "title": ["h1.title", "h1"],
            "body": ["div.body-content", "article.content"],
            "date": [".release-date", ".date"],
            "date_format": "%d/%m/%Y"
        },
        "config_metadata": {
            "display_name": "Ministry of Finance",
            "priority_level": "critical",
            "default_frequency_minutes": 360,
            "content_type": "official_announcement",
            "notes": "Fiscal policy, budget, taxation, debt management"
        }
    },

    {
        "source_name": "govt_info_dept",
        "base_url": "https://www.news.lk",
        "source_type": "government",
        "language": "en",
        "country": "LK",
        "categories": ["government", "policy"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.news.lk/news",
            "article_link_pattern": r"/news/[\w-]+",
            "article_link_selector": "h2 a, div.news-item a",
            "title": ["h1.entry-title", "h1"],
            "body": "div.entry-content, div.article-body",
            "body_exclude": ".sidebar, .related",
            "date": [".entry-date", ".date"],
            "author": ".author"
        },
        "config_metadata": {
            "display_name": "Government Information Department",
            "priority_level": "high",
            "default_frequency_minutes": 120,
            "content_type": "official_news",
            "notes": "Official government announcements and news"
        }
    },

    {
        "source_name": "parliament_lk",
        "base_url": "https://www.parliament.lk",
        "source_type": "government",
        "language": "en",
        "country": "LK",
        "categories": ["legislative", "policy", "government"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 3,
        "rate_limit_period": 120,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.parliament.lk/en/news-en",
            "article_link_pattern": r"/en/news-en/",
            "article_link_selector": "div.news-item a",
            "title": ["h1.page-title", "h1"],
            "body": ["div.field-name-body", "div.content"],
            "date": [".field-name-post-date", ".date"]
        },
        "config_metadata": {
            "display_name": "Parliament of Sri Lanka",
            "priority_level": "high",
            "default_frequency_minutes": 360,
            "content_type": "legislative",
            "notes": "Bills, acts, parliamentary debates, committee reports"
        }
    },

    # ============================================
    # SPECIALIZED SOURCES (Think Tanks, Research)
    # ============================================

    {
        "source_name": "ips_sri_lanka",
        "base_url": "https://www.ips.lk",
        "source_type": "research",
        "language": "en",
        "country": "LK",
        "categories": ["research", "policy", "economic"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 5,
        "rate_limit_period": 120,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.ips.lk/publications/",
            "article_link_pattern": r"/(publications|research)",
            "article_link_selector": "h3 a, div.publication a",
            "title": ["h1.entry-title", "h1"],
            "body": "div.entry-content, div.publication-content",
            "body_exclude": ".sidebar, .related",
            "date": [".entry-date", ".publish-date"],
            "author": ".author-name"
        },
        "config_metadata": {
            "display_name": "Institute of Policy Studies",
            "priority_level": "high",
            "default_frequency_minutes": 720,
            "content_type": "research_report",
            "notes": "Economic research, policy analysis, think tank publications"
        }
    },

    {
        "source_name": "verite_research",
        "base_url": "https://www.veriteresearch.org",
        "source_type": "research",
        "language": "en",
        "country": "LK",
        "categories": ["research", "policy", "governance"],
        "reliability_tier": "premium",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 5,
        "rate_limit_period": 120,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.veriteresearch.org/publications/",
            "article_link_pattern": r"/publications/[\w-]+",
            "article_link_selector": "div.publication a, h3 a",
            "title": ["h1.page-title", "h1"],
            "body": "div.publication-content, article.content",
            "date": ".publication-date",
            "author": ".authors"
        },
        "config_metadata": {
            "display_name": "Verité Research",
            "priority_level": "high",
            "default_frequency_minutes": 720,
            "content_type": "research_report",
            "notes": "Independent think tank - governance, policy, economic research"
        }
    },

    {
        "source_name": "ceylon_chamber",
        "base_url": "https://www.chamber.lk",
        "source_type": "business",
        "language": "en",
        "country": "LK",
        "categories": ["business", "trade", "economic"],
        "reliability_tier": "trusted",
        "scraper_class": "ConfigurableScraper",
        "rate_limit_requests": 10,
        "rate_limit_period": 60,
        "is_active": True,
        "selectors": {
            "list_url": "https://www.chamber.lk/news",
            "article_link_pattern": r"/news/[\w-]+",
            "article_link_selector": "h2 a, div.news-item a",
            "title": ["h1.entry-title", "h1"],
            "body": "div.entry-content, div.news-content",
            "date": ".entry-date",
            "author": ".author"
        },
        "config_metadata": {
            "display_name": "Ceylon Chamber of Commerce",
            "priority_level": "medium",
            "default_frequency_minutes": 360,
            "content_type": "business_news",
            "notes": "Business community perspectives, trade policy, economic trends"
        }
    }
]


def populate_enhanced_sources():
    """Populate database with enhanced source configurations."""
    db = SessionLocal()

    try:
        inserted = 0
        updated = 0

        print(f"\n🔧 Processing {len(ENHANCED_SOURCE_CONFIGS)} source configurations...")
        print("=" * 80)

        for config_data in ENHANCED_SOURCE_CONFIGS:
            source_name = config_data["source_name"]

            # Check if exists
            existing = db.query(SourceConfig).filter(
                SourceConfig.source_name == source_name
            ).first()

            if existing:
                # Update
                for key, value in config_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                updated += 1
                status = "✏️  UPDATED"
            else:
                # Insert
                new_config = SourceConfig(**config_data)
                db.add(new_config)
                inserted += 1
                status = "✅ INSERTED"

            display_name = config_data.get("config_metadata", {}).get("display_name", source_name)
            source_type = config_data.get("source_type", "unknown")
            active = "🟢" if config_data.get("is_active", False) else "🔴"

            print(f"{status} | {active} | {source_type:12} | {source_name:25} | {display_name}")

        db.commit()

        print("=" * 80)
        print(f"\n✅ Successfully processed {inserted + updated} configurations")
        print(f"   📊 Inserted: {inserted}")
        print(f"   📝 Updated:  {updated}")

        # Summary by type and status
        active_sources = db.query(SourceConfig).filter(
            SourceConfig.is_active == True
        ).all()

        by_type = {}
        for source in active_sources:
            stype = source.source_type or "unknown"
            by_type[stype] = by_type.get(stype, 0) + 1

        print(f"\n📰 Active Sources Summary ({len(active_sources)} total):")
        for stype, count in sorted(by_type.items()):
            print(f"   - {stype.title():15} : {count} sources")

        print("\n🌍 Coverage Breakdown:")
        news_count = by_type.get("news", 0)
        gov_count = by_type.get("government", 0)
        research_count = by_type.get("research", 0) + by_type.get("business", 0)
        print(f"   - News Sources:        {news_count}")
        print(f"   - Government Sources:  {gov_count}")
        print(f"   - Research/Business:   {research_count}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def list_all_sources():
    """List all sources with details."""
    db = SessionLocal()

    try:
        configs = db.query(SourceConfig).order_by(
            SourceConfig.source_type,
            SourceConfig.reliability_tier,
            SourceConfig.source_name
        ).all()

        print(f"\n📋 All Source Configurations ({len(configs)} total)\n")
        print(f"{'Source Name':<25} {'Display Name':<35} {'Type':<12} {'Tier':<12} {'Active':<8} {'Scraper'}")
        print("=" * 130)

        current_type = None
        for config in configs:
            if config.source_type != current_type:
                current_type = config.source_type
                print(f"\n--- {current_type.upper() if current_type else 'UNKNOWN'} ---")

            active = "🟢 YES" if config.is_active else "🔴 NO"
            scraper = config.scraper_class or "ConfigurableScraper"
            display_name = (config.config_metadata or {}).get("display_name", config.source_name)

            print(f"{config.source_name:<25} {display_name[:33]:<35} {config.source_type:<12} {config.reliability_tier:<12} {active:<8} {scraper}")

        print("\n" + "=" * 130)

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced source configuration management")
    parser.add_argument("--list", action="store_true", help="List all sources")
    parser.add_argument("--populate", action="store_true", help="Populate enhanced sources")

    args = parser.parse_args()

    if args.list:
        list_all_sources()
    elif args.populate:
        populate_enhanced_sources()
    else:
        # Default: populate then list
        populate_enhanced_sources()
        print("\n" + "=" * 80 + "\n")
        list_all_sources()
