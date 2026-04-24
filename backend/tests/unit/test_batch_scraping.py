"""
Batch Source Testing - Test sources in controlled batches
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.scrapers.configurable_scraper import ConfigurableScraper
from app.scrapers.news.ada_derana import AdaDeranaScraper
from app.models.agent_models import SourceConfig
from app.db.session import SessionLocal


async def test_source_batch(batch_name: str, sources: list, max_articles: int = 3):
    """Test a batch of sources."""

    print(f"\n{'='*80}")
    print(f"📦 BATCH TEST: {batch_name}")
    print('='*80)

    db = SessionLocal()
    results = []

    for source_name in sources:
        print(f"\n🔍 Testing: {source_name}")
        print('-'*80)

        try:
            config = db.query(SourceConfig).filter(
                SourceConfig.source_name == source_name,
                SourceConfig.is_active == True
            ).first()

            if not config:
                print(f"❌ Not found or inactive")
                results.append({'source': source_name, 'status': 'inactive', 'articles': 0})
                continue

            # Create scraper
            if config.scraper_class == 'AdaDeranaScraper':
                scraper = AdaDeranaScraper()
            else:
                scraper = ConfigurableScraper(config)

            # Scrape
            articles = await scraper.fetch_articles()
            articles = articles[:max_articles]

            if not articles:
                print(f"⚠️  No articles scraped")
                results.append({'source': source_name, 'status': 'no_articles', 'articles': 0})
                continue

            # Check quality
            valid = sum(1 for a in articles if a.validation.is_valid)
            with_dates = sum(1 for a in articles if a.raw_content.publish_date)
            with_images = sum(1 for a in articles if a.raw_content.images)

            print(f"✅ Scraped: {len(articles)} articles")
            print(f"   Valid: {valid}/{len(articles)}")
            print(f"   With dates: {with_dates}/{len(articles)}")
            print(f"   With images: {with_images}/{len(articles)}")

            # Show sample
            if articles:
                a = articles[0]
                print(f"   Sample: {a.raw_content.title[:50]}...")
                print(f"   Body: {len(a.raw_content.body)} chars")

            results.append({
                'source': source_name,
                'status': 'success',
                'articles': len(articles),
                'valid': valid,
                'quality_score': (valid/len(articles) * 50 + with_dates/len(articles) * 25 + with_images/len(articles) * 25)
            })

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({'source': source_name, 'status': 'error', 'articles': 0, 'error': str(e)})

    db.close()

    # Batch summary
    print(f"\n{'='*80}")
    print(f"📊 BATCH SUMMARY: {batch_name}")
    print('='*80)

    success_count = sum(1 for r in results if r['status'] == 'success')
    total_articles = sum(r.get('articles', 0) for r in results)

    print(f"\n{'Source':<25} {'Status':<15} {'Articles':<10} {'Quality':<10}")
    print('-'*80)
    for r in results:
        status = r['status'].upper()
        articles = str(r.get('articles', 0))
        quality = f"{r.get('quality_score', 0):.0f}%" if 'quality_score' in r else '-'
        print(f"{r['source']:<25} {status:<15} {articles:<10} {quality:<10}")

    print('-'*80)
    print(f"Success: {success_count}/{len(sources)} | Total articles: {total_articles}\n")

    return results


async def main():
    """Run batch tests."""

    print("="*80)
    print("🧪 INCREMENTAL SOURCE TESTING")
    print("="*80)

    # Batch 1: Already working (verify)
    batch1_results = await test_source_batch(
        "Batch 1 - Existing Sources (Verification)",
        ['ada_derana', 'daily_ft', 'hiru_news'],
        max_articles=2
    )

    # Batch 2: New Sri Lankan news
    batch2_results = await test_source_batch(
        "Batch 2 - Sri Lankan News",
        ['daily_mirror', 'news_first', 'the_island', 'sunday_observer'],
        max_articles=2
    )

    # Batch 3: Government sources
    batch3_results = await test_source_batch(
        "Batch 3 - Government Sources",
        ['cbsl', 'govt_info_dept', 'ministry_finance'],
        max_articles=2
    )

    # Overall summary
    print(f"\n{'='*80}")
    print("📈 OVERALL SUMMARY")
    print('='*80)

    all_results = batch1_results + batch2_results + batch3_results
    total_success = sum(1 for r in all_results if r['status'] == 'success')
    total_articles = sum(r.get('articles', 0) for r in all_results)

    print(f"\nTotal sources tested: {len(all_results)}")
    print(f"Successful: {total_success}/{len(all_results)} ({total_success/len(all_results)*100:.0f}%)")
    print(f"Total articles scraped: {total_articles}")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    high_quality = [r for r in all_results if r.get('quality_score', 0) > 75]
    medium_quality = [r for r in all_results if 50 <= r.get('quality_score', 0) <= 75]
    low_quality = [r for r in all_results if 0 < r.get('quality_score', 0) < 50]

    if high_quality:
        print(f"   ✅ Ready for production ({len(high_quality)}): {', '.join(r['source'] for r in high_quality)}")
    if medium_quality:
        print(f"   ⚠️  Needs tuning ({len(medium_quality)}): {', '.join(r['source'] for r in medium_quality)}")
    if low_quality:
        print(f"   🔧 Requires fixes ({len(low_quality)}): {', '.join(r['source'] for r in low_quality)}")

    failed = [r for r in all_results if r['status'] in ['error', 'no_articles', 'inactive']]
    if failed:
        print(f"   ❌ Failed ({len(failed)}): {', '.join(r['source'] for r in failed)}")

    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
