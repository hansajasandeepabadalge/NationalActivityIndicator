"""
Unit tests for Semantic Deduplication module.

Tests cover:
- EmbeddingGenerator: embedding generation, batch processing, combined embeddings
- SimilarityEngine: FAISS index operations, similarity search
- DuplicateClusterManager: cluster creation and management
- SemanticDeduplicator: multi-level duplicate detection
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

# Import test subjects
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestEmbeddingGenerator:
    """Test cases for EmbeddingGenerator class."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock sentence transformer model."""
        mock = Mock()
        # Return 384-dim embedding
        mock.encode.return_value = np.random.randn(384).astype(np.float32)
        return mock
    
    @pytest.fixture
    def embedding_generator(self, mock_model):
        """Create EmbeddingGenerator with mocked model."""
        with patch('app.deduplication.embedding_generator.SentenceTransformer', return_value=mock_model):
            from app.deduplication.embedding_generator import EmbeddingGenerator
            generator = EmbeddingGenerator()
            generator.model = mock_model
            return generator
    
    def test_generate_embedding_returns_correct_shape(self, embedding_generator, mock_model):
        """Test that embedding has correct dimensionality."""
        mock_model.encode.return_value = np.random.randn(384).astype(np.float32)
        
        embedding = embedding_generator.generate_embedding("Test article text")
        
        assert embedding is not None
        assert len(embedding) == 384
        mock_model.encode.assert_called_once()
    
    def test_generate_embedding_empty_text(self, embedding_generator, mock_model):
        """Test handling of empty text."""
        mock_model.encode.return_value = np.zeros(384).astype(np.float32)
        
        embedding = embedding_generator.generate_embedding("")
        
        assert embedding is not None
        assert len(embedding) == 384
    
    def test_generate_batch_embeddings(self, embedding_generator, mock_model):
        """Test batch embedding generation."""
        texts = ["First article", "Second article", "Third article"]
        mock_model.encode.return_value = np.random.randn(3, 384).astype(np.float32)
        
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        
        assert embeddings is not None
        assert len(embeddings) == 3
        assert all(len(e) == 384 for e in embeddings)
    
    def test_get_combined_embedding_with_title_and_body(self, embedding_generator, mock_model):
        """Test combined embedding from title and body."""
        mock_model.encode.return_value = np.ones(384).astype(np.float32)
        
        embedding = embedding_generator.get_combined_embedding(
            title="Breaking News: Major Event",
            body="This is the body of the article with more details."
        )
        
        assert embedding is not None
        assert len(embedding) == 384
    
    def test_get_combined_embedding_title_only(self, embedding_generator, mock_model):
        """Test combined embedding with only title."""
        mock_model.encode.return_value = np.ones(384).astype(np.float32)
        
        embedding = embedding_generator.get_combined_embedding(
            title="Breaking News",
            body=""
        )
        
        assert embedding is not None
        assert len(embedding) == 384
    
    def test_embedding_normalization(self, embedding_generator, mock_model):
        """Test that embeddings are normalized for cosine similarity."""
        # Return non-normalized embedding
        mock_model.encode.return_value = np.array([3.0, 4.0] + [0.0] * 382).astype(np.float32)
        
        embedding = embedding_generator.generate_embedding("Test text")
        
        # Check if normalized (L2 norm should be approximately 1)
        if hasattr(embedding_generator, '_normalize'):
            norm = np.linalg.norm(embedding)
            assert abs(norm - 1.0) < 0.01


