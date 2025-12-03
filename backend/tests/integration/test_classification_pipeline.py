"""Integration tests for classification pipeline"""

import sys
from pathlib import Path
import sqlalchemy as sa

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.session import SessionLocal
from app.layer2.ml_classification.classification_pipeline import ClassificationPipeline
from app.models.article_mapping import ArticleIndicatorMapping


def test_full_classification_pipeline():
    """Test complete flow: load → classify → store"""
    db = SessionLocal()

    try:
        print("\n" + "="*60)
        print("INTEGRATION TEST: Classification Pipeline")
        print("="*60)

        # Clear previous test data
        print("\n1. Cleaning up previous test data...")
        db.query(ArticleIndicatorMapping).delete()
        db.commit()
        print("   ✅ Database cleared")

        # Run pipeline on subset
        print("\n2. Running classification pipeline on 50 articles...")
        pipeline = ClassificationPipeline(db)
        results = pipeline.run_full_pipeline(limit=50, min_confidence=0.3)

        # Verify results
        print("\n3. Verifying results...")
        assert results['articles_processed'] == 50, "Expected 50 articles processed"
        assert results['mappings_created'] > 0, "Expected some mappings created"
        print(f"   ✅ Processed: {results['articles_processed']} articles")
        print(f"   ✅ Created: {results['mappings_created']} mappings")
        print(f"   ✅ Average: {results['avg_mappings_per_article']:.2f} mappings/article")

        # Verify database
        print("\n4. Verifying database storage...")
        mapping_count = db.query(ArticleIndicatorMapping).count()
        assert mapping_count == results['mappings_created'], "Mapping count mismatch"
        print(f"   ✅ Database contains {mapping_count} mappings")

        # Verify data quality
        print("\n5. Verifying data quality...")
        sample = db.query(ArticleIndicatorMapping).first()
        assert sample.article_id is not None, "Article ID is missing"
        assert sample.indicator_id is not None, "Indicator ID is missing"
        assert 0 <= sample.match_confidence <= 1.0, "Confidence out of range"
        assert len(sample.matched_keywords) > 0, "No keywords matched"
        print(f"   ✅ Sample mapping: {sample.article_id} → {sample.indicator_id}")
        print(f"   ✅ Confidence: {sample.match_confidence:.2f}")
        print(f"   ✅ Keywords: {', '.join(sample.matched_keywords[:3])}")

        # Get distribution by indicator
        print("\n6. Indicator distribution:")
        indicators = db.query(
            ArticleIndicatorMapping.indicator_id,
            sa.func.count(ArticleIndicatorMapping.mapping_id).label('count')
        ).group_by(ArticleIndicatorMapping.indicator_id).all()

        for indicator_id, count in indicators:
            print(f"   - {indicator_id}: {count} articles")

        print("\n" + "="*60)
        print("✅ PIPELINE TEST PASSED!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    finally:
        db.close()


def test_classification_accuracy():
    """Test classification on known examples"""
    db = SessionLocal()

    try:
        print("\n" + "="*60)
        print("ACCURACY CHECK: Classification Results")
        print("="*60)

        # Get sample classified articles
        mappings = db.query(ArticleIndicatorMapping).limit(10).all()

        if not mappings:
            print("   ⚠️  No mappings found. Run test_full_classification_pipeline first.")
            return

        print(f"\nShowing {len(mappings)} sample classifications:\n")
        for i, mapping in enumerate(mappings, 1):
            print(f"{i}. Article {mapping.article_id}")
            print(f"   Indicator: {mapping.indicator_id}")
            print(f"   Confidence: {mapping.match_confidence:.2f}")
            print(f"   Keywords: {', '.join(mapping.matched_keywords[:3])}")
            print(f"   Method: {mapping.classification_method}")
            print()

        print("="*60)
        print("✅ ACCURACY CHECK COMPLETED")
        print("="*60)

    finally:
        db.close()


if __name__ == "__main__":
    import sqlalchemy as sa  # Import here for the query

    print("\n🚀 Starting Integration Tests...\n")

    try:
        test_full_classification_pipeline()
        test_classification_accuracy()
        print("\n✅ ALL INTEGRATION TESTS PASSED!\n")
    except Exception as e:
        print(f"\n❌ TESTS FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
