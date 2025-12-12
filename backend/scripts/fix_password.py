"""
Check the actual password hash stored in database
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.core.config import settings
import bcrypt

def check_password():
    """Check password hash and verify it"""
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT email, password_hash FROM l5_users WHERE email = 'admin@example.com'"))
        user = result.fetchone()
        
        if user:
            print(f"✅ Found user: {user.email}")
            print(f"📝 Password hash: {user.password_hash[:50]}...")
            
            # Test password verification
            test_password = "admin123"
            try:
                is_valid = bcrypt.checkpw(test_password.encode('utf-8'), user.password_hash.encode('utf-8'))
                print(f"\n🔐 Password verification result: {is_valid}")
                
                if is_valid:
                    print("✅ Password 'admin123' is CORRECT!")
                else:
                    print("❌ Password 'admin123' does NOT match!")
                    print("\n🔧 Creating new hash for 'admin123'...")
                    new_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    print(f"New hash: {new_hash[:50]}...")
                    
                    # Update the password
                    conn.execute(text("UPDATE l5_users SET password_hash = :hash WHERE email = 'admin@example.com'"), 
                                {"hash": new_hash})
                    conn.commit()
                    print("✅ Password updated!")
                    
            except Exception as e:
                print(f"❌ Error verifying password: {e}")
        else:
            print("❌ User not found!")

if __name__ == "__main__":
    check_password()
