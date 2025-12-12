"""
Check tables
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.core.config import settings

def check_tables():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print("Tables:", tables)
        
        if 'source_configs' in tables:
            cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'source_configs'"))
            columns = [row[0] for row in cols]
            print("source_configs columns:", columns)

if __name__ == "__main__":
    check_tables()
