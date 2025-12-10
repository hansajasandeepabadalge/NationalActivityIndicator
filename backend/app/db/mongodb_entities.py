from pymongo import MongoClient, ASCENDING
from typing import Optional, List
from datetime import datetime
from app.core.config import settings
from app.layer2.nlp_processing.entity_schemas import ExtractedEntities

class MongoDBEntityStorage:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]

        self.entity_extractions = self.db["entity_extractions"]
        self.indicator_calculations = self.db["indicator_calculations"]
        self.narratives = self.db["narratives"]

        try:
            self.client.admin.command('ping')
        except Exception as e:
            raise ConnectionError(f"MongoDB connection failed: {e}")

        self._create_indexes()

    def _create_indexes(self):
        """Create indexes for performance"""
        self.entity_extractions.create_index([("article_id", ASCENDING)], unique=True)
        self.entity_extractions.create_index([("extraction_timestamp", ASCENDING)])
        self.entity_extractions.create_index([("locations.text", ASCENDING)])
        self.entity_extractions.create_index([("organizations.text", ASCENDING)])

        self.indicator_calculations.create_index([("article_id", ASCENDING)])
        self.indicator_calculations.create_index([("indicator_id", ASCENDING)])
        self.indicator_calculations.create_index([("calculation_timestamp", ASCENDING)])

        # Narrative indexes
        self.narratives.create_index([("article_id", ASCENDING)])
        self.narratives.create_index([("indicator_id", ASCENDING)])
        self.narratives.create_index([("generated_at", ASCENDING)])

    def store_entities(self, entities: ExtractedEntities) -> bool:
        """Store extracted entities"""
        try:
            self.entity_extractions.replace_one(
                {"article_id": entities.article_id},
                entities.dict(),
                upsert=True
            )
            return True
        except Exception as e:
            print(f"❌ Failed to store entities for {entities.article_id}: {e}")
            return False

    def store_indicator_calculation(
        self,
        article_id: str,
        indicator_id: str,
        confidence: float,
        method: str = "entity_based"
    ) -> bool:
        """Store entity-based indicator calculation"""
        try:
            doc = {
                "article_id": article_id,
                "indicator_id": indicator_id,
                "confidence": confidence,
                "method": method,
                "calculation_timestamp": datetime.utcnow()
            }
            self.indicator_calculations.insert_one(doc)
            return True
        except Exception as e:
            print(f"❌ Failed to store indicator calculation: {e}")
            return False

    def get_entities(self, article_id: str) -> Optional[ExtractedEntities]:
        """Retrieve entities for an article"""
        doc = self.entity_extractions.find_one({"article_id": article_id})
        if doc:
            return ExtractedEntities(**doc)
        return None

    def get_articles_with_location(self, location_text: str, limit: int = 100) -> List[str]:
        """Find articles mentioning a specific location"""
        results = self.entity_extractions.find(
            {"locations.text": {"$regex": location_text, "$options": "i"}},
            {"article_id": 1}
        ).limit(limit)
        return [doc["article_id"] for doc in results]

    def get_articles_with_organization(self, org_text: str, limit: int = 100) -> List[str]:
        """Find articles mentioning a specific organization"""
        results = self.entity_extractions.find(
            {"organizations.text": {"$regex": org_text, "$options": "i"}},
            {"article_id": 1}
        ).limit(limit)
        return [doc["article_id"] for doc in results]

    def store_narrative(self, narrative) -> bool:
        """Store generated narrative"""
        try:
            self.narratives.replace_one(
                {
                    "article_id": narrative.article_id,
                    "indicator_id": narrative.indicator_id
                },
                narrative.dict(),
                upsert=True
            )
            return True
        except Exception as e:
            print(f"❌ Failed to store narrative: {e}")
            return False

    def get_narrative(self, article_id: str, indicator_id: str):
        """Retrieve narrative"""
        from app.layer2.narrative.schemas import NarrativeText
        doc = self.narratives.find_one({
            "article_id": article_id,
            "indicator_id": indicator_id
        })
        if doc:
            return NarrativeText(**doc)
        return None

    def get_recent_narratives(self, limit: int = 10):
        """Get recent narratives"""
        from app.layer2.narrative.schemas import NarrativeText
        docs = self.narratives.find().sort("generated_at", -1).limit(limit)
        return [NarrativeText(**doc) for doc in docs]