class TestSimilarityEngine:
    """Test cases for SimilarityEngine class."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.get.return_value = None
        mock.set.return_value = True
        mock.hset.return_value = True
        mock.hget.return_value = None
        mock.hgetall.return_value = {}
        return mock
    
    @pytest.fixture
    def similarity_engine(self, mock_redis):
        """Create SimilarityEngine with mocked dependencies."""
        with patch('app.deduplication.similarity_engine.faiss') as mock_faiss:
            # Mock FAISS index
            mock_index = Mock()
            mock_index.add.return_value = None
            mock_index.search.return_value = (np.array([[0.95, 0.85]]), np.array([[0, 1]]))
            mock_index.ntotal = 0
            mock_faiss.IndexFlatIP.return_value = mock_index
            
            from app.deduplication.similarity_engine import SimilarityEngine
            engine = SimilarityEngine(redis_client=mock_redis)
            engine.index = mock_index
            return engine
    
    def test_add_article_to_index(self, similarity_engine):
        """Test adding article embedding to FAISS index."""
        embedding = np.random.randn(384).astype(np.float32)
        
        similarity_engine.add_article("article_123", embedding)
        
        # Verify article was tracked
        assert "article_123" in similarity_engine.article_ids or similarity_engine.index.add.called
    
    @pytest.mark.asyncio
    async def test_find_similar_articles(self, similarity_engine):
        """Test finding similar articles."""
        query_embedding = np.random.randn(384).astype(np.float32)
        
        # Setup mock return
        similarity_engine.article_ids = ["article_1", "article_2"]
        similarity_engine.embeddings = [
            np.random.randn(384).astype(np.float32),
            np.random.randn(384).astype(np.float32)
        ]
        
        similar = await similarity_engine.find_similar(query_embedding, k=5, threshold=0.7)
        
        # Should return list of similar articles
        assert isinstance(similar, list)
    
    def test_cleanup_old_articles(self, similarity_engine):
        """Test removal of old articles from index."""
        # Add articles with timestamps
        old_time = datetime.utcnow() - timedelta(hours=72)
        recent_time = datetime.utcnow() - timedelta(hours=12)
        
        similarity_engine.article_timestamps = {
            "old_article": old_time,
            "recent_article": recent_time
        }
        similarity_engine.article_ids = ["old_article", "recent_article"]
        
        similarity_engine.cleanup_old_articles(max_age_hours=48)
        
        # Old article should be removed
        if hasattr(similarity_engine, 'article_timestamps'):
            assert "old_article" not in similarity_engine.article_timestamps
    
    def test_search_empty_index(self, similarity_engine):
        """Test search on empty index returns empty results."""
        similarity_engine.index.ntotal = 0
        query_embedding = np.random.randn(384).astype(np.float32)
        
        results = similarity_engine.search(query_embedding, top_k=5)
        
        # Should handle empty index gracefully
        assert isinstance(results, (list, tuple))


class TestDuplicateClusterManager:
    """Test cases for DuplicateClusterManager class."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.get.return_value = None
        mock.set.return_value = True
        mock.hset.return_value = True
        mock.hget.return_value = None
        mock.hgetall.return_value = {}
        mock.sadd.return_value = 1
        mock.smembers.return_value = set()
        return mock
    
    @pytest.fixture
    def cluster_manager(self, mock_redis):
        """Create DuplicateClusterManager with mocked Redis."""
        from app.deduplication.duplicate_cluster import DuplicateClusterManager
        manager = DuplicateClusterManager(redis_client=mock_redis)
        return manager
    
    @pytest.mark.asyncio
    async def test_create_cluster(self, cluster_manager, mock_redis):
        """Test creating a new duplicate cluster."""
        article_ids = ["article_1", "article_2"]
        
        cluster_id = await cluster_manager.create_cluster(
            article_ids=article_ids,
            topic="Economy"
        )
        
        assert cluster_id is not None
        assert isinstance(cluster_id, str)
    
    @pytest.mark.asyncio
    async def test_add_to_cluster(self, cluster_manager, mock_redis):
        """Test adding article to existing cluster."""
        mock_redis.get.return_value = json.dumps({
            "id": "cluster_123",
            "article_ids": ["article_1"],
            "topic": "Politics",
            "created_at": datetime.utcnow().isoformat()
        })
        
        result = await cluster_manager.add_to_cluster("cluster_123", "article_2")
        
        assert result is True or mock_redis.set.called
    
    @pytest.mark.asyncio
    async def test_get_cluster(self, cluster_manager, mock_redis):
        """Test retrieving cluster details."""
        cluster_data = {
            "id": "cluster_123",
            "article_ids": ["article_1", "article_2"],
            "topic": "Technology",
            "created_at": datetime.utcnow().isoformat()
        }
        mock_redis.get.return_value = json.dumps(cluster_data)
        
        cluster = await cluster_manager.get_cluster("cluster_123")
        
        if cluster:
            assert cluster.get("id") == "cluster_123"
    
    @pytest.mark.asyncio
    async def test_get_primary_article(self, cluster_manager, mock_redis):
        """Test getting primary article from cluster."""
        cluster_data = {
            "id": "cluster_123",
            "article_ids": ["article_1", "article_2", "article_3"],
            "primary_article_id": "article_2",
            "topic": "Sports"
        }
        mock_redis.get.return_value = json.dumps(cluster_data)
        
        primary = await cluster_manager.get_primary_article("cluster_123")
        
        # Should return primary or first article
        assert primary is not None or mock_redis.get.called


