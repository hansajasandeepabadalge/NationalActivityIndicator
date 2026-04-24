"""
Corroboration Engine

Finds corroborating articles for claims across multiple sources.
Uses semantic similarity to identify articles reporting the same information.

Features:
- Semantic similarity-based article matching
- Claim-level corroboration
- Conflict detection
- Source diversity scoring
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class CorroborationLevel(Enum):
    """Level of corroboration found."""
    STRONG = "strong"           # 3+ independent sources confirm
    MODERATE = "moderate"       # 2 sources confirm
    WEAK = "weak"              # 1 other source or partial match
    NONE = "none"              # No corroboration found
    CONFLICTING = "conflicting" # Sources contradict each other


@dataclass
class CorroboratingArticle:
    """An article that corroborates a claim."""
    article_id: str
    source_name: str
    title: str
    similarity_score: float
    published_at: Optional[datetime] = None
    matching_claims: List[str] = field(default_factory=list)
    source_tier: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "article_id": self.article_id,
            "source": self.source_name,
            "title": self.title,
            "similarity": round(self.similarity_score, 3),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "matching_claims": self.matching_claims,
            "source_tier": self.source_tier
        }


@dataclass
class ConflictingArticle:
    """An article that conflicts with a claim."""
    article_id: str
    source_name: str
    title: str
    conflict_type: str          # "value_mismatch", "contradictory", "timeline"
    conflict_details: str
    source_tier: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "article_id": self.article_id,
            "source": self.source_name,
            "title": self.title,
            "conflict_type": self.conflict_type,
            "conflict_details": self.conflict_details,
            "source_tier": self.source_tier
        }


@dataclass
class CorroborationResult:
    """Result of corroboration analysis for an article."""
    article_id: str
    source_name: str
    corroboration_level: CorroborationLevel
    corroboration_score: float        # 0-100
    
    # Corroborating articles
    corroborating_articles: List[CorroboratingArticle] = field(default_factory=list)
    
    # Conflicting articles
    conflicting_articles: List[ConflictingArticle] = field(default_factory=list)
    
    # Source diversity
    unique_sources: int = 0
    source_tiers_represented: List[str] = field(default_factory=list)
    
    # Timing
    earliest_report: Optional[datetime] = None
    is_first_to_report: bool = False
    
    # Analysis timestamp
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "article_id": self.article_id,
            "source": self.source_name,
            "corroboration_level": self.corroboration_level.value,
            "corroboration_score": round(self.corroboration_score, 1),
            "corroborating_count": len(self.corroborating_articles),
            "corroborating_articles": [a.to_dict() for a in self.corroborating_articles],
            "conflicting_count": len(self.conflicting_articles),
            "conflicting_articles": [a.to_dict() for a in self.conflicting_articles],
            "unique_sources": self.unique_sources,
            "source_tiers": self.source_tiers_represented,
            "is_first_to_report": self.is_first_to_report,
            "analyzed_at": self.analyzed_at.isoformat()
        }


class CorroborationEngine:
    """
    Finds corroborating articles across sources.
    
    Uses the SemanticDeduplicator to find similar articles,
    then analyzes them for corroboration or conflicts.
    """
    
    # Similarity thresholds
    STRONG_SIMILARITY_THRESHOLD = 0.85
    MODERATE_SIMILARITY_THRESHOLD = 0.70
    WEAK_SIMILARITY_THRESHOLD = 0.55
    
    # Corroboration scoring
    BASE_CORROBORATION_SCORE = 30      # Base score for single source
    PER_SOURCE_BONUS = 15              # Bonus per corroborating source
    TIER_1_BONUS = 10                  # Bonus for Tier 1 source
    OFFICIAL_BONUS = 20                # Bonus for official source
    FIRST_TO_REPORT_BONUS = 5          # Bonus for breaking news
    CONFLICT_PENALTY = 25              # Penalty for conflicting reports
    
    # Time window for related articles
    CORROBORATION_WINDOW_HOURS = 72    # 3 days
    
    def __init__(self, deduplicator=None, reputation_tracker=None):
        """
        Initialize the corroboration engine.
        
        Args:
            deduplicator: SemanticDeduplicator instance for similarity search
            reputation_tracker: SourceReputationTracker instance
        """
        self._deduplicator = deduplicator
        self._reputation_tracker = reputation_tracker
        
        # Article cache for corroboration checking
        self._article_cache: Dict[str, Dict[str, Any]] = {}
        
        # Corroboration results cache
        self._results_cache: Dict[str, CorroborationResult] = {}
        
        logger.info("CorroborationEngine initialized")
    
    def set_deduplicator(self, deduplicator):
        """Set the semantic deduplicator."""
        self._deduplicator = deduplicator
    
    def set_reputation_tracker(self, reputation_tracker):
        """Set the reputation tracker."""
        self._reputation_tracker = reputation_tracker
    
    def add_article_to_cache(
        self,
        article_id: str,
        content: str,
        title: str,
        source_name: str,
        published_at: Optional[datetime] = None,
        claims: List[Dict[str, Any]] = None
    ):
        """
        Add an article to the corroboration cache.
        
        Args:
            article_id: Article identifier
            content: Article content
            title: Article title
            source_name: Source name
            published_at: Publication time
            claims: Extracted claims from article
        """
        self._article_cache[article_id] = {
            "article_id": article_id,
            "content": content,
            "title": title,
            "source_name": source_name,
            "published_at": published_at or datetime.utcnow(),
            "claims": claims or [],
            "cached_at": datetime.utcnow()
        }
        
        # Clean old cache entries
        self._cleanup_cache()
    
    def find_corroboration(
        self,
        article_id: str,
        content: str,
        title: str,
        source_name: str,
        published_at: Optional[datetime] = None,
        claims: List[Dict[str, Any]] = None
    ) -> CorroborationResult:
        """
        Find corroborating articles for a given article.
        
        Args:
            article_id: Article identifier
            content: Article content
            title: Article title
            source_name: Source name
            published_at: Publication time
            claims: Extracted claims
            
        Returns:
            CorroborationResult with analysis
        """
        pub_time = published_at or datetime.utcnow()
        
        # Add to cache if not present
        if article_id not in self._article_cache:
            self.add_article_to_cache(
                article_id, content, title, source_name, pub_time, claims
            )
        
        # Check cache for recent result
        if article_id in self._results_cache:
            cached = self._results_cache[article_id]
            cache_age = (datetime.utcnow() - cached.analyzed_at).total_seconds()
            if cache_age < 3600:  # 1 hour cache
                return cached
        
        # Find similar articles
        similar_articles = self._find_similar_articles(
            article_id, content, title, source_name
        )
        
        # Analyze corroboration
        corroborating = []
        conflicting = []
        sources_seen = set()
        tiers_seen = set()
        earliest_time = pub_time
        
        for similar in similar_articles:
            sim_id = similar["article_id"]
            sim_source = similar["source_name"]
            sim_score = similar["similarity_score"]
            sim_time = similar.get("published_at", datetime.utcnow())
            
            # Skip same source
            if sim_source.lower() == source_name.lower():
                continue
            
            # Get source tier
            tier = self._get_source_tier(sim_source)
            
            # Check for conflicts
            conflict = self._check_for_conflicts(
                claims or [],
                similar.get("claims", [])
            )
            
            if conflict:
                conflicting.append(ConflictingArticle(
                    article_id=sim_id,
                    source_name=sim_source,
                    title=similar.get("title", ""),
                    conflict_type=conflict["type"],
                    conflict_details=conflict["details"],
                    source_tier=tier
                ))
            else:
                # Add as corroborating
                corroborating.append(CorroboratingArticle(
                    article_id=sim_id,
                    source_name=sim_source,
                    title=similar.get("title", ""),
                    similarity_score=sim_score,
                    published_at=sim_time,
                    source_tier=tier
                ))
                
                sources_seen.add(sim_source)
                tiers_seen.add(tier)
                
                if sim_time < earliest_time:
                    earliest_time = sim_time
        
        # Determine corroboration level
        level = self._determine_level(
            len(corroborating),
            len(conflicting),
            tiers_seen
        )
        
        # Calculate corroboration score
        score = self._calculate_score(
            corroborating,
            conflicting,
            pub_time <= earliest_time  # Is first to report
        )
        
        # Create result
        result = CorroborationResult(
            article_id=article_id,
            source_name=source_name,
            corroboration_level=level,
            corroboration_score=score,
            corroborating_articles=corroborating,
            conflicting_articles=conflicting,
            unique_sources=len(sources_seen),
            source_tiers_represented=list(tiers_seen),
            earliest_report=earliest_time,
            is_first_to_report=(pub_time <= earliest_time)
        )
        
        # Cache result
        self._results_cache[article_id] = result
        
        return result
    
    def batch_corroboration(
        self,
        articles: List[Dict[str, Any]]
    ) -> List[CorroborationResult]:
        """
        Find corroboration for multiple articles.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of CorroborationResult objects
        """
        # First add all articles to cache
        for article in articles:
            self.add_article_to_cache(
                article_id=article.get("article_id", article.get("id", "")),
                content=article.get("content", article.get("body", "")),
                title=article.get("title", ""),
                source_name=article.get("source_name", article.get("source", "")),
                published_at=article.get("published_at"),
                claims=article.get("claims", [])
            )
        
        # Then analyze each
        results = []
        for article in articles:
            result = self.find_corroboration(
                article_id=article.get("article_id", article.get("id", "")),
                content=article.get("content", article.get("body", "")),
                title=article.get("title", ""),
                source_name=article.get("source_name", article.get("source", "")),
                published_at=article.get("published_at"),
                claims=article.get("claims", [])
            )
            results.append(result)
        
        return results
    
    def _find_similar_articles(
        self,
        article_id: str,
        content: str,
        title: str,
        source_name: str
    ) -> List[Dict[str, Any]]:
        """Find similar articles using semantic deduplicator or cache."""
        similar = []
        
        # Use semantic deduplicator if available
        if self._deduplicator:
            try:
                duplicates = self._deduplicator.find_duplicates(
                    article_id=article_id,
                    content=content,
                    title=title,
                    threshold=self.WEAK_SIMILARITY_THRESHOLD
                )
                
                for dup in duplicates:
                    # Get additional info from cache
                    cached = self._article_cache.get(dup.get("duplicate_id", ""))
                    
                    similar.append({
                        "article_id": dup.get("duplicate_id", ""),
                        "source_name": cached.get("source_name", "") if cached else "",
                        "title": cached.get("title", "") if cached else "",
                        "similarity_score": dup.get("similarity_score", 0),
                        "published_at": cached.get("published_at") if cached else None,
                        "claims": cached.get("claims", []) if cached else []
                    })
            except Exception as e:
                logger.warning(f"Deduplicator error: {e}")
        
        # Fall back to cache-based similarity
        if not similar:
            similar = self._find_similar_from_cache(
                article_id, content, title, source_name
            )
        
        return similar
    
    def _find_similar_from_cache(
        self,
        article_id: str,
        content: str,
        title: str,
        source_name: str
    ) -> List[Dict[str, Any]]:
        """Find similar articles from cache using basic text similarity."""
        similar = []
        
        # Get title words for matching
        title_words = set(title.lower().split())
        content_words = set(content.lower().split()[:100])  # First 100 words
        
        for cached_id, cached in self._article_cache.items():
            if cached_id == article_id:
                continue
            
            # Calculate basic similarity
            cached_title_words = set(cached.get("title", "").lower().split())
            cached_content_words = set(cached.get("content", "").lower().split()[:100])
            
            # Title similarity (Jaccard)
            title_intersection = len(title_words & cached_title_words)
            title_union = len(title_words | cached_title_words)
            title_sim = title_intersection / title_union if title_union > 0 else 0
            
            # Content similarity
            content_intersection = len(content_words & cached_content_words)
            content_union = len(content_words | cached_content_words)
            content_sim = content_intersection / content_union if content_union > 0 else 0
            
            # Combined score
            similarity = 0.4 * title_sim + 0.6 * content_sim
            
            if similarity >= self.WEAK_SIMILARITY_THRESHOLD:
                similar.append({
                    "article_id": cached_id,
                    "source_name": cached.get("source_name", ""),
                    "title": cached.get("title", ""),
                    "similarity_score": similarity,
                    "published_at": cached.get("published_at"),
                    "claims": cached.get("claims", [])
                })
        
        # Sort by similarity
        similar.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return similar[:10]  # Top 10 matches
    
    def _check_for_conflicts(
        self,
        claims1: List[Dict[str, Any]],
        claims2: List[Dict[str, Any]]
    ) -> Optional[Dict[str, str]]:
        """Check for conflicts between claims."""
        if not claims1 or not claims2:
            return None
        
        for c1 in claims1:
            for c2 in claims2:
                # Check for value mismatches in numeric claims
                if c1.get("type") == "numeric" and c2.get("type") == "numeric":
                    val1 = c1.get("numeric_value")
                    val2 = c2.get("numeric_value")
                    
                    if val1 and val2:
                        # Check if same context but different values
                        if c1.get("numeric_unit") == c2.get("numeric_unit"):
                            max_val = max(abs(val1), abs(val2))
                            if max_val > 0:
                                diff = abs(val1 - val2) / max_val
                                if diff > 0.2:  # >20% difference
                                    return {
                                        "type": "value_mismatch",
                                        "details": f"Values differ: {val1} vs {val2}"
                                    }
        
        return None
    
    def _determine_level(
        self,
        corroborating_count: int,
        conflicting_count: int,
        tiers: Set[str]
    ) -> CorroborationLevel:
        """Determine corroboration level."""
        if conflicting_count > corroborating_count:
            return CorroborationLevel.CONFLICTING
        
        if corroborating_count >= 3 or "official" in tiers:
            return CorroborationLevel.STRONG
        
        if corroborating_count >= 2 or "tier_1" in tiers:
            return CorroborationLevel.MODERATE
        
        if corroborating_count >= 1:
            return CorroborationLevel.WEAK
        
        return CorroborationLevel.NONE
    
    def _calculate_score(
        self,
        corroborating: List[CorroboratingArticle],
        conflicting: List[ConflictingArticle],
        is_first_to_report: bool
    ) -> float:
        """Calculate corroboration score."""
        score = self.BASE_CORROBORATION_SCORE
        
        # Add bonus for each corroborating source
        for article in corroborating:
            score += self.PER_SOURCE_BONUS
            
            # Tier bonuses
            if article.source_tier == "official":
                score += self.OFFICIAL_BONUS
            elif article.source_tier == "tier_1":
                score += self.TIER_1_BONUS
        
        # First to report bonus
        if is_first_to_report and len(corroborating) > 0:
            score += self.FIRST_TO_REPORT_BONUS
        
        # Conflict penalties
        for article in conflicting:
            score -= self.CONFLICT_PENALTY
        
        # Bound score
        return max(0, min(100, score))
    
    def _get_source_tier(self, source_name: str) -> str:
        """Get tier for a source."""
        if self._reputation_tracker:
            try:
                tier = self._reputation_tracker.get_source_tier(source_name)
                return tier.value
            except Exception:
                pass
        
        # Fallback
        return "unknown"
    
    def _cleanup_cache(self):
        """Remove old cache entries."""
        cutoff = datetime.utcnow() - timedelta(hours=self.CORROBORATION_WINDOW_HOURS * 2)
        
        to_remove = []
        for article_id, article in self._article_cache.items():
            cached_at = article.get("cached_at", datetime.utcnow())
            if cached_at < cutoff:
                to_remove.append(article_id)
        
        for article_id in to_remove:
            del self._article_cache[article_id]
            if article_id in self._results_cache:
                del self._results_cache[article_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        results = list(self._results_cache.values())
        
        if not results:
            return {
                "articles_analyzed": 0,
                "avg_corroboration_score": 0,
                "by_level": {}
            }
        
        by_level = defaultdict(int)
        for r in results:
            by_level[r.corroboration_level.value] += 1
        
        return {
            "articles_analyzed": len(results),
            "articles_in_cache": len(self._article_cache),
            "avg_corroboration_score": round(
                sum(r.corroboration_score for r in results) / len(results), 1
            ),
            "by_level": dict(by_level),
            "first_to_report_count": sum(1 for r in results if r.is_first_to_report)
        }
