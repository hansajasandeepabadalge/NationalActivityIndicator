"""
Test Adaptive Learning System Integration with Layer 1

This script verifies that the Adaptive Learning System is properly
integrated with our Layer 1 components and can:
1. Record scrape results from our scrapers
2. Record validation results from deduplication/impact scoring
3. Provide recommendations for sources
4. Run learning cycles
5. Track system health
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.learning import (
    AdaptiveLearningSystem,
    LearningSystemConfig,
    LearningMode,
    get_learning_system
)
from app.learning.integration import LearningHooks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_learning_system_initialization():
    """Test basic initialization of the learning system."""
    print("\n" + "="*60)
    print("1️⃣ TESTING: Learning System Initialization")
    print("="*60)
    
    try:
        # Get or create learning system
        learning_system = await get_learning_system()
        await learning_system.initialize()
        
        print("✅ Learning system initialized successfully")
        print(f"   Mode: {learning_system.config.mode.value}")
        print(f"   Components enabled:")
        print(f"      - Metrics: {learning_system.config.enable_metrics}")
        print(f"      - Feedback: {learning_system.config.enable_feedback}")
        print(f"      - Auto-tuning: {learning_system.config.enable_auto_tuning}")
        print(f"      - Performance: {learning_system.config.enable_performance_optimization}")
        print(f"      - Quality: {learning_system.config.enable_quality_analysis}")
        
        return learning_system
    except Exception as e:
        print(f"❌ Failed to initialize learning system: {e}")
        return None


async def test_record_scrape_results(learning_system: AdaptiveLearningSystem):
    """Test recording scrape results from our Layer 1 scrapers."""
    print("\n" + "="*60)
    print("2️⃣ TESTING: Recording Scrape Results")
    print("="*60)
    
    try:
        # Simulate scrape results from our sources
        sources = [
            ("daily_ft", "configurable_scraper", True, 17, 1500.0, None),
            ("hiru_news", "configurable_scraper", True, 20, 2100.0, None),
            ("ada_derana", "ada_derana_scraper", True, 26, 1800.0, None),
        ]
        
        for source_id, scraper_type, success, count, latency, error in sources:
            await learning_system.record_scrape_result(
                source_id=source_id,
                scraper_type=scraper_type,
                success=success,
                articles_count=count,
                latency_ms=latency,
                error_type=error
            )
            print(f"   ✅ Recorded: {source_id} - {count} articles in {latency:.0f}ms")
        
        # Also simulate a failed scrape
        await learning_system.record_scrape_result(
            source_id="test_source",
            scraper_type="configurable_scraper",
            success=False,
            articles_count=0,
            latency_ms=5000.0,
            error_type="timeout"
        )
        print(f"   ✅ Recorded: test_source - FAILED (timeout)")
        
        print("\n✅ All scrape results recorded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to record scrape results: {e}")
        return False


async def test_record_validation_results(learning_system: AdaptiveLearningSystem):
    """Test recording validation results from deduplication/impact scoring."""
    print("\n" + "="*60)
    print("3️⃣ TESTING: Recording Validation Results")
    print("="*60)
    
    try:
        # Simulate validation results
        validations = [
            ("article_001", "daily_ft", True, []),
            ("article_002", "daily_ft", True, []),
            ("article_003", "hiru_news", False, [{"type": "duplicate", "detail": "Same as article_001"}]),
            ("article_004", "ada_derana", True, []),
            ("article_005", "ada_derana", False, [{"type": "low_quality", "detail": "Insufficient content"}]),
        ]
        
        for article_id, source_id, valid, issues in validations:
            await learning_system.record_validation_result(
                article_id=article_id,
                source_id=source_id,
                valid=valid,
                issues=issues
            )
            status = "✓ Valid" if valid else f"✗ Invalid ({len(issues)} issues)"
            print(f"   ✅ Recorded: {article_id} from {source_id} - {status}")
        
        print("\n✅ All validation results recorded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to record validation results: {e}")
        return False


async def test_record_article_outcomes(learning_system: AdaptiveLearningSystem):
    """Test recording article outcomes (downstream feedback)."""
    print("\n" + "="*60)
    print("4️⃣ TESTING: Recording Article Outcomes (Feedback Loop)")
    print("="*60)
    
    try:
        # Simulate article outcomes - whether they were used downstream
        outcomes = [
            ("article_001", "daily_ft", True, 0.85, "article_used"),
            ("article_002", "daily_ft", True, 0.72, "article_used"),
            ("article_004", "ada_derana", True, 0.90, "high_quality"),
            ("article_003", "hiru_news", False, 0.30, "article_discarded"),
            ("article_005", "ada_derana", False, 0.20, "low_quality"),
        ]
        
        for article_id, source_id, used, rating, feedback_type in outcomes:
            await learning_system.record_article_outcome(
                article_id=article_id,
                source_id=source_id,
                used_by_downstream=used,
                quality_rating=rating,
                feedback_type=feedback_type
            )
            status = f"Used (rating: {rating:.2f})" if used else f"Discarded ({feedback_type})"
            print(f"   ✅ Recorded: {article_id} - {status}")
        
        print("\n✅ All article outcomes recorded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to record article outcomes: {e}")
        return False


async def test_get_recommendations(learning_system: AdaptiveLearningSystem):
    """Test getting recommendations for sources."""
    print("\n" + "="*60)
    print("5️⃣ TESTING: Getting Source Recommendations")
    print("="*60)
    
    try:
        sources = ["daily_ft", "hiru_news", "ada_derana"]
        
        for source_id in sources:
            recs = await learning_system.get_source_recommendations(source_id)
            print(f"\n   📊 Recommendations for {source_id}:")
            
            # Performance recommendations
            perf = recs.get("performance", {})
            if perf:
                timing = perf.get("optimal_timing", {})
                if timing.get("best_hours"):
                    print(f"      🕐 Best scraping hours: {timing['best_hours'][:3]}")
                concurrency = perf.get("concurrency", 5)
                print(f"      ⚡ Recommended concurrency: {concurrency}")
            
            # Quality analysis
            quality = recs.get("quality", {})
            if quality:
                score = quality.get("quality_score", 0)
                print(f"      📈 Quality score: {score:.2%}")
            
            # Action items
            actions = recs.get("actions", [])
            if actions:
                print(f"      📝 Action items: {len(actions)}")
                for action in actions[:2]:
                    print(f"         - [{action['priority']}] {action['action']}")
        
        print("\n✅ Recommendations retrieved successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to get recommendations: {e}")
        return False


async def test_optimal_parameters(learning_system: AdaptiveLearningSystem):
    """Test getting optimal parameters for scraping."""
    print("\n" + "="*60)
    print("6️⃣ TESTING: Getting Optimal Scraping Parameters")
    print("="*60)
    
    try:
        sources = ["daily_ft", "hiru_news", "ada_derana"]
        
        for source_id in sources:
            params = await learning_system.get_optimal_parameters(source_id)
            print(f"\n   ⚙️ Optimal parameters for {source_id}:")
            print(f"      - Timeout: {params.get('timeout_ms', 30000)}ms")
            print(f"      - Max retries: {params.get('max_retries', 3)}")
            print(f"      - Retry delay: {params.get('retry_delay_ms', 1000)}ms")
            print(f"      - Concurrency: {params.get('concurrency', 5)}")
            print(f"      - Quality threshold: {params.get('quality_threshold', 0.5):.2f}")
        
        print("\n✅ Optimal parameters retrieved successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to get optimal parameters: {e}")
        return False


async def test_system_health(learning_system: AdaptiveLearningSystem):
    """Test getting system health status."""
    print("\n" + "="*60)
    print("7️⃣ TESTING: System Health Monitoring")
    print("="*60)
    
    try:
        health = await learning_system.get_system_health()
        
        print(f"\n   🏥 System Health Status:")
        print(f"      Overall Status: {health.status.upper()}")
        print(f"      Quality Score: {health.quality_score:.2%}")
        print(f"      Quality Trend: {health.quality_trend}")
        print(f"      Active Issues: {health.active_issues}")
        print(f"      Pending Recommendations: {health.pending_recommendations}")
        print(f"      Message: {health.message}")
        
        print(f"\n   📦 Component Status:")
        for component, status in health.components_status.items():
            icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
            print(f"      {icon} {component}: {status}")
        
        print("\n✅ System health retrieved successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to get system health: {e}")
        return False


async def test_learning_cycle(learning_system: AdaptiveLearningSystem):
    """Test running a learning cycle."""
    print("\n" + "="*60)
    print("8️⃣ TESTING: Running Learning Cycle")
    print("="*60)
    
    try:
        result = await learning_system.run_learning_cycle(force=True)
        
        print(f"\n   🔄 Learning Cycle Result:")
        print(f"      Status: {result.get('status', 'unknown')}")
        print(f"      Started at: {result.get('started_at', 'N/A')}")
        print(f"      Completed at: {result.get('completed_at', 'N/A')}")
        print(f"      Recommendations applied: {result.get('recommendations_applied', 0)}")
        print(f"      Parameters adjusted: {result.get('parameters_adjusted', 0)}")
        
        components = result.get("components", {})
        if components:
            print(f"\n   📊 Component Results:")
            for comp_name, comp_data in components.items():
                print(f"      {comp_name}: {comp_data}")
        
        print("\n✅ Learning cycle completed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to run learning cycle: {e}")
        return False


async def test_dashboard_data(learning_system: AdaptiveLearningSystem):
    """Test getting dashboard data for monitoring."""
    print("\n" + "="*60)
    print("9️⃣ TESTING: Dashboard Data for Monitoring")
    print("="*60)
    
    try:
        dashboard = await learning_system.get_dashboard_data()
        
        print(f"\n   📊 Dashboard Overview:")
        
        health = dashboard.get("health", {})
        print(f"      Health Status: {health.get('status', 'unknown')}")
        print(f"      Quality Score: {health.get('quality_score', 0):.2%}")
        print(f"      Quality Trend: {health.get('quality_trend', 'unknown')}")
        
        components = dashboard.get("components", {})
        if components:
            healthy = sum(1 for s in components.values() if s == "healthy")
            print(f"      Components: {healthy}/{len(components)} healthy")
        
        performance = dashboard.get("performance", {})
        if performance:
            print(f"      Performance data available: Yes")
        
        quality = dashboard.get("quality", {})
        if quality:
            print(f"      Quality data available: Yes")
        
        print("\n✅ Dashboard data retrieved successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to get dashboard data: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 ADAPTIVE LEARNING SYSTEM - INTEGRATION TEST")
    print("="*70)
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Initialize learning system
    learning_system = await test_learning_system_initialization()
    if not learning_system:
        print("\n❌ Cannot continue without learning system")
        return
    
    # Run all tests
    results = {}
    
    results["record_scrape"] = await test_record_scrape_results(learning_system)
    results["record_validation"] = await test_record_validation_results(learning_system)
    results["record_outcomes"] = await test_record_article_outcomes(learning_system)
    results["recommendations"] = await test_get_recommendations(learning_system)
    results["optimal_params"] = await test_optimal_parameters(learning_system)
    results["system_health"] = await test_system_health(learning_system)
    results["learning_cycle"] = await test_learning_cycle(learning_system)
    results["dashboard_data"] = await test_dashboard_data(learning_system)
    
    # Summary
    print("\n" + "="*70)
    print("📋 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, passed_test in results.items():
        icon = "✅" if passed_test else "❌"
        print(f"   {icon} {test_name}: {'PASSED' if passed_test else 'FAILED'}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Adaptive Learning System is fully integrated.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review the output above.")
    
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
