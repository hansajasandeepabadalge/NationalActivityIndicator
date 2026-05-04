"""Integration test for classification pipeline - Docker version"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.layer2.ml_classification.classification_pipeline import ClassificationPipeline
from app.models.article_mapping import ArticleIndicatorMapping

DB_URL = "postgresql://postgres:postgres_secure_2024@national_indicator_timescaledb:5432/national_indicator"

print("\n" + "="*60)
print("INTEGRATION TEST: Classification Pipeline")
print("="*60)

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("\n1. Cleaning previous test data...")
    db.query(ArticleIndicatorMapping).delete()
    db.commit()
    print("   ✅ Database cleared")

    print("\n2. Running pipeline on 50 articles...")
    pipeline = ClassificationPipeline(db)
    results = pipeline.run_full_pipeline(limit=50, min_confidence=0.3)

    print("\n3. Verifying results...")
    assert results["articles_processed"] == 50
    assert results["mappings_created"] > 0
    print(f"   ✅ Processed: {results['articles_processed']} articles")
    print(f"   ✅ Created: {results['mappings_created']} mappings")
    print(f"   ✅ Average: {results['avg_mappings_per_article']:.2f} mappings/article")

    mapping_count = db.query(ArticleIndicatorMapping).count()
    assert mapping_count == results["mappings_created"]
    print(f"\n4. ✅ Database contains {mapping_count} mappings")

    print("\n" + "="*60)
    print("✅ INTEGRATION TEST PASSED!")
    print("="*60)
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
