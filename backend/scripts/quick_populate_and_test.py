"""Quick populate indicators and run integration test"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.indicator_models import IndicatorDefinition
from app.layer2.ml_classification.keyword_config import INDICATOR_KEYWORDS
from app.layer2.ml_classification.classification_pipeline import ClassificationPipeline
from app.models.article_mapping import ArticleIndicatorMapping

DB_URL = "postgresql://postgres:postgres_secure_2024@national_indicator_timescaledb:5432/national_indicator"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Populate indicators
print("="*60)
print("Step 1: Populating Indicator Definitions")
print("="*60)
count = 0
category_map = {'POL': 'Political', 'ECO': 'Economic', 'SOC': 'Social',
                'TECH': 'Technological', 'ENV': 'Environmental', 'LEG': 'Legal'}
for ind_id, config in INDICATOR_KEYWORDS.items():
    existing = db.query(IndicatorDefinition).filter_by(indicator_id=ind_id).first()
    if not existing:
        category = category_map.get(ind_id.split('_')[0], 'Economic')
        db.add(IndicatorDefinition(
            indicator_id=ind_id,
            indicator_name=config['name'],
            pestel_category=category,
            calculation_type='frequency_count',
            description=f"Measures {config['name'].lower()}",
            is_active=True
        ))
        count += 1
db.commit()
print(f"✅ Added {count} indicators, Total: {db.query(IndicatorDefinition).count()}")

# Run integration test
print("\n" + "="*60)
print("Step 2: Classification Pipeline Integration Test")
print("="*60)
try:
    db.query(ArticleIndicatorMapping).delete()
    db.commit()
    print("✅ Cleaned previous data")

    pipeline = ClassificationPipeline(db)
    results = pipeline.run_full_pipeline(limit=50, min_confidence=0.3)

    assert results["articles_processed"] == 50 and results["mappings_created"] > 0
    print(f"✅ Processed: {results['articles_processed']} articles")
    print(f"✅ Mappings: {results['mappings_created']} (avg {results['avg_mappings_per_article']:.2f}/article)")
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)
finally:
    db.close()
