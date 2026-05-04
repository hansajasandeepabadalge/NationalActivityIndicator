"""
Inspect MongoDB operational_calculations documents to see actual structure
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from app.core.config import settings
import json

def inspect_docs():
    """Inspect actual document structure"""
    try:
        client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        db = client[settings.MONGODB_DB_NAME]
        
        collection = db["operational_calculations"]
        count = collection.count_documents({})
        
        print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        print(f"📊 operational_calculations collection has {count} documents\n")
        
        if count > 0:
            # Show first document structure
            doc = collection.find_one()
            print("📄 First document structure:")
            print(json.dumps(doc, indent=2, default=str))
            
            print("\n\n📋 All field names in first document:")
            for key in doc.keys():
                print(f"  - {key}")
        else:
            print("⚠️  No documents found!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_docs()
