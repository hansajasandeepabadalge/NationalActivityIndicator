"""
Contextual Topic Modeling Service with ChromaDB

This module provides dynamic topic modeling and trend detection using:
- ChromaDB for semantic similarity and clustering
- LLM for topic interpretation and naming
- Velocity-based trending detection
- Topic evolution tracking over time

Enables discovery of emerging themes and patterns in the news corpus.
"""

import asyncio
import logging
import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from pydantic import BaseModel, Field

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

from .llm_base import GroqLLMClient, LLMConfig, CacheConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Topic Models
# ============================================================================

class TopicStatus(str, Enum):
    """Topic lifecycle status."""
    EMERGING = "emerging"      # New topic, gaining traction
    TRENDING = "trending"      # High velocity, active discussion
    STABLE = "stable"          # Consistent presence
    DECLINING = "declining"    # Decreasing activity
    DORMANT = "dormant"        # Very low recent activity


class TopicCategory(str, Enum):
    """High-level topic categories."""
    ECONOMY = "economy"
    POLITICS = "politics"
    SOCIAL = "social"
    TECHNOLOGY = "technology"
    ENVIRONMENT = "environment"
    INTERNATIONAL = "international"
    BUSINESS = "business"
    POLICY = "policy"
    OTHER = "other"


# Pydantic models for LLM structured output
class TopicInterpretation(BaseModel):
    """LLM interpretation of a topic cluster."""
    name: str = Field(description="Short, descriptive topic name")
    description: str = Field(description="Brief topic description")
    category: str = Field(default="other", description="Topic category")
    key_terms: List[str] = Field(default_factory=list, description="Key terms")
    significance: str = Field(default="", description="Why this topic matters")
    trend_outlook: str = Field(default="stable", description="Trend direction")


# ============================================================================
# Topic Dataclasses
# ============================================================================

@dataclass
class TopicCluster:
    """
    A cluster of semantically related articles forming a topic.
    """
    topic_id: str
    name: str
    description: str = ""
    category: TopicCategory = TopicCategory.OTHER
    
    # Cluster metadata
    article_ids: List[str] = field(default_factory=list)
    article_count: int = 0
    key_terms: List[str] = field(default_factory=list)
    
    # Temporal data
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    # Trend metrics
    status: TopicStatus = TopicStatus.EMERGING
    velocity: float = 0.0  # Articles per day
    momentum: float = 0.0  # Change in velocity
    significance_score: float = 0.5
    
    # Representative article
    centroid_article_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic_id": self.topic_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "article_count": self.article_count,
            "key_terms": self.key_terms,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "status": self.status.value,
            "velocity": self.velocity,
            "momentum": self.momentum,
            "significance_score": self.significance_score
        }


@dataclass
class TopicMatch:
    """
    Result of matching an article to topics.
    """
    article_id: str
    matched_topics: List[Tuple[str, float]] = field(default_factory=list)  # (topic_id, similarity)
    primary_topic_id: Optional[str] = None
    primary_similarity: float = 0.0
    is_new_topic: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "article_id": self.article_id,
            "matched_topics": [
                {"topic_id": tid, "similarity": sim}
                for tid, sim in self.matched_topics
            ],
            "primary_topic_id": self.primary_topic_id,
            "primary_similarity": self.primary_similarity,
            "is_new_topic": self.is_new_topic
        }


@dataclass
class TrendingTopicsResult:
    """
    Result of trending topic analysis.
    """
    trending_topics: List[TopicCluster] = field(default_factory=list)
    emerging_topics: List[TopicCluster] = field(default_factory=list)
    declining_topics: List[TopicCluster] = field(default_factory=list)
    total_topics: int = 0
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trending": [t.to_dict() for t in self.trending_topics],
            "emerging": [t.to_dict() for t in self.emerging_topics],
            "declining": [t.to_dict() for t in self.declining_topics],
            "total_topics": self.total_topics,
            "analysis_timestamp": self.analysis_timestamp.isoformat()
        }


# ============================================================================
# Topic Modeler Service
# ============================================================================

