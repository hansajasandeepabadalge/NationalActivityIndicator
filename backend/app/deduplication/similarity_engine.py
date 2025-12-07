"""
Similarity Engine

FAISS-based vector similarity search for fast duplicate detection.
Optimized for a rolling window of recent articles.

Features:
- In-memory FAISS index for fast similarity search
- Configurable similarity thresholds
- Rolling window management (48-hour default)
- Batch search support
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import json

logger = logging.getLogger(__name__)


@dataclass
class SimilarityConfig:
    """Configuration for similarity search"""
    # Similarity thresholds
    exact_duplicate_threshold: float = 0.95
    near_duplicate_threshold: float = 0.85
    related_story_threshold: float = 0.70
    
    # Index settings
    embedding_dim: int = 384
    index_type: str = "flat"  # "flat" for exact, "ivf" for approximate
    nlist: int = 100  # For IVF index
    nprobe: int = 10  # For IVF search
    
    # Rolling window
    window_hours: int = 48
    max_articles: int = 50000
    
    # Search settings
    top_k: int = 10  # Number of candidates to retrieve
    batch_size: int = 100


@dataclass
class SimilarityMatch:
    """Represents a similarity match result"""
    article_id: str
    similarity_score: float
    matched_at: str
    source_name: Optional[str] = None


@dataclass
class ArticleVector:
    """Stores article metadata with its vector"""
    article_id: str
    embedding: np.ndarray
    title: str
    source_name: str
    scraped_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class SimilarityEngine:
    """
    FAISS-based similarity search engine.
    
    Maintains an in-memory index of recent articles for
    fast duplicate detection.
    """
    
    def __init__(self, config: Optional[SimilarityConfig] = None, redis_client=None):
        """
        Initialize similarity engine.
        
        Args:
            config: Similarity configuration
            redis_client: Redis client for persistence
        """
        self.config = config or SimilarityConfig()
        self.redis = redis_client
        
        # FAISS index
        self._index = None
        self._article_ids: List[str] = []
        self._article_metadata: Dict[str, ArticleVector] = {}
        
        # Tracking
        self._initialized = False
        self._faiss_available = False
    
    async def initialize(self):
        """Initialize FAISS index"""
        if self._initialized:
            return
        
        try:
            import faiss
            self._faiss_available = True
            
            # Create appropriate index
            if self.config.index_type == "ivf":
                # IVF index for large-scale approximate search
                quantizer = faiss.IndexFlatIP(self.config.embedding_dim)
                self._index = faiss.IndexIVFFlat(
                    quantizer, 
                    self.config.embedding_dim, 
                    self.config.nlist,
                    faiss.METRIC_INNER_PRODUCT
                )
            else:
                # Flat index for exact search (good for < 100k vectors)
                self._index = faiss.IndexFlatIP(self.config.embedding_dim)
            
            logger.info(f"FAISS index initialized (type={self.config.index_type}, dim={self.config.embedding_dim})")
            
        except ImportError:
            logger.warning(
                "FAISS not installed. Using numpy-based similarity. "
                "Install with: pip install faiss-cpu"
            )
            self._faiss_available = False
        except Exception as e:
            logger.error(f"Error initializing FAISS: {e}")
            self._faiss_available = False
        
        # Load existing index from Redis if available
        await self._load_from_redis()
        
        self._initialized = True
    
    def _ensure_initialized(self):
        """Ensure index is initialized (sync)"""
        if not self._initialized:
            try:
                import faiss
                self._faiss_available = True
                self._index = faiss.IndexFlatIP(self.config.embedding_dim)
            except ImportError:
                self._faiss_available = False
            self._initialized = True
    
    async def _get_redis(self):
        """Lazy load Redis client"""
        if self.redis is None:
            try:
                from app.db.redis_client import get_redis
                self.redis = get_redis()
            except:
                pass
        return self.redis
    
    async def _load_from_redis(self):
        """Load index state from Redis"""
        redis = await self._get_redis()
        if redis is None:
            return
        
        try:
            # Load article IDs
            ids_data = await redis.get("dedup:index:article_ids")
            if ids_data:
                self._article_ids = json.loads(ids_data)
            
            # Load metadata
            metadata_data = await redis.get("dedup:index:metadata")
            if metadata_data:
                metadata_dict = json.loads(metadata_data)
                for article_id, meta in metadata_dict.items():
                    self._article_metadata[article_id] = ArticleVector(
                        article_id=meta["article_id"],
                        embedding=np.array(meta["embedding"], dtype=np.float32),
                        title=meta["title"],
                        source_name=meta["source_name"],
                        scraped_at=datetime.fromisoformat(meta["scraped_at"]),
                        metadata=meta.get("metadata", {})
                    )
            
            # Rebuild FAISS index from embeddings
            if self._faiss_available and self._article_metadata:
                embeddings = [
                    self._article_metadata[aid].embedding 
                    for aid in self._article_ids
                    if aid in self._article_metadata
                ]
                if embeddings:
                    vectors = np.vstack(embeddings).astype(np.float32)
                    self._index.add(vectors)
            
            logger.info(f"Loaded {len(self._article_ids)} articles from Redis")
            
        except Exception as e:
            logger.warning(f"Could not load index from Redis: {e}")
    
    async def _save_to_redis(self):
        """Persist index state to Redis"""
        redis = await self._get_redis()
        if redis is None:
            return
        
        try:
            # Save article IDs
            await redis.set(
                "dedup:index:article_ids",
                json.dumps(self._article_ids)
            )
            
            # Save metadata (convert to serializable)
            metadata_dict = {}
            for article_id, av in self._article_metadata.items():
                metadata_dict[article_id] = {
                    "article_id": av.article_id,
                    "embedding": av.embedding.tolist(),
                    "title": av.title,
                    "source_name": av.source_name,
                    "scraped_at": av.scraped_at.isoformat(),
                    "metadata": av.metadata
                }
            
            await redis.set(
                "dedup:index:metadata",
                json.dumps(metadata_dict)
            )
            
        except Exception as e:
            logger.warning(f"Could not save index to Redis: {e}")
    
    async def add_article(
        self,
        article_id: str,
        embedding: np.ndarray,
        title: str,
        source_name: str,
        scraped_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an article to the similarity index.
        
        Args:
            article_id: Unique article identifier
            embedding: Article embedding vector
            title: Article title
            source_name: Source name
            scraped_at: Timestamp when scraped
            metadata: Additional metadata
            
        Returns:
            True if added successfully
        """
        await self.initialize()
        
        if article_id in self._article_metadata:
            logger.debug(f"Article {article_id} already in index")
            return False
        
        if scraped_at is None:
            scraped_at = datetime.utcnow()
        
        # Store article vector
        av = ArticleVector(
            article_id=article_id,
            embedding=embedding.astype(np.float32),
            title=title,
            source_name=source_name,
            scraped_at=scraped_at,
            metadata=metadata or {}
        )
        
        self._article_ids.append(article_id)
        self._article_metadata[article_id] = av
        
        # Add to FAISS index
        if self._faiss_available and self._index is not None:
            self._index.add(embedding.reshape(1, -1).astype(np.float32))
        
        # Cleanup old articles
        await self._cleanup_old_articles()
        
        # Persist periodically
        if len(self._article_ids) % 100 == 0:
            await self._save_to_redis()
        
        return True
    
    async def _cleanup_old_articles(self):
        """Remove articles outside the rolling window"""
        if len(self._article_ids) <= self.config.max_articles:
            cutoff = datetime.utcnow() - timedelta(hours=self.config.window_hours)
            
            # Find articles to remove
            to_remove = []
            for article_id in self._article_ids:
                if article_id in self._article_metadata:
                    if self._article_metadata[article_id].scraped_at < cutoff:
                        to_remove.append(article_id)
            
            if not to_remove:
                return
        else:
            # Remove oldest articles if over max
            excess = len(self._article_ids) - self.config.max_articles
            to_remove = self._article_ids[:excess]
        
        # Remove articles
        for article_id in to_remove:
            if article_id in self._article_metadata:
                del self._article_metadata[article_id]
            if article_id in self._article_ids:
                self._article_ids.remove(article_id)
        
        # Rebuild index if significant cleanup
        if len(to_remove) > 100 and self._faiss_available:
            await self._rebuild_index()
        
        logger.debug(f"Cleaned up {len(to_remove)} old articles")
    
    async def _rebuild_index(self):
        """Rebuild FAISS index from current articles"""
        if not self._faiss_available:
            return
        
        try:
            import faiss
            
            # Create new index
            if self.config.index_type == "ivf":
                quantizer = faiss.IndexFlatIP(self.config.embedding_dim)
                self._index = faiss.IndexIVFFlat(
                    quantizer,
                    self.config.embedding_dim,
                    min(self.config.nlist, len(self._article_ids)),
                    faiss.METRIC_INNER_PRODUCT
                )
            else:
                self._index = faiss.IndexFlatIP(self.config.embedding_dim)
            
            # Add all embeddings
            if self._article_ids:
                embeddings = [
                    self._article_metadata[aid].embedding
                    for aid in self._article_ids
                    if aid in self._article_metadata
                ]
                if embeddings:
                    vectors = np.vstack(embeddings).astype(np.float32)
                    
                    if self.config.index_type == "ivf":
                        self._index.train(vectors)
                    
                    self._index.add(vectors)
            
            logger.info(f"Rebuilt FAISS index with {len(self._article_ids)} articles")
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
    
    async def search(
        self,
        embedding: np.ndarray,
        top_k: Optional[int] = None,
        exclude_ids: Optional[List[str]] = None
    ) -> List[SimilarityMatch]:
        """
        Search for similar articles.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            exclude_ids: Article IDs to exclude from results
            
        Returns:
            List of similarity matches
        """
        await self.initialize()
        
        if not self._article_ids:
            return []
        
        top_k = top_k or self.config.top_k
        exclude_ids = set(exclude_ids or [])
        
        query = embedding.reshape(1, -1).astype(np.float32)
        
        if self._faiss_available and self._index is not None:
            # FAISS search
            try:
                # Search for more than needed to allow filtering
                search_k = min(top_k * 2, len(self._article_ids))
                scores, indices = self._index.search(query, search_k)
                
                matches = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx < 0 or idx >= len(self._article_ids):
                        continue
                    
                    article_id = self._article_ids[idx]
                    if article_id in exclude_ids:
                        continue
                    
                    av = self._article_metadata.get(article_id)
                    if av:
                        matches.append(SimilarityMatch(
                            article_id=article_id,
                            similarity_score=float(score),
                            matched_at=datetime.utcnow().isoformat(),
                            source_name=av.source_name
                        ))
                    
                    if len(matches) >= top_k:
                        break
                
                return matches
                
            except Exception as e:
                logger.error(f"FAISS search error: {e}")
                return self._numpy_search(embedding, top_k, exclude_ids)
        else:
            return self._numpy_search(embedding, top_k, exclude_ids)
    
    def _numpy_search(
        self,
        embedding: np.ndarray,
        top_k: int,
        exclude_ids: set
    ) -> List[SimilarityMatch]:
        """Fallback numpy-based search"""
        if not self._article_metadata:
            return []
        
        # Calculate similarities with all articles
        similarities = []
        for article_id, av in self._article_metadata.items():
            if article_id in exclude_ids:
                continue
            
            # Cosine similarity (assuming normalized embeddings)
            sim = float(np.dot(embedding, av.embedding))
            similarities.append((article_id, sim, av))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top matches
        matches = []
        for article_id, sim, av in similarities[:top_k]:
            matches.append(SimilarityMatch(
                article_id=article_id,
                similarity_score=sim,
                matched_at=datetime.utcnow().isoformat(),
                source_name=av.source_name
            ))
        
        return matches
    
    def search_sync(
        self,
        embedding: np.ndarray,
        top_k: Optional[int] = None,
        exclude_ids: Optional[List[str]] = None
    ) -> List[SimilarityMatch]:
        """Synchronous search for non-async contexts"""
        self._ensure_initialized()
        
        if not self._article_ids:
            return []
        
        top_k = top_k or self.config.top_k
        exclude_ids = set(exclude_ids or [])
        
        return self._numpy_search(embedding, top_k, exclude_ids)
    
    def classify_similarity(self, score: float) -> str:
        """
        Classify a similarity score into duplicate type.
        
        Args:
            score: Similarity score (0-1)
            
        Returns:
            Classification: "exact_duplicate", "near_duplicate", "related", "unique"
        """
        if score >= self.config.exact_duplicate_threshold:
            return "exact_duplicate"
        elif score >= self.config.near_duplicate_threshold:
            return "near_duplicate"
        elif score >= self.config.related_story_threshold:
            return "related"
        else:
            return "unique"
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the similarity index"""
        return {
            "total_articles": len(self._article_ids),
            "unique_sources": len(set(
                av.source_name for av in self._article_metadata.values()
            )),
            "faiss_available": self._faiss_available,
            "index_type": self.config.index_type,
            "embedding_dim": self.config.embedding_dim,
            "window_hours": self.config.window_hours,
            "thresholds": {
                "exact_duplicate": self.config.exact_duplicate_threshold,
                "near_duplicate": self.config.near_duplicate_threshold,
                "related_story": self.config.related_story_threshold
            }
        }
