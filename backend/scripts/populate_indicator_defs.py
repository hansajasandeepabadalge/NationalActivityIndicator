"""Populate basic indicator definitions from keyword config"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.indicator_models import IndicatorDefinition
from app.layer2.ml_classification.keyword_config import INDICATOR_KEYWORDS
from app.core.config import settings

# Use settings from config (respects .env file)
DB_URL = settings.DATABASE_URL

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("Populating indicator definitions...")
count = 0

for indicator_code, config in INDICATOR_KEYWORDS.items():
    existing = db.query(IndicatorDefinition).filter_by(indicator_id=indicator_code).first()
    if not existing:
        indicator = IndicatorDefinition(
            indicator_id=indicator_code,
            indicator_name=config['name'],
            pestel_category=config['pestel'],
            calculation_type='frequency_count',
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
