"""
Direct test of DashboardService to bypass API layer
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.layer5.services.dashboard_service import DashboardService

def test_dashboard_service():
    """Test DashboardService directly"""
    print("Testing DashboardService.get_operational_indicators()...")
    print("=" * 60)
    
    try:
        # Setup database connections
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        mongo_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Create service
        service = DashboardService(db, mongo_client=mongo_client, mongo_db_name=settings.MONGODB_DB_NAME)
        
        # Test 1: Admin view (all companies)
        print("\n📊 Test 1: Admin view (company_id=None)")
        result = service.get_operational_indicators(company_id=None, limit=20)
        print(f"✅ Total indicators: {result.total}")
        print(f"   Critical count: {result.critical_count}")
        if result.indicators:
            print(f"   Sample: {result.indicators[0].indicator_name}")
            print(f"   Value: {result.indicators[0].current_value}")
        
        # Test 2: Specific company view
        print("\n📊 Test 2: Specific company (company_id='retail_001')")
        result2 = service.get_operational_indicators(company_id='retail_001', limit=20)
        print(f"✅ Total indicators: {result2.total}")
        print(f"   Critical count: {result2.critical_count}")
        if result2.indicators:
            print(f"   Sample: {result2.indicators[0].indicator_name}")
            print(f"   Company: {result2.indicators[0].company_id}")
        
        # Cleanup
        mongo_client.close()
        db.close()
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_service()
