"""
Quick script to create an admin user for testing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import bcrypt

def create_admin_user():
    """Create admin user if not exists"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user exists
        result = db.execute(text("SELECT id FROM l5_users WHERE email = :email"), {"email": "admin@example.com"})
        result = db.execute(text("SELECT id FROM l5_users WHERE email = :email"), {"email": "admin@example.com"})
        existing_user = result.fetchone()
        
        password = "admin123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if existing_user:
            print("Updating existing admin password...")
            db.execute(text("""
                UPDATE l5_users 
                SET password_hash = :password, is_active = true, is_verified = true
                WHERE email = :email
            """), {
                "email": "admin@example.com",
                "password": hashed_password
            })
            db.commit()
            print("✅ Admin password updated to: admin123")
            return

        # Create admin user

        
        db.execute(text("""
            INSERT INTO l5_users (email, password_hash, full_name, role, is_active, is_verified, company_id)
            VALUES (:email, :password, :name, :role, true, true, :company_id)
        """), {
            "email": "admin@example.com",
            "password": hashed_password,
            "name": "Admin User",
            "role": "admin",
            "company_id": "COMP-001" 
        })
        db.commit()
        print("✅ Admin user created successfully!")
        print("   Email: admin@example.com")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
