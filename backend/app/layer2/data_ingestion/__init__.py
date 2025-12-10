"""
Layer 2 Data Ingestion Module

Provides loaders for fetching articles from various sources:
- ArticleLoader: Load from mock JSON data files
- MongoDBArticleLoader: Load from MongoDB processed_articles collection (Layer 1 output)
"""

from .article_loader import ArticleLoader
from .mongodb_loader import (
    MongoDBArticleLoader,
    Layer2Article,
    create_mongodb_loader,
    fetch_articles_for_layer2,
    process_layer1_to_layer2_batch
)
from .schemas import Article, ArticleMetadata, ProcessedArticle

__all__ = [
    # Mock data loader
    "ArticleLoader",
    
    # MongoDB loader (Layer 1 -> Layer 2 bridge)
    "MongoDBArticleLoader",
    "Layer2Article",
    "create_mongodb_loader",
    "fetch_articles_for_layer2",
    "process_layer1_to_layer2_batch",
    
    # Schemas
    "Article",
    "ArticleMetadata",
    "ProcessedArticle"
]
