"""
Check user's company_id and MongoDB data alignment
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from pymongo import MongoClient
from app.core.config import settings

def check_alignment():
    """Check if user company_id matches MongoDB data"""
    # Check PostgreSQL user
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT email, company_id, role FROM l5_users WHERE email = 'admin@example.com'"))
        user = result.fetchone()
        
        if user:
            print(f"✅ User: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Company ID: {user.company_id}")
        
    # Check MongoDB operational data
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DB_NAME]
    
    # Get unique company_ids from MongoDB
    company_ids = db.operational_calculations.distinct("company_id")
    print(f"\n📊 MongoDB company_ids: {company_ids}")
    
    # Check if user's company_id exists in MongoDB
    if user and user.company_id:
        count = db.operational_calculations.count_documents({"company_id": user.company_id})
        print(f"\n🔍 Documents for '{user.company_id}': {count}")
    
    # For admin, check total
    if user and user.role == 'admin':
        total = db.operational_calculations.count_documents({})
        print(f"📈 Total documents (admin sees all): {total}")
    
    client.close()

if __name__ == "__main__":
    check_alignment()
