"""
Embedding Generator

Generates semantic embeddings for article text using sentence-transformers.
Supports both local and API-based embedding generation.

Models:
- all-MiniLM-L6-v2: Fast, English-focused (default)
- paraphrase-multilingual-MiniLM-L12-v2: For Sinhala/Tamil support
"""

import logging
import hashlib
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation"""
    model_name: str = "all-MiniLM-L6-v2"
    multilingual_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384
    max_seq_length: int = 256
    batch_size: int = 32
    use_gpu: bool = False
    normalize: bool = True  # L2 normalize for cosine similarity
    cache_embeddings: bool = True


class EmbeddingGenerator:
    """
    Generates semantic embeddings for text content.
    
    Uses sentence-transformers for local embedding generation
    with optional multilingual support for Sinhala/Tamil.
    """
    
    def __init__(self, config: Optional[EmbeddingConfig] = None, redis_client=None):
        """
        Initialize embedding generator.
        
        Args:
            config: Embedding configuration
            redis_client: Redis client for caching (optional)
        """
        self.config = config or EmbeddingConfig()
        self.redis = redis_client
        self._model = None
        self._multilingual_model = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the embedding model (lazy loading)"""
        if self._initialized:
            return
        
        try:
            # Try to import sentence-transformers
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading embedding model: {self.config.model_name}")
            self._model = SentenceTransformer(
                self.config.model_name,
                device="cuda" if self.config.use_gpu else "cpu"
            )
            self._initialized = True
            logger.info(f"Embedding model loaded successfully (dim={self.config.embedding_dim})")
            
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Using fallback TF-IDF based embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._initialized = True  # Will use fallback
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self._initialized = True  # Will use fallback
    
    def _ensure_initialized(self):
        """Ensure model is initialized (sync version)"""
        if not self._initialized:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(
                    self.config.model_name,
                    device="cuda" if self.config.use_gpu else "cpu"
                )
            except:
                pass
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
    
    def _text_hash(self, text: str) -> str:
        """Generate hash of text for cache key"""
        normalized = " ".join(text.lower().split())[:500]  # First 500 chars
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def _get_cached_embedding(self, text_hash: str) -> Optional[np.ndarray]:
        """Get cached embedding if available"""
        if not self.config.cache_embeddings:
            return None
        
        redis = await self._get_redis()
        if redis is None:
            return None
        
        try:
            key = f"embedding:{text_hash}"
            cached = await redis.get(key)
            if cached:
                import json
                return np.array(json.loads(cached), dtype=np.float32)
        except Exception as e:
            logger.debug(f"Cache miss for embedding: {e}")
        
        return None
    
    async def _cache_embedding(self, text_hash: str, embedding: np.ndarray, ttl: int = 86400):
        """Cache embedding for future use"""
        if not self.config.cache_embeddings:
            return
        
        redis = await self._get_redis()
        if redis is None:
            return
        
        try:
            import json
            key = f"embedding:{text_hash}"
            await redis.setex(key, ttl, json.dumps(embedding.tolist()))
        except Exception as e:
            logger.debug(f"Failed to cache embedding: {e}")
    
    def _generate_fallback_embedding(self, text: str) -> np.ndarray:
        """
        Generate TF-IDF based embedding as fallback.
        
        This is less accurate but doesn't require sentence-transformers.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        
        # Simple TF-IDF + SVD to get fixed-size embedding
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        try:
            tfidf = vectorizer.fit_transform([text])
            
            # Reduce to target dimension
            if tfidf.shape[1] > self.config.embedding_dim:
                svd = TruncatedSVD(n_components=self.config.embedding_dim)
                embedding = svd.fit_transform(tfidf)[0]
            else:
                embedding = np.zeros(self.config.embedding_dim)
                embedding[:tfidf.shape[1]] = tfidf.toarray()[0]
            
            # Normalize
            if self.config.normalize:
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Fallback embedding failed: {e}")
            return np.zeros(self.config.embedding_dim, dtype=np.float32)
    
    async def generate(
        self, 
        text: str,
        language: str = "en",
        use_cache: bool = True
    ) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            language: Language code (en, si, ta)
            use_cache: Whether to use Redis cache
            
        Returns:
            Embedding vector as numpy array
        """
        await self.initialize()
        
        if not text or len(text.strip()) < 10:
            return np.zeros(self.config.embedding_dim, dtype=np.float32)
        
        # Check cache
        if use_cache:
            text_hash = self._text_hash(text)
            cached = await self._get_cached_embedding(text_hash)
            if cached is not None:
                return cached
        
        # Truncate to max length
        text = text[:self.config.max_seq_length * 4]  # Approximate char limit
        
        # Generate embedding
        if self._model is not None:
            try:
                # Use multilingual model for non-English
                model = self._model
                if language in ["si", "ta"] and self._multilingual_model is not None:
                    model = self._multilingual_model
                
                embedding = model.encode(
                    text,
                    normalize_embeddings=self.config.normalize,
                    show_progress_bar=False
                )
                embedding = np.array(embedding, dtype=np.float32)
                
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")
                embedding = self._generate_fallback_embedding(text)
        else:
            embedding = self._generate_fallback_embedding(text)
        
        # Cache result
        if use_cache:
            await self._cache_embedding(text_hash, embedding)
        
        return embedding
    
    async def generate_batch(
        self,
        texts: List[str],
        languages: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            languages: Optional list of language codes
            use_cache: Whether to use Redis cache
            
        Returns:
            List of embedding vectors
        """
        await self.initialize()
        
        if not texts:
            return []
        
        if languages is None:
            languages = ["en"] * len(texts)
        
        # Check cache for each text
        results = [None] * len(texts)
        texts_to_embed = []
        indices_to_embed = []
        
        if use_cache:
            for i, text in enumerate(texts):
                if text and len(text.strip()) >= 10:
                    text_hash = self._text_hash(text)
                    cached = await self._get_cached_embedding(text_hash)
                    if cached is not None:
                        results[i] = cached
                    else:
                        texts_to_embed.append(text[:self.config.max_seq_length * 4])
                        indices_to_embed.append(i)
                else:
                    results[i] = np.zeros(self.config.embedding_dim, dtype=np.float32)
        else:
            texts_to_embed = [t[:self.config.max_seq_length * 4] if t else "" for t in texts]
            indices_to_embed = list(range(len(texts)))
        
        # Generate embeddings for uncached texts
        if texts_to_embed and self._model is not None:
            try:
                embeddings = self._model.encode(
                    texts_to_embed,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False
                )
                
                for i, idx in enumerate(indices_to_embed):
                    emb = np.array(embeddings[i], dtype=np.float32)
                    results[idx] = emb
                    
                    # Cache
                    if use_cache:
                        text_hash = self._text_hash(texts[idx])
                        await self._cache_embedding(text_hash, emb)
                        
            except Exception as e:
                logger.error(f"Error in batch embedding: {e}")
                for idx in indices_to_embed:
                    results[idx] = self._generate_fallback_embedding(texts[idx])
        else:
            # Use fallback for all
            for idx in indices_to_embed:
                if texts[idx]:
                    results[idx] = self._generate_fallback_embedding(texts[idx])
                else:
                    results[idx] = np.zeros(self.config.embedding_dim, dtype=np.float32)
        
        return results
    
    def generate_sync(self, text: str, language: str = "en") -> np.ndarray:
        """
        Synchronous version of generate for non-async contexts.
        
        Args:
            text: Text to embed
            language: Language code
            
        Returns:
            Embedding vector
        """
        self._ensure_initialized()
        
        if not text or len(text.strip()) < 10:
            return np.zeros(self.config.embedding_dim, dtype=np.float32)
        
        text = text[:self.config.max_seq_length * 4]
        
        if self._model is not None:
            try:
                embedding = self._model.encode(
                    text,
                    normalize_embeddings=self.config.normalize,
                    show_progress_bar=False
                )
                return np.array(embedding, dtype=np.float32)
            except Exception as e:
                logger.error(f"Error in sync embedding: {e}")
        
        return self._generate_fallback_embedding(text)
    
    def get_embedding_dim(self) -> int:
        """Get the dimensionality of embeddings"""
        return self.config.embedding_dim
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            "model_name": self.config.model_name,
            "embedding_dim": self.config.embedding_dim,
            "max_seq_length": self.config.max_seq_length,
            "is_initialized": self._initialized,
            "has_sentence_transformers": self._model is not None,
            "using_fallback": self._model is None
        }
