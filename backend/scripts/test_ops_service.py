"""
Test the operational indicators API endpoint directly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.layer5.services.dashboard_service import DashboardService
import json

def test_service():
    """Test DashboardService.get_operational_indicators()"""
    try:
        # Create DB session
        db: Session = SessionLocal()
        
        # Connect to MongoDB
        mongo_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Create service
        service = DashboardService(
            db=db,
            mongo_client=mongo_client,
            mongo_db_name=settings.MONGODB_DB_NAME
        )
        
        print("="*70)
        print("TESTING DashboardService.get_operational_indicators()")
        print("="*70)
        
        # Test 1: Get all operational indicators (admin view)
        print("\n[Test 1] Getting all operational indicators (company_id=None)...")
        result = service.get_operational_indicators(company_id=None, limit=20)
        
        print(f"\n✅ Result:")
        print(f"   Company ID: {result.company_id}")
        print(f"   Total indicators: {result.total}")
        print(f"   Critical count: {result.critical_count}")
        print(f"   Warning count: {result.warning_count}")
        print(f"   Number of indicator objects: {len(result.indicators)}")
        
        if result.indicators:
            print(f"\n📊 First 3 indicators:")
            for i, ind in enumerate(result.indicators[:3], 1):
                print(f"\n   {i}. {ind.indicator_name}")
                print(f"      ID: {ind.indicator_id}")
                print(f"      Category: {ind.category}")
                print(f"      Current Value: {ind.current_value}")
                print(f"      Baseline: {ind.baseline_value}")
                print(f"      Company: {ind.company_id}")
        else:
            print("\n⚠️  No indicators returned!")
        
        # Test 2: Get for specific company
        print("\n\n[Test 2] Getting indicators for retail_001...")
        result2 = service.get_operational_indicators(company_id="retail_001", limit=20)
        print(f"\n✅ Result:")
        print(f"   Total indicators: {result2.total}")
        print(f"   Number of indicator objects: {len(result2.indicators)}")
        
        # Cleanup
        mongo_client.close()
        db.close()
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()
