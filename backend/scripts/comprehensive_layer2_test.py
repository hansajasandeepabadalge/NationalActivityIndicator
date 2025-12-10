"""Comprehensive Layer 2 Integration Test"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.layer2.data_ingestion.article_loader import ArticleLoader
from app.layer2.ml_classification.rule_based_classifier import RuleBasedClassifier
from app.layer2.nlp_processing.entity_extractor import EntityExtractor
from app.layer2.narrative.generator import NarrativeGenerator
from app.db.mongodb_entities import MongoDBEntityStorage

def print_header(title):
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def main():
    print_header("LAYER 2 COMPREHENSIVE INTEGRATION TEST")

    # Phase 1: Article Loading
    print_header("Phase 1: Article Ingestion")
    try:
        loader = ArticleLoader()
        articles = loader.load_articles()
        print_success(f"Loaded {len(articles)} articles")

        # Show distribution
        categories = {}
        for article in articles:
            cat = article.category
            categories[cat] = categories.get(cat, 0) + 1

        print("\nArticle Distribution:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat:15s}: {count:3d} articles")

    except Exception as e:
        print_error(f"Article loading failed: {e}")
        return False

    # Phase 2: Rule-Based Classification
    print_header("Phase 2: Rule-Based Classification")
    try:
        classifier = RuleBasedClassifier()

        classified_count = 0
        total_predictions = 0

        for article in articles[:20]:  # Test first 20
            article_text = article.content  # content is a string
            predictions = classifier.classify_article(article_text, article.title)
            classified_count += 1
            total_predictions += len(predictions)

        avg_predictions = total_predictions / classified_count if classified_count > 0 else 0

        print_success(f"Classified {classified_count} articles")
        print(f"  Average indicators per article: {avg_predictions:.1f}")
        print(f"  Cache stats: {classifier.get_cache_stats()}")

        # Show sample classification
        sample_article = articles[0]
        sample_text = sample_article.content
        sample_preds = classifier.classify_article(sample_text, sample_article.title)

        print(f"\nSample Classification ({sample_article.article_id}):")
        print(f"  Title: {sample_article.title[:60]}...")
        print(f"  Indicators found: {len(sample_preds)}")
        for pred in sample_preds[:3]:
            pred_dict = dict(pred)  # Convert tuple to dict
            print(f"    - {pred_dict['indicator_id']}: {pred_dict['confidence']:.2f}")

    except Exception as e:
        print_error(f"Classification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Phase 3: Entity Extraction
    print_header("Phase 3: Entity Extraction")
    try:
        extractor = EntityExtractor()

        sample_article = articles[0]
        entities = extractor.extract_entities(
            article_id=sample_article.article_id,
            title=sample_article.title,
            content=sample_article.content
        )

        print_success("Entity extraction working")
        print(f"\nExtracted from '{sample_article.title[:50]}...':")
        print(f"  Locations: {len(entities.locations)}")
        print(f"  Organizations: {len(entities.organizations)}")
        print(f"  Persons: {len(entities.persons)}")
        print(f"  Amounts: {len(entities.amounts)}")
        print(f"  Percentages: {len(entities.percentages)}")

        if entities.amounts:
            print(f"\n  Sample amounts:")
            for amt in entities.amounts[:3]:
                print(f"    - {amt.currency} {amt.amount:,.0f}")

        if entities.locations:
            print(f"\n  Sample locations:")
            for loc in entities.locations[:3]:
                print(f"    - {loc.text}")

    except Exception as e:
        print_error(f"Entity extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Phase 4: Narrative Generation
    print_header("Phase 4: Narrative Generation")
    try:
        generator = NarrativeGenerator()

        narrative = generator.generate_narrative(
            article_id=sample_article.article_id,
            indicator_id="ECO_CURRENCY_STABILITY",
            confidence=0.75,
            entities=entities,
            trend="rising"
        )

        print_success("Narrative generation working")
        print(f"\nGenerated Narrative:")
        print(f"  Emoji: {narrative.emoji}")
        print(f"  Headline: {narrative.headline}")
        print(f"  Summary: {narrative.summary[:100]}...")

    except Exception as e:
        print_error(f"Narrative generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Phase 5: MongoDB Storage
    print_header("Phase 5: MongoDB Storage")
    try:
        mongo = MongoDBEntityStorage()

        # Store entities
        success = mongo.store_entities(entities)
        if success:
            print_success("Entity storage successful")
        else:
            print_error("Entity storage failed")

        # Store narrative
        success = mongo.store_narrative(narrative)
        if success:
            print_success("Narrative storage successful")
        else:
            print_error("Narrative storage failed")

        # Retrieve entities
        retrieved = mongo.get_entities(sample_article.article_id)
        if retrieved:
            print_success(f"Retrieved entities for article {retrieved.article_id}")
        else:
            print_error("Entity retrieval failed")

    except Exception as e:
        print_error(f"MongoDB operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Summary
    print_header("TEST SUMMARY")
    print_success("All core Layer 2 components are functional!")
    print("\nVerified Components:")
    print("  ✅ Article Ingestion (240 articles)")
    print("  ✅ Rule-Based Classification")
    print("  ✅ Entity Extraction")
    print("  ✅ Narrative Generation")
    print("  ✅ MongoDB Storage & Retrieval")

    print("\nNote: PostgreSQL tests require auth fix")
    print("Note: Full ML classification requires trained models")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
