"""Test script to check operational indicators"""
from pymongo import MongoClient
from app.db.session import SessionLocal
from app.layer5.services.dashboard_service import DashboardService
from app.core.config import settings

# Create database session
db = SessionLocal()

# Create MongoDB connection
mongo_client = MongoClient(settings.MONGODB_URL)

# Create dashboard service
dashboard_service = DashboardService(db, mongo_client=mongo_client)

print("=" * 60)
print("Testing Operational Indicators")
print("=" * 60)

try:
    # Test with company_id=None (admin view - all companies)
    print("\n1. Testing with company_id=None (all companies)...")
    result = dashboard_service.get_operational_indicators(company_id=None, limit=20)
    print(f"   Total indicators: {result.total}")
    print(f"   Critical count: {result.critical_count}")
    print(f"   Number of indicators returned: {len(result.indicators)}")

    if result.indicators:
        print(f"\n   First indicator:")
        ind = result.indicators[0]
        print(f"     ID: {ind.indicator_id}")
        print(f"     Name: {ind.indicator_name}")
        print(f"     Category: {ind.category}")
        print(f"     Current Value: {ind.current_value}")
        print(f"     Baseline: {ind.baseline_value}")
        print(f"     Trend: {ind.trend}")
        print(f"     Company: {ind.company_id}")
    else:
        print("   WARNING: No indicators returned!")

    # Test with specific company
    print("\n2. Testing with company_id='retail_001'...")
    result2 = dashboard_service.get_operational_indicators(company_id='retail_001', limit=20)
    print(f"   Total indicators: {result2.total}")
    print(f"   Number of indicators returned: {len(result2.indicators)}")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    mongo_client.close()
    db.close()
