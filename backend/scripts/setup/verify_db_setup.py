import asyncio

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect
from app.core.config import settings

def verify_sync_connection():
    print("Verifying synchronous connection...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Successfully connected! Found tables: {tables}")
        
        required_tables = [
            'indicator_definitions', 
            'indicator_values', 
            'indicator_events', 
            'indicator_correlations',
            'ml_classification_results',
            'trend_analysis'
        ]
        
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            print(f"ERROR: Missing tables: {missing_tables}")
        else:
            print("All required tables found.")
            
    except Exception as e:
        print(f"Sync connection failed: {e}")

if __name__ == "__main__":
    verify_sync_connection()
