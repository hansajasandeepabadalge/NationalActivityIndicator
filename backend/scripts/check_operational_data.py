"""
Check operational indicators data in MongoDB
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from app.core.config import settings

def check_operational_data():
    """Check if operational data exists in MongoDB"""
    try:
        client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        db = client[settings.MONGODB_DB_NAME]
        
        # Check operational_calculations collection
        collection = db["operational_calculations"]
        count = collection.count_documents({})
        
        print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        print(f"📊 operational_calculations collection has {count} documents")
        
        if count > 0:
            # Show sample documents
            print("\n📄 Sample documents:")
            for doc in collection.find().limit(3):
                print(f"  - {doc.get('indicator_code', 'N/A')}: {doc.get('indicator_name', 'N/A')}")
                print(f"    Company: {doc.get('company_id', 'N/A')}, Value: {doc.get('value', 'N/A')}")
        else:
            print("\n⚠️  No operational data found!")
            print("   Run: python backend/scripts/populate_layer3_operational_indicators.py")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_operational_data()
