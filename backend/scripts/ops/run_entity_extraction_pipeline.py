"""Entity extraction pipeline - Day 4"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tqdm import tqdm
from app.layer2.data_ingestion.article_loader import ArticleLoader
from app.layer2.nlp_processing.entity_extractor import EntityExtractor
from app.layer2.indicator_calculation.entity_based_calculator import EntityBasedIndicatorCalculator
from app.db.mongodb_entities import MongoDBEntityStorage

def run_entity_extraction_pipeline(limit: int = 200):
    """Run full entity extraction pipeline"""

    print("🚀 Starting Entity Extraction Pipeline")

    article_loader = ArticleLoader()
    entity_extractor = EntityExtractor()
    calculator = EntityBasedIndicatorCalculator()
    mongo_storage = MongoDBEntityStorage()

    print(f"📥 Loading {limit} articles...")
    articles = article_loader.load_articles(limit=limit)
    print(f"✅ Loaded {len(articles)} articles")

    success_count = 0
    for article in tqdm(articles, desc="Extracting entities"):
        try:
            entities = entity_extractor.extract_entities(
                article_id=article.article_id,
                title=article.title,
                content=article.content
            )

            mongo_storage.store_entities(entities)

            indicators = calculator.calculate_all_indicators(entities)

            for indicator_id, confidence in indicators.items():
                if confidence > 0.3:
                    mongo_storage.store_indicator_calculation(
                        article_id=article.article_id,
                        indicator_id=indicator_id,
                        confidence=confidence
                    )

            success_count += 1

        except Exception as e:
            print(f"❌ Error processing {article.article_id}: {e}")
            continue

    print(f"\n✅ Pipeline complete: {success_count}/{len(articles)} articles processed")

    print("\n📊 Extraction Statistics:")
    total_entities = mongo_storage.entity_extractions.count_documents({})
    total_indicators = mongo_storage.indicator_calculations.count_documents({})
    print(f"  - Total entity records: {total_entities}")
    print(f"  - Total indicator calculations: {total_indicators}")

if __name__ == "__main__":
    run_entity_extraction_pipeline(limit=200)
