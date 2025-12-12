"""
Check l5_users
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.core.config import settings

def check_l5_users():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'l5_users'"))
        columns = [row[0] for row in cols]
        print("l5_users columns:", columns)

if __name__ == "__main__":
    check_l5_users()
