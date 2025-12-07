"""
Duplicate Cluster Manager

Manages clusters of duplicate/related articles for story tracking.
Groups articles about the same event/story from different sources.

Features:
- Automatic cluster creation and merging
- Primary article selection (best source/most complete)
- Story timeline tracking
- Cross-source narrative aggregation
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class ClusterMember:
    """Represents a member article in a duplicate cluster"""
    article_id: str
    source_name: str
    title: str
    scraped_at: datetime
    similarity_to_primary: float
    credibility_score: float = 0.5
    is_primary: bool = False
    word_count: int = 0


@dataclass
class DuplicateCluster:
    """Represents a cluster of related/duplicate articles"""
    cluster_id: str
    topic_summary: str
    created_at: datetime
    updated_at: datetime
    members: List[ClusterMember] = field(default_factory=list)
    unique_sources: Set[str] = field(default_factory=set)
    total_reach: int = 0  # Combined from all sources
    aggregate_sentiment: float = 0.0
    
    def get_primary(self) -> Optional[ClusterMember]:
        """Get the primary (best) article in the cluster"""
        for member in self.members:
            if member.is_primary:
                return member
        return self.members[0] if self.members else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "cluster_id": self.cluster_id,
            "topic_summary": self.topic_summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "members": [
                {
                    "article_id": m.article_id,
                    "source_name": m.source_name,
                    "title": m.title,
                    "scraped_at": m.scraped_at.isoformat(),
                    "similarity_to_primary": m.similarity_to_primary,
                    "credibility_score": m.credibility_score,
                    "is_primary": m.is_primary,
                    "word_count": m.word_count
                }
                for m in self.members
            ],
            "unique_sources": list(self.unique_sources),
            "member_count": len(self.members),
            "total_reach": self.total_reach,
            "aggregate_sentiment": self.aggregate_sentiment
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DuplicateCluster":
        """Create from dictionary"""
        members = [
            ClusterMember(
                article_id=m["article_id"],
                source_name=m["source_name"],
                title=m["title"],
                scraped_at=datetime.fromisoformat(m["scraped_at"]),
                similarity_to_primary=m["similarity_to_primary"],
                credibility_score=m.get("credibility_score", 0.5),
                is_primary=m.get("is_primary", False),
                word_count=m.get("word_count", 0)
            )
            for m in data.get("members", [])
        ]
        
        return cls(
            cluster_id=data["cluster_id"],
            topic_summary=data["topic_summary"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            members=members,
            unique_sources=set(data.get("unique_sources", [])),
            total_reach=data.get("total_reach", 0),
            aggregate_sentiment=data.get("aggregate_sentiment", 0.0)
        )


class DuplicateClusterManager:
    """
    Manages duplicate clusters for story tracking and aggregation.
    
    Provides:
    - Automatic clustering of related articles
    - Primary article selection based on quality
    - Story evolution timeline
    - Cross-source narrative analysis
    """
    
    # Redis key prefixes
    KEY_PREFIX = "dedup:cluster"
    
    def __init__(self, redis_client=None):
        """
        Initialize cluster manager.
        
        Args:
            redis_client: Redis client for persistence
        """
        self.redis = redis_client
        self._clusters: Dict[str, DuplicateCluster] = {}
        self._article_to_cluster: Dict[str, str] = {}  # article_id -> cluster_id
        
        # Source credibility scores (higher = more trusted)
        self._source_credibility = {
            "ada_derana": 0.90,
            "daily_mirror": 0.85,
            "hiru_news": 0.80,
            "newsfirst": 0.80,
            "government_gazette": 0.95,
            "central_bank": 0.95,
            "default": 0.70
        }
    
    async def _get_redis(self):
        """Lazy load Redis client"""
        if self.redis is None:
            try:
                from app.db.redis_client import get_redis
                self.redis = get_redis()
            except:
                pass
        return self.redis
    
    def _make_key(self, *parts) -> str:
        """Generate Redis key"""
        return ":".join([self.KEY_PREFIX] + list(parts))
    
    def _generate_cluster_id(self, topic: str) -> str:
        """Generate unique cluster ID"""
        import hashlib
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        topic_hash = hashlib.md5(topic.lower().encode()).hexdigest()[:8]
        return f"cluster_{timestamp}_{topic_hash}"
    
    def _get_source_credibility(self, source_name: str) -> float:
        """Get credibility score for a source"""
        source_key = source_name.lower().replace(" ", "_")
        return self._source_credibility.get(source_key, self._source_credibility["default"])
    
    async def create_cluster(
        self,
        primary_article_id: str,
        primary_title: str,
        primary_source: str,
        scraped_at: Optional[datetime] = None,
        word_count: int = 0
    ) -> DuplicateCluster:
        """
        Create a new duplicate cluster with a primary article.
        
        Args:
            primary_article_id: ID of the primary article
            primary_title: Title of the primary article
            primary_source: Source of the primary article
            scraped_at: When the article was scraped
            word_count: Word count of the article
            
        Returns:
            New DuplicateCluster instance
        """
        now = datetime.utcnow()
        scraped_at = scraped_at or now
        
        cluster_id = self._generate_cluster_id(primary_title)
        credibility = self._get_source_credibility(primary_source)
        
        primary_member = ClusterMember(
            article_id=primary_article_id,
            source_name=primary_source,
            title=primary_title,
            scraped_at=scraped_at,
            similarity_to_primary=1.0,
            credibility_score=credibility,
            is_primary=True,
            word_count=word_count
        )
        
        cluster = DuplicateCluster(
            cluster_id=cluster_id,
            topic_summary=primary_title[:100],
            created_at=now,
            updated_at=now,
            members=[primary_member],
            unique_sources={primary_source}
        )
        
        self._clusters[cluster_id] = cluster
        self._article_to_cluster[primary_article_id] = cluster_id
        
        # Persist
        await self._save_cluster(cluster)
        
        logger.info(f"Created new cluster {cluster_id} with primary: {primary_article_id}")
        return cluster
    
    async def add_to_cluster(
        self,
        cluster_id: str,
        article_id: str,
        title: str,
        source_name: str,
        similarity_score: float,
        scraped_at: Optional[datetime] = None,
        word_count: int = 0
    ) -> bool:
        """
        Add an article to an existing cluster.
        
        Args:
            cluster_id: ID of the cluster
            article_id: ID of the article to add
            title: Article title
            source_name: Source name
            similarity_score: Similarity to the primary article
            scraped_at: When the article was scraped
            word_count: Word count of the article
            
        Returns:
            True if added successfully
        """
        cluster = self._clusters.get(cluster_id)
        if not cluster:
            cluster = await self._load_cluster(cluster_id)
        
        if not cluster:
            logger.warning(f"Cluster {cluster_id} not found")
            return False
        
        # Check if article already in cluster
        existing_ids = {m.article_id for m in cluster.members}
        if article_id in existing_ids:
            return False
        
        now = datetime.utcnow()
        scraped_at = scraped_at or now
        credibility = self._get_source_credibility(source_name)
        
        new_member = ClusterMember(
            article_id=article_id,
            source_name=source_name,
            title=title,
            scraped_at=scraped_at,
            similarity_to_primary=similarity_score,
            credibility_score=credibility,
            is_primary=False,
            word_count=word_count
        )
        
        cluster.members.append(new_member)
        cluster.unique_sources.add(source_name)
        cluster.updated_at = now
        
        # Re-evaluate primary if new article is better
        self._update_primary_selection(cluster)
        
        self._article_to_cluster[article_id] = cluster_id
        
        # Persist
        await self._save_cluster(cluster)
        
        logger.info(f"Added article {article_id} to cluster {cluster_id}")
        return True
    
    def _update_primary_selection(self, cluster: DuplicateCluster):
        """
        Update primary article selection based on quality factors.
        
        Considers:
        - Source credibility
        - Word count (completeness)
        - Recency
        """
        if len(cluster.members) <= 1:
            return
        
        # Score each member
        def score_member(m: ClusterMember) -> float:
            # Base score from credibility (0-1) * 40
            score = m.credibility_score * 40
            
            # Word count bonus (normalized, max 30 points)
            max_words = max(member.word_count for member in cluster.members)
            if max_words > 0:
                score += (m.word_count / max_words) * 30
            
            # Recency bonus (max 30 points for newest)
            now = datetime.utcnow()
            age_hours = (now - m.scraped_at).total_seconds() / 3600
            score += max(0, 30 - age_hours * 2)  # Lose 2 points per hour
            
            return score
        
        # Find best member
        scored_members = [(m, score_member(m)) for m in cluster.members]
        scored_members.sort(key=lambda x: x[1], reverse=True)
        
        # Update primary status
        for member, score in scored_members:
            member.is_primary = False
        scored_members[0][0].is_primary = True
    
    async def get_cluster_for_article(self, article_id: str) -> Optional[DuplicateCluster]:
        """Get the cluster containing an article"""
        cluster_id = self._article_to_cluster.get(article_id)
        if cluster_id:
            cluster = self._clusters.get(cluster_id)
            if cluster:
                return cluster
            return await self._load_cluster(cluster_id)
        
        # Try to find in Redis
        redis = await self._get_redis()
        if redis:
            try:
                cluster_id = await redis.get(f"dedup:article_cluster:{article_id}")
                if cluster_id:
                    return await self._load_cluster(cluster_id)
            except:
                pass
        
        return None
    
    async def get_cluster(self, cluster_id: str) -> Optional[DuplicateCluster]:
        """Get a cluster by ID"""
        cluster = self._clusters.get(cluster_id)
        if cluster:
            return cluster
        return await self._load_cluster(cluster_id)
    
    async def merge_clusters(
        self,
        cluster_id_1: str,
        cluster_id_2: str
    ) -> Optional[DuplicateCluster]:
        """
        Merge two clusters into one.
        
        Args:
            cluster_id_1: First cluster ID
            cluster_id_2: Second cluster ID
            
        Returns:
            Merged cluster
        """
        cluster1 = await self.get_cluster(cluster_id_1)
        cluster2 = await self.get_cluster(cluster_id_2)
        
        if not cluster1 or not cluster2:
            return None
        
        # Keep the older cluster as the base
        if cluster1.created_at > cluster2.created_at:
            cluster1, cluster2 = cluster2, cluster1
        
        # Merge members
        existing_ids = {m.article_id for m in cluster1.members}
        for member in cluster2.members:
            if member.article_id not in existing_ids:
                member.is_primary = False  # Will be re-evaluated
                cluster1.members.append(member)
        
        # Merge sources
        cluster1.unique_sources.update(cluster2.unique_sources)
        cluster1.updated_at = datetime.utcnow()
        
        # Re-evaluate primary
        self._update_primary_selection(cluster1)
        
        # Update mappings
        for member in cluster2.members:
            self._article_to_cluster[member.article_id] = cluster1.cluster_id
        
        # Remove old cluster
        if cluster2.cluster_id in self._clusters:
            del self._clusters[cluster2.cluster_id]
        await self._delete_cluster(cluster2.cluster_id)
        
        # Save merged cluster
        await self._save_cluster(cluster1)
        
        logger.info(f"Merged clusters {cluster_id_2} into {cluster1.cluster_id}")
        return cluster1
    
    async def get_recent_clusters(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[DuplicateCluster]:
        """Get recently active clusters"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Get from memory
        recent = [
            c for c in self._clusters.values()
            if c.updated_at >= cutoff
        ]
        
        # Sort by update time
        recent.sort(key=lambda c: c.updated_at, reverse=True)
        
        return recent[:limit]
    
    async def _save_cluster(self, cluster: DuplicateCluster):
        """Persist cluster to Redis"""
        redis = await self._get_redis()
        if redis is None:
            return
        
        try:
            key = self._make_key(cluster.cluster_id)
            await redis.set(key, json.dumps(cluster.to_dict()))
            
            # Save article-to-cluster mappings
            for member in cluster.members:
                await redis.set(
                    f"dedup:article_cluster:{member.article_id}",
                    cluster.cluster_id
                )
            
        except Exception as e:
            logger.warning(f"Failed to save cluster: {e}")
    
    async def _load_cluster(self, cluster_id: str) -> Optional[DuplicateCluster]:
        """Load cluster from Redis"""
        redis = await self._get_redis()
        if redis is None:
            return None
        
        try:
            key = self._make_key(cluster_id)
            data = await redis.get(key)
            if data:
                cluster = DuplicateCluster.from_dict(json.loads(data))
                self._clusters[cluster_id] = cluster
                return cluster
        except Exception as e:
            logger.warning(f"Failed to load cluster: {e}")
        
        return None
    
    async def _delete_cluster(self, cluster_id: str):
        """Delete cluster from Redis"""
        redis = await self._get_redis()
        if redis is None:
            return
        
        try:
            key = self._make_key(cluster_id)
            await redis.delete(key)
        except:
            pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cluster statistics"""
        if not self._clusters:
            return {
                "total_clusters": 0,
                "total_articles_in_clusters": 0,
                "avg_cluster_size": 0,
                "sources_represented": []
            }
        
        total_articles = sum(len(c.members) for c in self._clusters.values())
        all_sources = set()
        for c in self._clusters.values():
            all_sources.update(c.unique_sources)
        
        return {
            "total_clusters": len(self._clusters),
            "total_articles_in_clusters": total_articles,
            "avg_cluster_size": round(total_articles / len(self._clusters), 2),
            "sources_represented": list(all_sources)
        }
