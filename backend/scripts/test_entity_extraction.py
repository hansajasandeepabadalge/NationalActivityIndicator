"""Test entity extraction pipeline with 10 articles"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.layer2.data_ingestion.article_loader import ArticleLoader
from app.layer2.nlp_processing.entity_extractor import EntityExtractor
from app.layer2.indicator_calculation.entity_based_calculator import EntityBasedIndicatorCalculator
from app.db.mongodb_entities import MongoDBEntityStorage

def test_extraction():
    print("🧪 Testing Entity Extraction (10 articles)")

    article_loader = ArticleLoader()
    entity_extractor = EntityExtractor()
    calculator = EntityBasedIndicatorCalculator()
    mongo_storage = MongoDBEntityStorage()

    articles = article_loader.load_articles(limit=10)
    print(f"✅ Loaded {len(articles)} test articles\n")

    for i, article in enumerate(articles, 1):
        print(f"[{i}/10] Processing: {article.title[:50]}...")

        entities = entity_extractor.extract_entities(
            article_id=article.article_id,
            title=article.title,
            content=article.content
        )

        print(f"  - Locations: {len(entities.locations)}")
        print(f"  - Organizations: {len(entities.organizations)}")
        print(f"  - Persons: {len(entities.persons)}")
        print(f"  - Dates: {len(entities.dates)}")
        print(f"  - Amounts: {len(entities.amounts)}")
        print(f"  - Percentages: {len(entities.percentages)}")
        print(f"  - Processing time: {entities.processing_time_ms:.2f}ms")

        mongo_storage.store_entities(entities)

        indicators = calculator.calculate_all_indicators(entities)
        print(f"  - Indicators:")
        for ind_id, conf in indicators.items():
            if conf > 0.3:
                print(f"    {ind_id}: {conf:.3f}")
                mongo_storage.store_indicator_calculation(
                    article_id=article.article_id,
                    indicator_id=ind_id,
                    confidence=conf
                )
        print()

    print("✅ Test complete!")

if __name__ == "__main__":
    test_extraction()
