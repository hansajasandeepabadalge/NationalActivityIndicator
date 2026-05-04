"""
Check detailed structure of operational data
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from app.core.config import settings
import json

def check_data_structure():
    """Check actual structure of operational data"""
    try:
        client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        db = client[settings.MONGODB_DB_NAME]
        
        collection = db["operational_calculations"]
        
        # Get one document to see structure
        doc = collection.find_one()
        
        if doc:
            print("📄 Sample document structure:")
            print(json.dumps(doc, indent=2, default=str))
        else:
            print("⚠️  No documents found")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data_structure()
