"""
Test script for Layer 4 Database Integration (Phase 6)

Tests:
1. PostgreSQL storage (insights, recommendations)
2. MongoDB storage (reasoning, narratives)
3. Redis caching
4. Complete orchestrator pipeline
5. TimescaleDB hypertables
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from pymongo import MongoClient
from redis import Redis
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.layer4.integration.layer4_orchestrator import Layer4Orchestrator
from app.layer4.mock_data.layer3_mock_generator import MockLayer3Generator
from app.layer4.mock_data.company_profiles_mock import MockCompanyGenerator
from app.layer4.storage.insight_storage import InsightStorageService
from app.layer4.storage.reasoning_storage import ReasoningStorageService
from app.layer4.storage.cache_manager import InsightCacheManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0

    def add_result(self, test_name: str, passed: bool, message: str = ""):
        self.tests.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        if passed:
            self.passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {test_name} - {message}")

    def print_summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {len(self.tests)}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Pass Rate: {(self.passed / len(self.tests) * 100):.1f}%")
        print("="*70)

        if self.failed > 0:
            print("\nFailed Tests:")
            for test in self.tests:
                if not test['passed']:
                    print(f"  - {test['test']}: {test['message']}")


def test_database_connections(results: TestResults):
    """Test 1: Verify database connections"""
    print("\n=== Test 1: Database Connections ===")

    # PostgreSQL
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        results.add_result("PostgreSQL Connection", True)
    except Exception as e:
        results.add_result("PostgreSQL Connection", False, str(e))

    # MongoDB
    try:
        mongo_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')
        results.add_result("MongoDB Connection", True)
    except Exception as e:
        results.add_result("MongoDB Connection", False, str(e))

    # Redis
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        results.add_result("Redis Connection", True)
    except Exception as e:
        results.add_result("Redis Connection", False, str(e))


def test_postgresql_storage(results: TestResults):
    """Test 2: PostgreSQL storage service"""
    print("\n=== Test 2: PostgreSQL Storage ===")

    db = SessionLocal()
    storage = InsightStorageService(db)

    try:
        # Generate mock data
        mock_layer3 = MockLayer3Generator()
        indicators = mock_layer3.generate_indicators(
            company_id="test_001",
            industry="retail",
            business_scale="large",
            timestamp=datetime.now(),
            scenario="supply_disruption"
        )

        # Create mock risk
        from app.layer4.schemas.risk_schemas import DetectedRisk
        from decimal import Decimal

        risk = DetectedRisk(
            risk_code="TEST_RISK_001",
            company_id="test_001",
            title="Test Supply Chain Risk",
            description="Test risk for storage validation",
            category="operational",
            probability=Decimal("0.75"),
            impact=Decimal("8.0"),
            urgency=4,
            confidence=Decimal("0.85"),
            final_score=Decimal("40.5"),
            severity_level="critical",
            triggering_indicators={"test_indicator": {"value": 45, "threshold": 50}},
            detection_method="rule_based",
            reasoning="Test reasoning",
            is_urgent=True,
            requires_immediate_action=True
        )

        # Store insight
        insight_id = storage.store_business_insight(risk, "test_001")
        results.add_result("Store Business Insight", insight_id > 0, f"insight_id: {insight_id}")

        # Store recommendations
        recommendations = [
            {
                "category": "immediate",
                "priority": 1,
                "action_title": "Test Action 1",
                "action_description": "Test action description",
                "responsible_role": "Test Manager",
                "timeframe": "24 hours"
            }
        ]
        rec_ids = storage.store_recommendations(insight_id, recommendations)
        results.add_result("Store Recommendations", len(rec_ids) > 0, f"Stored {len(rec_ids)} recommendations")

        # Retrieve insights
        active = storage.get_active_insights("test_001")
        results.add_result("Retrieve Active Insights", len(active) > 0, f"Found {len(active)} insights")

        # Acknowledge insight
        success = storage.acknowledge_insight(insight_id, "test_user")
        results.add_result("Acknowledge Insight", success)

    except Exception as e:
        results.add_result("PostgreSQL Storage", False, str(e))
        logger.exception("PostgreSQL storage test failed")
    finally:
        db.close()


def test_mongodb_storage(results: TestResults):
    """Test 3: MongoDB storage service"""
    print("\n=== Test 3: MongoDB Storage ===")

    mongo_client = MongoClient(settings.MONGODB_URL)
    storage = ReasoningStorageService(mongo_client)

    try:
        # Create mock risk
        from app.layer4.schemas.risk_schemas import DetectedRisk, RiskScoreBreakdown
        from decimal import Decimal

        risk = DetectedRisk(
            risk_code="TEST_RISK_002",
            company_id="test_002",
            title="Test Risk for MongoDB",
            description="Test risk for MongoDB storage",
            category="financial",
            probability=Decimal("0.70"),
            impact=Decimal("7.5"),
            urgency=3,
            confidence=Decimal("0.80"),
            final_score=Decimal("35.0"),
            severity_level="high",
            triggering_indicators={"indicator1": "value1"},
            detection_method="pattern",
            reasoning="Pattern-based detection test",
            is_urgent=False,
            requires_immediate_action=False
        )

        breakdown = RiskScoreBreakdown(
            probability=Decimal("0.70"),
            probability_reasoning="Test probability reasoning",
            impact=Decimal("7.5"),
            impact_reasoning="Test impact reasoning",
            urgency=3,
            urgency_reasoning="Test urgency reasoning",
            confidence=Decimal("0.80"),
            confidence_source="Test confidence source",
            final_score=Decimal("35.0"),
            severity="high"
        )

        # Store reasoning
        reasoning_id = storage.store_detection_reasoning(
            insight_id=999,
            risk=risk,
            score_breakdown=breakdown
        )
        results.add_result("Store Detection Reasoning", reasoning_id is not None)

        # Store narrative
        narrative = {
            "emoji": "⚠️",
            "headline": "Test Headline",
            "summary": "Test summary",
            "detailed_explanation": "Test explanation"
        }
        narrative_id = storage.store_narrative(
            insight_id=999,
            company_id="test_002",
            narrative=narrative
        )
        results.add_result("Store Narrative", narrative_id is not None)

        # Retrieve reasoning
        retrieved_reasoning = storage.get_reasoning(999)
        results.add_result("Retrieve Reasoning", retrieved_reasoning is not None)

        # Retrieve narrative
        retrieved_narrative = storage.get_narrative(999)
        results.add_result("Retrieve Narrative", retrieved_narrative is not None)

        # Get stats
        stats = storage.get_stats()
        results.add_result("MongoDB Stats", stats['total_reasoning_documents'] > 0)

    except Exception as e:
        results.add_result("MongoDB Storage", False, str(e))
        logger.exception("MongoDB storage test failed")


def test_redis_cache(results: TestResults):
    """Test 4: Redis cache manager"""
    print("\n=== Test 4: Redis Cache ===")

    redis_client = Redis.from_url(settings.REDIS_URL)
    cache = InsightCacheManager(redis_client)

    try:
        # Cache insights
        test_insights = [
            {"insight_id": 1, "title": "Test Insight 1"},
            {"insight_id": 2, "title": "Test Insight 2"}
        ]
        success = cache.cache_company_insights("test_company", test_insights)
        results.add_result("Cache Company Insights", success)

        # Retrieve cached insights
        cached = cache.get_cached_insights("test_company")
        results.add_result("Retrieve Cached Insights", cached is not None and len(cached) == 2)

        # Cache narrative
        test_narrative = {"headline": "Test", "summary": "Summary"}
        success = cache.cache_narrative(123, test_narrative)
        results.add_result("Cache Narrative", success)

        # Retrieve cached narrative
        cached_narrative = cache.get_cached_narrative(123)
        results.add_result("Retrieve Cached Narrative", cached_narrative is not None)

        # Cache portfolio metrics
        test_metrics = {"total_risks": 5, "critical_risks": 2}
        success = cache.cache_portfolio_metrics("test_company", test_metrics)
        results.add_result("Cache Portfolio Metrics", success)

        # Retrieve portfolio metrics
        cached_metrics = cache.get_cached_portfolio_metrics("test_company")
        results.add_result("Retrieve Portfolio Metrics", cached_metrics is not None)

        # Invalidate cache
        deleted = cache.invalidate_company_cache("test_company")
        results.add_result("Invalidate Company Cache", deleted > 0, f"Deleted {deleted} keys")

        # Get cache stats
        stats = cache.get_stats()
        results.add_result("Redis Stats", stats['connected'])

    except Exception as e:
        results.add_result("Redis Cache", False, str(e))
        logger.exception("Redis cache test failed")


def test_complete_orchestrator(results: TestResults):
    """Test 5: Complete orchestrator pipeline"""
    print("\n=== Test 5: Complete Orchestrator Pipeline ===")

    db = SessionLocal()
    mongo_client = MongoClient(settings.MONGODB_URL)
    redis_client = Redis.from_url(settings.REDIS_URL)

    try:
        # Initialize orchestrator
        orchestrator = Layer4Orchestrator(db, mongo_client, redis_client)
        results.add_result("Initialize Orchestrator", True)

        # Generate mock data
        mock_companies = MockCompanyGenerator()
        company = mock_companies.get_company_by_id("retail_001")

        mock_layer3 = MockLayer3Generator()
        indicators = mock_layer3.generate_indicators(
            company_id="retail_001",
            industry="retail",
            business_scale="large",
            timestamp=datetime.now(),
            scenario="supply_disruption"
        )

        # Process company through complete pipeline
        result = orchestrator.process_company(
            company_id="retail_001",
            indicators=indicators,
            company_profile=company,
            use_cache=False  # Don't use cache for testing
        )

        # Verify output structure
        results.add_result("Process Company", "company_id" in result)
        results.add_result("Risk Insights Generated", len(result.get("risk_insights", [])) > 0)
        results.add_result("Portfolio Metrics Calculated", "portfolio_metrics" in result)
        results.add_result("Top Priorities Identified", len(result.get("top_priorities", [])) > 0)

        # Verify storage occurred
        db_insights = orchestrator.insight_storage.get_active_insights("retail_001")
        results.add_result("Insights Stored in PostgreSQL", len(db_insights) > 0, f"Found {len(db_insights)} insights")

        # Verify caching occurred
        cached = orchestrator.cache_manager.get_cached_insights("retail_001")
        results.add_result("Results Cached in Redis", cached is not None)

        # Test get summary
        summary = orchestrator.get_company_insights_summary("retail_001", use_cache=False)
        results.add_result("Get Company Summary", "total_active_risks" in summary)

        logger.info(f"Pipeline processed: {result['summary']}")

    except Exception as e:
        results.add_result("Complete Orchestrator", False, str(e))
        logger.exception("Orchestrator test failed")
    finally:
        db.close()


def test_timescaledb_hypertables(results: TestResults):
    """Test 6: TimescaleDB hypertables"""
    print("\n=== Test 6: TimescaleDB Hypertables ===")

    db = SessionLocal()

    try:
        # Check if hypertables exist
        query = text("""
        SELECT hypertable_name
        FROM timescaledb_information.hypertables
        WHERE hypertable_name IN ('insight_tracking', 'insight_score_history')
        """)
        result = db.execute(query)
        hypertables = [row[0] for row in result]

        results.add_result("insight_tracking Hypertable", "insight_tracking" in hypertables)
        results.add_result("insight_score_history Hypertable", "insight_score_history" in hypertables)

        # Test storing daily tracking
        storage = InsightStorageService(db)
        metrics = {
            "total_active_risks": 5,
            "critical_risks": 2,
            "high_risks": 2,
            "medium_risks": 1
        }
        success = storage.store_daily_tracking("test_company", metrics)
        results.add_result("Store Daily Tracking", success)

    except Exception as e:
        results.add_result("TimescaleDB Hypertables", False, str(e))
        logger.exception("TimescaleDB test failed")
    finally:
        db.close()


def main():
    """Run all tests"""
    print("="*70)
    print("LAYER 4 DATABASE INTEGRATION TEST SUITE")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = TestResults()

    # Run all tests
    test_database_connections(results)
    test_postgresql_storage(results)
    test_mongodb_storage(results)
    test_redis_cache(results)
    test_complete_orchestrator(results)
    test_timescaledb_hypertables(results)

    # Print summary
    results.print_summary()

    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Return exit code
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