class TopicModeler:
    """
    Contextual topic modeling with ChromaDB for semantic clustering.
    
    Features:
    - Semantic clustering of articles
    - LLM-powered topic interpretation
    - Velocity-based trend detection
    - Topic evolution tracking
    - Similar article discovery
    
    Usage:
        modeler = TopicModeler()
        await modeler.initialize()
        match = await modeler.add_article(article_id, text, title)
        trending = await modeler.get_trending_topics()
    """
    
    TOPIC_INTERPRETATION_PROMPT = """Analyze these article excerpts that form a topic cluster and provide interpretation.

ARTICLE EXCERPTS:
{excerpts}

INSTRUCTIONS:
1. Provide a short, descriptive name for this topic (2-5 words)
2. Write a brief description of what this topic covers
3. Identify the category: economy, politics, social, technology, environment, international, business, policy, other
4. List 5-10 key terms that define this topic
5. Explain why this topic is significant
6. Predict the trend direction: emerging, trending, stable, declining

Be concise and focus on the essence of the topic cluster."""

    SYSTEM_PROMPT = """You are a topic analysis expert. Your task is to interpret clusters of related news articles and identify cohesive themes. Be precise and insightful in your analysis."""

    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        cache_config: Optional[CacheConfig] = None,
        collection_name: str = "article_topics",
        similarity_threshold: float = 0.75,
        min_cluster_size: int = 3,
        persist_directory: Optional[str] = None
    ):
        """
        Initialize Topic Modeler.
        
        Args:
            llm_config: LLM configuration for topic interpretation
            cache_config: Cache configuration
            collection_name: ChromaDB collection name
            similarity_threshold: Threshold for topic matching
            min_cluster_size: Minimum articles for a topic
            persist_directory: Directory for ChromaDB persistence
        """
        self.llm_config = llm_config or LLMConfig()
        self.cache_config = cache_config or CacheConfig(prefix="topic_modeler")
        self.llm_client = GroqLLMClient(self.llm_config, self.cache_config)
        
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.persist_directory = persist_directory
        
        # ChromaDB components
        self.chroma_client: Optional[Any] = None
        self.collection: Optional[Any] = None
        
        # Topic tracking
        self._topics: Dict[str, TopicCluster] = {}
        self._article_topics: Dict[str, str] = {}  # article_id -> topic_id
        self._topic_articles: Dict[str, List[Tuple[str, datetime]]] = defaultdict(list)
        
        # Statistics
        self._articles_processed = 0
        self._topics_created = 0
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize ChromaDB connection and collection.
        
        Returns:
            True if successfully initialized
        """
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available. Topic modeling disabled.")
            return False
        
        try:
            # Initialize ChromaDB client
            if self.persist_directory:
                self.chroma_client = chromadb.PersistentClient(
                    path=self.persist_directory
                )
            else:
                self.chroma_client = chromadb.Client()
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Article topic embeddings"}
            )
            
            self._initialized = True
            logger.info(f"Topic modeler initialized with collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self._initialized = False
            return False
    
    async def add_article(
        self,
        article_id: str,
        text: str,
        title: str = "",
        published_at: Optional[datetime] = None
    ) -> TopicMatch:
        """
        Add an article and match it to topics.
        
        Args:
            article_id: Unique article identifier
            text: Article text content
            title: Article title
            published_at: Publication timestamp
        
        Returns:
            TopicMatch result with matched topics
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._initialized:
            return TopicMatch(article_id=article_id)
        
        published_at = published_at or datetime.now()
        full_text = f"{title}\n\n{text}" if title else text
        
        # Truncate for embedding
        max_length = 2000
        if len(full_text) > max_length:
            full_text = full_text[:max_length]
        
        try:
            # Add to ChromaDB
            self.collection.add(
                documents=[full_text],
                ids=[article_id],
                metadatas=[{
                    "title": title[:200] if title else "",
                    "published_at": published_at.isoformat(),
                    "text_preview": text[:500]
                }]
            )
            
            # Query for similar articles
            results = self.collection.query(
                query_texts=[full_text],
                n_results=10,
                include=["documents", "metadatas", "distances"]
            )
            
            self._articles_processed += 1
            
            # Process matches
            return await self._process_topic_match(
                article_id,
                results,
                published_at,
                text[:500]
            )
            
        except Exception as e:
            logger.error(f"Failed to add article to topic model: {e}")
            return TopicMatch(article_id=article_id)
    
    async def _process_topic_match(
        self,
        article_id: str,
        query_results: Dict,
        published_at: datetime,
        text_preview: str
    ) -> TopicMatch:
        """
        Process ChromaDB query results to match/create topics.
        """
        matched_topics: List[Tuple[str, float]] = []
        
        # Extract similar articles (excluding self)
        if query_results and query_results.get("ids") and len(query_results["ids"]) > 0:
            ids = query_results["ids"][0]
            distances = query_results["distances"][0] if query_results.get("distances") else []
            
            for i, similar_id in enumerate(ids):
                if similar_id == article_id:
                    continue
                
                # Convert distance to similarity (ChromaDB uses L2 distance)
                distance = distances[i] if i < len(distances) else 1.0
                similarity = max(0, 1 - (distance / 2))  # Normalize
                
                if similarity >= self.similarity_threshold:
                    # Check if similar article has a topic
                    if similar_id in self._article_topics:
                        topic_id = self._article_topics[similar_id]
                        matched_topics.append((topic_id, similarity))
        
        # Determine primary topic
        if matched_topics:
            # Use highest similarity topic
            matched_topics.sort(key=lambda x: x[1], reverse=True)
            primary_topic_id, primary_similarity = matched_topics[0]
            
            # Add article to topic
            self._article_topics[article_id] = primary_topic_id
            self._topic_articles[primary_topic_id].append((article_id, published_at))
            
            # Update topic
            if primary_topic_id in self._topics:
                topic = self._topics[primary_topic_id]
                topic.article_count += 1
                topic.article_ids.append(article_id)
                topic.last_seen = published_at
                self._update_topic_metrics(topic)
            
            return TopicMatch(
                article_id=article_id,
                matched_topics=matched_topics[:5],
                primary_topic_id=primary_topic_id,
                primary_similarity=primary_similarity,
                is_new_topic=False
            )
        else:
            # Potentially new topic - will be created when cluster forms
            # For now, create a provisional topic
            topic_id = self._generate_topic_id(text_preview)
            
            self._article_topics[article_id] = topic_id
            self._topic_articles[topic_id].append((article_id, published_at))
            
            # Create provisional topic
            if topic_id not in self._topics:
                self._topics[topic_id] = TopicCluster(
                    topic_id=topic_id,
                    name=f"Topic {len(self._topics) + 1}",
                    article_ids=[article_id],
                    article_count=1,
                    first_seen=published_at,
                    last_seen=published_at,
                    status=TopicStatus.EMERGING,
                    centroid_article_id=article_id
                )
                self._topics_created += 1
            
            return TopicMatch(
                article_id=article_id,
                matched_topics=[],
                primary_topic_id=topic_id,
                primary_similarity=1.0,
                is_new_topic=True
            )
    
    def _generate_topic_id(self, text: str) -> str:
        """Generate a topic ID from text."""
        hash_obj = hashlib.md5(text.encode())
        return f"topic_{hash_obj.hexdigest()[:12]}"
    
    def _update_topic_metrics(self, topic: TopicCluster):
        """Update velocity and momentum for a topic."""
        articles = self._topic_articles.get(topic.topic_id, [])
        if not articles:
            return
        
        now = datetime.now()
        one_day_ago = now - timedelta(days=1)
        one_week_ago = now - timedelta(days=7)
        
        # Count articles in different time windows
        last_day_count = sum(1 for _, ts in articles if ts >= one_day_ago)
        last_week_count = sum(1 for _, ts in articles if ts >= one_week_ago)
        
        # Calculate velocity (articles per day)
        days_active = max(1, (now - topic.first_seen).days)
        topic.velocity = topic.article_count / days_active
        
        # Calculate momentum (recent vs historical velocity)
        recent_velocity = last_day_count
        historical_velocity = (last_week_count - last_day_count) / 6 if last_week_count > last_day_count else 0
        topic.momentum = recent_velocity - historical_velocity
        
        # Determine status
        if topic.article_count < self.min_cluster_size:
            topic.status = TopicStatus.EMERGING
        elif topic.momentum > 1.0:
            topic.status = TopicStatus.TRENDING
        elif topic.momentum < -0.5:
            topic.status = TopicStatus.DECLINING
        elif last_day_count == 0 and last_week_count == 0:
            topic.status = TopicStatus.DORMANT
        else:
            topic.status = TopicStatus.STABLE
    
    async def interpret_topic(self, topic_id: str) -> Optional[TopicInterpretation]:
        """
        Use LLM to interpret and name a topic cluster.
        
        Args:
            topic_id: Topic identifier
        
        Returns:
            TopicInterpretation with name and description
        """
        if topic_id not in self._topics:
            return None
        
        topic = self._topics[topic_id]
        
        # Get article excerpts for interpretation
        excerpts = await self._get_topic_excerpts(topic_id, max_articles=5)
        if not excerpts:
            return None
        
        try:
            prompt = self.TOPIC_INTERPRETATION_PROMPT.format(
                excerpts="\n\n---\n\n".join(excerpts)
            )
            
            interpretation = await self.llm_client.generate_structured(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                response_model=TopicInterpretation
            )
            
            # Update topic with interpretation
            topic.name = interpretation.name
            topic.description = interpretation.description
            topic.key_terms = interpretation.key_terms[:10]
            
            try:
                topic.category = TopicCategory(interpretation.category.lower())
            except ValueError:
                topic.category = TopicCategory.OTHER
            
            return interpretation
            
        except Exception as e:
            logger.error(f"Failed to interpret topic {topic_id}: {e}")
            return None
    
    async def _get_topic_excerpts(
        self,
        topic_id: str,
        max_articles: int = 5
    ) -> List[str]:
        """Get text excerpts from topic articles."""
        if not self._initialized or not self.collection:
            return []
        
        topic = self._topics.get(topic_id)
        if not topic:
            return []
        
        excerpts = []
        article_ids = topic.article_ids[:max_articles]
        
        for article_id in article_ids:
            try:
                result = self.collection.get(
                    ids=[article_id],
                    include=["metadatas"]
                )
                if result and result.get("metadatas"):
                    metadata = result["metadatas"][0]
                    title = metadata.get("title", "")
                    preview = metadata.get("text_preview", "")
                    excerpts.append(f"Title: {title}\n{preview}")
            except Exception:
                continue
        
        return excerpts
    
    async def get_trending_topics(
        self,
        limit: int = 10,
        interpret: bool = True
    ) -> TrendingTopicsResult:
        """
        Get current trending, emerging, and declining topics.
        
        Args:
            limit: Maximum topics per category
            interpret: Whether to interpret unnamed topics
        
        Returns:
            TrendingTopicsResult with categorized topics
        """
        # Update all topic metrics
        for topic in self._topics.values():
            self._update_topic_metrics(topic)
        
        # Categorize topics
        trending = []
        emerging = []
        declining = []
        
        for topic in self._topics.values():
            if topic.article_count < self.min_cluster_size:
                continue
            
            # Interpret if needed
            if interpret and topic.name.startswith("Topic "):
                await self.interpret_topic(topic.topic_id)
            
            if topic.status == TopicStatus.TRENDING:
                trending.append(topic)
            elif topic.status == TopicStatus.EMERGING:
                emerging.append(topic)
            elif topic.status == TopicStatus.DECLINING:
                declining.append(topic)
        
        # Sort by velocity/momentum
        trending.sort(key=lambda t: t.velocity, reverse=True)
        emerging.sort(key=lambda t: t.momentum, reverse=True)
        declining.sort(key=lambda t: t.momentum)
        
        return TrendingTopicsResult(
            trending_topics=trending[:limit],
            emerging_topics=emerging[:limit],
            declining_topics=declining[:limit],
            total_topics=len(self._topics)
        )
    
    async def find_similar_articles(
        self,
        article_id: str,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find articles similar to a given article.
        
        Args:
            article_id: Source article ID
            limit: Maximum results
        
        Returns:
            List of (article_id, similarity_score) tuples
        """
        if not self._initialized or not self.collection:
            return []
        
        try:
            # Get article text
            result = self.collection.get(ids=[article_id], include=["documents"])
            if not result or not result.get("documents"):
                return []
            
            text = result["documents"][0]
            
            # Query for similar
            query_result = self.collection.query(
                query_texts=[text],
                n_results=limit + 1,  # +1 to exclude self
                include=["distances"]
            )
            
            similar = []
            if query_result and query_result.get("ids"):
                ids = query_result["ids"][0]
                distances = query_result["distances"][0] if query_result.get("distances") else []
                
                for i, sim_id in enumerate(ids):
                    if sim_id == article_id:
                        continue
                    distance = distances[i] if i < len(distances) else 1.0
                    similarity = max(0, 1 - (distance / 2))
                    similar.append((sim_id, similarity))
            
            return similar[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar articles: {e}")
            return []
    
    def get_topic(self, topic_id: str) -> Optional[TopicCluster]:
        """Get a specific topic by ID."""
        return self._topics.get(topic_id)
    
    def get_article_topic(self, article_id: str) -> Optional[str]:
        """Get the topic ID for an article."""
        return self._article_topics.get(article_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get topic modeler statistics."""
        status_counts = defaultdict(int)
        for topic in self._topics.values():
            status_counts[topic.status.value] += 1
        
        return {
            "initialized": self._initialized,
            "articles_processed": self._articles_processed,
            "topics_created": self._topics_created,
            "active_topics": len(self._topics),
            "topic_status_distribution": dict(status_counts),
            "chromadb_available": CHROMADB_AVAILABLE
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_topic_modeler(
    api_key: Optional[str] = None,
    persist_directory: Optional[str] = None,
    collection_name: str = "article_topics",
    similarity_threshold: float = 0.75
) -> TopicModeler:
    """
    Factory function to create a TopicModeler instance.
    
    Args:
        api_key: Groq API key for topic interpretation
        persist_directory: Directory for ChromaDB persistence
        collection_name: Name for the ChromaDB collection
        similarity_threshold: Similarity threshold for topic matching
    
    Returns:
        Configured TopicModeler instance
    """
    llm_config = LLMConfig(
        model="llama-3.1-70b-versatile",
        temperature=0.3,
        max_tokens=1000
    )
    
    cache_config = CacheConfig(
        enabled=True,
        ttl_hours=24,
        prefix="topic_modeler"
    )
    
    return TopicModeler(
        llm_config=llm_config,
        cache_config=cache_config,
        collection_name=collection_name,
        similarity_threshold=similarity_threshold,
        persist_directory=persist_directory
    )
