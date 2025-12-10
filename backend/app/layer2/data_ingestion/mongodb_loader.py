"""
MongoDB Article Loader for Layer 2

This module provides the bridge between Layer 1 (processed_articles in MongoDB)
and Layer 2 (enhanced processing pipeline). It fetches processed articles
from MongoDB and transforms them into the format expected by Layer 2 services.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# Try to import settings, with fallback
try:
    from app.core.config import settings
except ImportError:
    settings = None

logger = logging.getLogger(__name__)


class Layer2Article(BaseModel):
    """
    Article format expected by Layer 2 enhanced processing pipeline.
    
    This is the bridge schema between Layer 1's ProcessedArticle 
    and Layer 2's processing services.
    """
    article_id: str
    text: str  # Main content for analysis
    title: str = ""
    source: str = ""  # Made truly optional with empty default
    url: str = ""     # Made truly optional with empty default
    published_at: Optional[datetime] = None
    language: str = "en"
    
    # Original metadata preserved from Layer 1
    layer1_quality_score: float = 1.0
    layer1_word_count: Optional[int] = None
    layer1_categories: List[str] = Field(default_factory=list)
    layer1_entities: Dict[str, List[str]] = Field(default_factory=dict)
    layer1_stages_completed: List[str] = Field(default_factory=list)
    
    model_config = {"populate_by_name": True}


class MongoDBArticleLoader:
    """
    Loads processed articles from MongoDB for Layer 2 processing.
    
    This loader fetches articles from the processed_articles collection
    that have completed Layer 1 cleaning and transforms them into
    the format required by Layer 2 services.
    """
    
    def __init__(
        self,
        mongo_url: Optional[str] = None,
        database_name: str = "national_indicator"
    ):
        """
        Initialize MongoDB article loader.
        
        Args:
            mongo_url: MongoDB connection URL. If None, uses settings.
            database_name: Name of the database to use.
        """
        self.mongo_url = mongo_url or getattr(
            settings, 'MONGODB_URL',
            "mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin"
        )
        self.database_name = database_name
        self._client: Optional[AsyncIOMotorClient] = None
        self._connected = False
        
    async def connect(self) -> bool:
        """Establish connection to MongoDB."""
        try:
            self._client = AsyncIOMotorClient(
                self.mongo_url,
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            await self._client.admin.command('ping')
            self._connected = True
            logger.info("MongoDB connection established for Layer 2 loader")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("MongoDB connection closed")
    
    @property
    def db(self):
        """Get the database instance."""
        if not self._client:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self._client[self.database_name]
    
    async def get_unprocessed_articles(
        self,
        limit: int = 100,
        skip: int = 0,
        min_quality_score: float = 0.5
    ) -> List[Layer2Article]:
        """
        Get processed articles from Layer 1 that haven't been processed by Layer 2.
        
        Args:
            limit: Maximum number of articles to fetch.
            skip: Number of articles to skip (for pagination).
            min_quality_score: Minimum quality score to include.
            
        Returns:
            List of articles ready for Layer 2 processing.
        """
        if not self._connected:
            await self.connect()
        
        # Query for articles that have completed Layer 1 but not Layer 2
        query = {
            "processing_pipeline.stages_completed": {"$in": ["cleaning"]},
            "$or": [
                {"layer2_processed": {"$exists": False}},
                {"layer2_processed": False}
            ],
            "quality.is_clean": True
        }
        
        cursor = self.db.processed_articles.find(query).skip(skip).limit(limit)
        articles = await cursor.to_list(length=limit)
        
        return [self._transform_to_layer2(doc) for doc in articles]
    
    async def get_articles_since(
        self,
        since: datetime,
        limit: int = 100
    ) -> List[Layer2Article]:
        """
        Get processed articles created since a specific time.
        
        Args:
            since: Fetch articles created after this time.
            limit: Maximum number of articles to fetch.
            
        Returns:
            List of articles ready for Layer 2 processing.
        """
        if not self._connected:
            await self.connect()
        
        query = {
            "processing_pipeline.last_updated": {"$gte": since},
            "processing_pipeline.stages_completed": {"$in": ["cleaning"]}
        }
        
        cursor = self.db.processed_articles.find(query).limit(limit)
        articles = await cursor.to_list(length=limit)
        
        return [self._transform_to_layer2(doc) for doc in articles]
    
    async def get_articles_by_ids(
        self,
        article_ids: List[str]
    ) -> List[Layer2Article]:
        """
        Get specific articles by their IDs.
        
        Args:
            article_ids: List of article IDs to fetch.
            
        Returns:
            List of matching articles.
        """
        if not self._connected:
            await self.connect()
        
        query = {"article_id": {"$in": article_ids}}
        cursor = self.db.processed_articles.find(query)
        articles = await cursor.to_list(length=len(article_ids))
        
        return [self._transform_to_layer2(doc) for doc in articles]
    
    async def get_all_articles(
        self,
        limit: int = 1000,
        skip: int = 0
    ) -> List[Layer2Article]:
        """
        Get all processed articles.
        
        Args:
            limit: Maximum number of articles to fetch.
            skip: Number of articles to skip.
            
        Returns:
            List of all processed articles.
        """
        if not self._connected:
            await self.connect()
        
        query = {
            "processing_pipeline.stages_completed": {"$in": ["cleaning"]}
        }
        
        cursor = self.db.processed_articles.find(query).skip(skip).limit(limit)
        articles = await cursor.to_list(length=limit)
        
        return [self._transform_to_layer2(doc) for doc in articles]
    
    async def mark_as_layer2_processed(
        self,
        article_id: str,
        layer2_result: Dict[str, Any]
    ) -> bool:
        """
        Mark an article as processed by Layer 2 and store results.
        
        Args:
            article_id: ID of the article to update.
            layer2_result: Results from Layer 2 processing.
            
        Returns:
            True if update was successful.
        """
        if not self._connected:
            await self.connect()
        
        update = {
            "$set": {
                "layer2_processed": True,
                "layer2_result": layer2_result,
                "layer2_processed_at": datetime.utcnow()
            },
            "$push": {
                "processing_pipeline.stages_completed": "layer2_enhanced"
            }
        }
        
        result = await self.db.processed_articles.update_one(
            {"article_id": article_id},
            update
        )
        
        return result.modified_count > 0
    
    async def count_unprocessed(self) -> int:
        """Count articles waiting for Layer 2 processing."""
        if not self._connected:
            await self.connect()
        
        query = {
            "processing_pipeline.stages_completed": {"$in": ["cleaning"]},
            "$or": [
                {"layer2_processed": {"$exists": False}},
                {"layer2_processed": False}
            ]
        }
        
        return await self.db.processed_articles.count_documents(query)
    
    async def count_all_processed(self) -> int:
        """Count all articles in processed_articles collection."""
        if not self._connected:
            await self.connect()
        
        return await self.db.processed_articles.count_documents({})
    
    def _transform_to_layer2(self, doc: Dict[str, Any]) -> Layer2Article:
        """
        Transform a MongoDB processed_article document to Layer2Article format.
        
        Args:
            doc: MongoDB document from processed_articles collection.
            
        Returns:
            Layer2Article ready for enhanced processing.
        """
        content = doc.get("content", {})
        extraction = doc.get("extraction", {})
        quality = doc.get("quality", {})
        pipeline = doc.get("processing_pipeline", {})
        
        # Combine title and body for text field
        title = content.get("title_original", "") or content.get("title_translated", "") or ""
        body = content.get("body_original", "") or content.get("body_translated", "") or ""
        text = f"{title}\n\n{body}".strip()
        
        return Layer2Article(
            article_id=doc.get("article_id", str(doc.get("_id", ""))),
            text=text,
            title=title,
            source=doc.get("source_name") or "",  # Handle None
            url=doc.get("source_url") or "",      # Handle None
            published_at=extraction.get("publish_timestamp"),
            language=content.get("language_detected") or content.get("language_original") or "en",
            layer1_quality_score=quality.get("credibility_score", 1.0) or 1.0,
            layer1_word_count=quality.get("word_count"),
            layer1_categories=extraction.get("categories") or [],
            layer1_entities=extraction.get("entities") or {},
            layer1_stages_completed=pipeline.get("stages_completed") or []
        )


async def create_mongodb_loader() -> MongoDBArticleLoader:
    """Factory function to create and connect a MongoDB loader."""
    loader = MongoDBArticleLoader()
    await loader.connect()
    return loader


# ============================================================================
# Convenience functions for Layer 2 services
# ============================================================================

async def fetch_articles_for_layer2(
    limit: int = 100,
    unprocessed_only: bool = True
) -> List[Layer2Article]:
    """
    Fetch articles from MongoDB for Layer 2 processing.
    
    Args:
        limit: Maximum number of articles to fetch.
        unprocessed_only: If True, only fetch articles not yet processed by Layer 2.
        
    Returns:
        List of articles ready for Layer 2 processing.
    """
    loader = await create_mongodb_loader()
    try:
        if unprocessed_only:
            return await loader.get_unprocessed_articles(limit=limit)
        else:
            return await loader.get_all_articles(limit=limit)
    finally:
        await loader.disconnect()


async def process_layer1_to_layer2_batch(
    pipeline,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Process a batch of articles from Layer 1 through Layer 2.
    
    Args:
        pipeline: EnhancedProcessingPipeline instance.
        limit: Maximum number of articles to process.
        
    Returns:
        Summary of processing results.
    """
    loader = await create_mongodb_loader()
    results = {
        "total_fetched": 0,
        "processed": 0,
        "failed": 0,
        "skipped": 0
    }
    
    try:
        articles = await loader.get_unprocessed_articles(limit=limit)
        results["total_fetched"] = len(articles)
        
        for article in articles:
            try:
                # Process through Layer 2 pipeline
                result = await pipeline.process(
                    text=article.text,
                    title=article.title,
                    article_id=article.article_id
                )
                
                # Mark as processed in MongoDB
                await loader.mark_as_layer2_processed(
                    article_id=article.article_id,
                    layer2_result=result.__dict__ if hasattr(result, '__dict__') else {}
                )
                
                results["processed"] += 1
                
            except Exception as e:
                logger.error(f"Failed to process article {article.article_id}: {e}")
                results["failed"] += 1
                
    finally:
        await loader.disconnect()
    
    return results
