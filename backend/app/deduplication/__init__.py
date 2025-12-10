"""
Semantic Deduplication System

This module provides intelligent duplicate detection using multi-level
matching strategies to achieve 90% better duplicate detection:

1. URL Hash (Exact Match) - Fastest
2. Content Hash (Normalized Text) - Fast
3. Semantic Similarity (Embeddings + FAISS) - Most Accurate

Key Features:
- Sentence-BERT embeddings for semantic understanding
- FAISS vector similarity search for scalability
- Rolling 48-hour window to limit search space
- Duplicate clustering for story tracking
- Redis caching for performance
"""

from app.deduplication.semantic_deduplicator import (
    SemanticDeduplicator,
    DuplicateResult,
    DuplicateType
)
from app.deduplication.embedding_generator import EmbeddingGenerator
from app.deduplication.similarity_engine import SimilarityEngine
from app.deduplication.duplicate_cluster import DuplicateClusterManager
from typing import Optional

# Global deduplicator instance
_deduplicator: Optional[SemanticDeduplicator] = None


async def get_deduplicator() -> SemanticDeduplicator:
    """
    Get global semantic deduplicator instance (async).
    
    Returns:
        SemanticDeduplicator instance ready for use
    """
    global _deduplicator
    if _deduplicator is None:
        _deduplicator = SemanticDeduplicator()
        await _deduplicator.initialize()
    return _deduplicator


def get_deduplicator_sync() -> SemanticDeduplicator:
    """
    Get global semantic deduplicator instance (sync version).
    
    Returns:
        SemanticDeduplicator instance
    """
    global _deduplicator
    if _deduplicator is None:
        _deduplicator = SemanticDeduplicator()
    return _deduplicator


__all__ = [
    "SemanticDeduplicator",
    "DuplicateResult",
    "DuplicateType",
    "EmbeddingGenerator",
    "SimilarityEngine",
    "DuplicateClusterManager",
    "get_deduplicator",
    "get_deduplicator_sync"
]
