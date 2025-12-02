"""Populate basic indicator definitions from keyword config"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.indicator_models import IndicatorDefinition
from app.layer2.ml_classification.keyword_config import INDICATOR_KEYWORDS

DB_URL = "postgresql://postgres:postgres_secure_2024@national_indicator_timescaledb:5432/national_indicator"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("Populating indicator definitions...")
count = 0

for indicator_id, config in INDICATOR_KEYWORDS.items():
    existing = db.query(IndicatorDefinition).filter_by(indicator_code=indicator_id).first()
    if not existing:
        indicator = IndicatorDefinition(
            indicator_code=indicator_id,
            indicator_name=config['name'],
            display_name=config['name'],
            pestel_category=config['category'],
            calculation_type='frequency',
            value_type='index',
            min_value=0,
            max_value=100,
            description=f"Measures {config['name'].lower()}",
            is_active=True
        )
        db.add(indicator)
        count += 1

db.commit()
print(f"✅ Added {count} indicator definitions")

total = db.query(IndicatorDefinition).count()
print(f"   Total indicators in database: {total}")
db.close()
