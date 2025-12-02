#!/usr/bin/env python3
"""Run database migrations via SQLAlchemy directly"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.models import *
from app.db.base_class import Base

DB_URL = "postgresql://postgres:postgres_secure_2024@national_indicator_timescaledb:5432/national_indicator"

print("Creating database engine...")
engine = create_engine(DB_URL)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("\n✅ Migrations completed successfully!")

# Verify
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"))
    count = result.scalar()
    print(f"   Total tables created: {count}")

    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"))
    tables = [row[0] for row in result]
    print(f"   Tables: {', '.join(tables)}")
