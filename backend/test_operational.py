"""Test operational indicators endpoint"""
from pymongo import MongoClient
from app.db.session import SessionLocal
from app.layer5.services.dashboard_service import DashboardService
from app.core.config import settings

def test_operational_indicators():
    """Test getting operational indicators"""
    db = SessionLocal()
    mongo_client = MongoClient(settings.MONGODB_URL)

    try:
        service = DashboardService(db, mongo_client=mongo_client)
        result = service.get_operational_indicators(
            company_id=None,
            limit=20
        )
        print(f"Success! Got {len(result.indicators)} indicators")
        print(f"Total: {result.total}")
        print(f"Critical count: {result.critical_count}")
        print(f"Warning count: {result.warning_count}")
        if result.indicators:
            print(f"\nFirst indicator: {result.indicators[0]}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        mongo_client.close()
        db.close()

if __name__ == "__main__":
    test_operational_indicators()
