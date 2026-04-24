"""
Script to check if users exist
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def check_users():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check count of users
        result = db.execute(text("SELECT count(*) FROM users"))
        count = result.scalar()
        print(f"Total users: {count}")
        
        if count > 0:
            users = db.execute(text("SELECT email, role FROM users limit 5"))
            print("Existing users:")
            for u in users:
                print(f" - {u.email} ({u.role})")
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