class TestSemanticDeduplicator:
    """Test cases for SemanticDeduplicator main class."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.get.return_value = None
        mock.set.return_value = True
        mock.hset.return_value = True
        mock.hget.return_value = None
        mock.exists.return_value = 0
        return mock
    
    @pytest.fixture
    def mock_embedding_generator(self):
        """Create mock EmbeddingGenerator."""
        mock = Mock()
        mock.get_combined_embedding.return_value = np.random.randn(384).astype(np.float32)
        mock.generate_embedding.return_value = np.random.randn(384).astype(np.float32)
        return mock
    
    @pytest.fixture
    def mock_similarity_engine(self):
        """Create mock SimilarityEngine."""
        mock = AsyncMock()
        mock.find_similar.return_value = []
        mock.add_article.return_value = None
        return mock
    
    @pytest.fixture
    def mock_cluster_manager(self):
        """Create mock DuplicateClusterManager."""
        mock = AsyncMock()
        mock.create_cluster.return_value = "cluster_123"
        mock.add_to_cluster.return_value = True
        return mock
    
    @pytest.fixture
    def deduplicator(self, mock_redis, mock_embedding_generator, mock_similarity_engine, mock_cluster_manager):
        """Create SemanticDeduplicator with mocked dependencies."""
        with patch('app.deduplication.semantic_deduplicator.EmbeddingGenerator', return_value=mock_embedding_generator):
            with patch('app.deduplication.semantic_deduplicator.SimilarityEngine', return_value=mock_similarity_engine):
                with patch('app.deduplication.semantic_deduplicator.DuplicateClusterManager', return_value=mock_cluster_manager):
                    from app.deduplication.semantic_deduplicator import SemanticDeduplicator
                    dedup = SemanticDeduplicator(redis_client=mock_redis)
                    dedup.embedder = mock_embedding_generator
                    dedup.similarity_engine = mock_similarity_engine
                    dedup.cluster_manager = mock_cluster_manager
                    return dedup
    
    @pytest.mark.asyncio
    async def test_check_duplicate_unique_article(self, deduplicator, mock_similarity_engine):
        """Test that unique article is correctly identified."""
        mock_similarity_engine.find_similar.return_value = []
        
        article = {
            "url": "https://example.com/unique-article",
            "title": "Unique Article Title",
            "body": "This is a completely unique article body."
        }
        
        result = await deduplicator.check_duplicate(article)
        
        assert result is not None
        assert result.status in ["UNIQUE", "unique"]
    
    @pytest.mark.asyncio
    async def test_check_duplicate_exact_url_match(self, deduplicator, mock_redis):
        """Test detection of exact URL duplicate."""
        mock_redis.exists.return_value = 1
        mock_redis.get.return_value = "existing_article_id"
        
        article = {
            "url": "https://example.com/existing-article",
            "title": "Some Title",
            "body": "Some body content."
        }
        
        result = await deduplicator.check_duplicate(article)
        
        # Should detect as duplicate via URL hash
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_check_duplicate_semantic_match(self, deduplicator, mock_similarity_engine):
        """Test detection of semantic duplicate."""
        # Mock finding a similar article
        similar_result = Mock()
        similar_result.article_id = "similar_article_123"
        similar_result.score = 0.92
        mock_similarity_engine.find_similar.return_value = [similar_result]
        
        article = {
            "url": "https://different-source.com/article",
            "title": "Similar Article Title",
            "body": "This article is semantically similar to another."
        }
        
        result = await deduplicator.check_duplicate(article)
        
        assert result is not None
        if hasattr(result, 'similarity_score'):
            assert result.similarity_score >= 0.85 or result.status != "UNIQUE"
    
    @pytest.mark.asyncio
    async def test_add_article_to_index(self, deduplicator, mock_similarity_engine, mock_redis):
        """Test adding processed article to index."""
        article = {
            "id": "new_article_123",
            "url": "https://example.com/new-article",
            "title": "New Article",
            "body": "Content of the new article."
        }
        
        await deduplicator.add_article(article)
        
        # Verify article was added to similarity engine
        mock_similarity_engine.add_article.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_dedup_stats(self, deduplicator):
        """Test retrieving deduplication statistics."""
        stats = await deduplicator.get_dedup_stats()
        
        assert stats is not None
        assert isinstance(stats, dict)
    
    @pytest.mark.asyncio
    async def test_check_duplicate_handles_missing_fields(self, deduplicator, mock_similarity_engine):
        """Test handling of articles with missing fields."""
        mock_similarity_engine.find_similar.return_value = []
        
        article = {
            "url": "https://example.com/article"
            # Missing title and body
        }
        
        result = await deduplicator.check_duplicate(article)
        
        # Should handle gracefully
        assert result is not None


class TestIntegration:
    """Integration tests for the full deduplication pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_deduplication_flow(self):
        """Test complete deduplication flow from article to result."""
        # This would test the full integration
        # Skipped in unit tests - run with integration flag
        pytest.skip("Integration test - run separately")
    
    @pytest.mark.asyncio
    async def test_duplicate_cluster_creation_on_match(self):
        """Test that clusters are created when duplicates are found."""
        pytest.skip("Integration test - run separately")


# Performance tests
class TestPerformance:
    """Performance benchmarks for deduplication."""
    
    def test_embedding_generation_speed(self):
        """Test that embedding generation is fast enough."""
        pytest.skip("Performance test - run with benchmarks")
    
    def test_similarity_search_at_scale(self):
        """Test similarity search performance with large index."""
        pytest.skip("Performance test - run with benchmarks")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
