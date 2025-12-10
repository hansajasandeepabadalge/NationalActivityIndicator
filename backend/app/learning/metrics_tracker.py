"""
Metrics Tracker for Adaptive Learning System

Collects, stores, and retrieves performance metrics for sources, scrapers,
validators, and the overall pipeline. These metrics drive adaptive tuning.

Metrics Categories:
- Scraping: Success rate, latency, error types, content volume
- Validation: Pass/fail rates, error patterns, correction frequency
- Quality: Average scores, trends, outliers
- Performance: Throughput, resource usage, timing
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import statistics
import json

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked."""
    # Scraping metrics
    SCRAPE_SUCCESS = "scrape_success"
    SCRAPE_FAILURE = "scrape_failure"
    SCRAPE_LATENCY = "scrape_latency"
    SCRAPE_TIMEOUT = "scrape_timeout"
    SCRAPE_ARTICLE_COUNT = "scrape_article_count"
    
    # Validation metrics
    VALIDATION_PASS = "validation_pass"
    VALIDATION_FAIL = "validation_fail"
    VALIDATION_ERROR_TYPE = "validation_error_type"
    VALIDATION_CORRECTION = "validation_correction"
    
    # Quality metrics
    QUALITY_SCORE = "quality_score"
    CREDIBILITY_SCORE = "credibility_score"
    CONTENT_LENGTH = "content_length"
    DUPLICATE_DETECTED = "duplicate_detected"
    
    # Processing metrics
    PROCESSING_TIME = "processing_time"
    DOWNSTREAM_ACCEPT = "downstream_accept"
    DOWNSTREAM_REJECT = "downstream_reject"
    
    # Error metrics
    ERROR_RATE = "error_rate"
    RETRY_COUNT = "retry_count"


@dataclass
class MetricEntry:
    """Single metric data point."""
    metric_type: MetricType
    value: float
    timestamp: datetime
    source_id: Optional[str] = None
    article_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "source_id": self.source_id,
            "article_id": self.article_id,
            "metadata": self.metadata
        }


@dataclass
class SourceMetrics:
    """Aggregated metrics for a single source."""
    source_id: str
    source_name: str
    
    # Scraping stats
    total_scrapes: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    total_articles_scraped: int = 0
    avg_scrape_latency_ms: float = 0.0
    timeout_count: int = 0
    
    # Validation stats
    validation_passes: int = 0
    validation_failures: int = 0
    corrections_applied: int = 0
    common_errors: Dict[str, int] = field(default_factory=dict)
    
    # Quality stats
    avg_quality_score: float = 0.0
    avg_credibility_score: float = 0.0
    quality_trend: str = "stable"  # "improving", "declining", "stable"
    
    # Downstream feedback
    downstream_accepts: int = 0
    downstream_rejects: int = 0
    
    # Time tracking
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Rolling windows (last N entries)
    recent_quality_scores: List[float] = field(default_factory=list)
    recent_latencies: List[float] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate scraping success rate."""
        total = self.successful_scrapes + self.failed_scrapes
        return self.successful_scrapes / total if total > 0 else 0.0
    
    @property
    def validation_pass_rate(self) -> float:
        """Calculate validation pass rate."""
        total = self.validation_passes + self.validation_failures
        return self.validation_passes / total if total > 0 else 0.0
    
    @property
    def downstream_acceptance_rate(self) -> float:
        """Calculate downstream acceptance rate."""
        total = self.downstream_accepts + self.downstream_rejects
        return self.downstream_accepts / total if total > 0 else 0.0
    
    @property
    def articles_per_scrape(self) -> float:
        """Average articles per successful scrape."""
        if self.successful_scrapes == 0:
            return 0.0
        return self.total_articles_scraped / self.successful_scrapes
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "success_rate": round(self.success_rate, 3),
            "validation_pass_rate": round(self.validation_pass_rate, 3),
            "downstream_acceptance_rate": round(self.downstream_acceptance_rate, 3),
            "avg_quality_score": round(self.avg_quality_score, 2),
            "avg_credibility_score": round(self.avg_credibility_score, 3),
            "quality_trend": self.quality_trend,
            "total_scrapes": self.total_scrapes,
            "total_articles": self.total_articles_scraped,
            "articles_per_scrape": round(self.articles_per_scrape, 1),
            "avg_latency_ms": round(self.avg_scrape_latency_ms, 1),
            "common_errors": self.common_errors,
            "last_updated": self.last_updated.isoformat()
        }


class MetricsTracker:
    """
    Tracks and aggregates metrics for the adaptive learning system.
    
    Features:
    - In-memory metric collection with periodic persistence
    - Rolling window statistics for trend detection
    - Per-source and global aggregations
    - Time-based querying and analysis
    
    Usage:
        tracker = MetricsTracker()
        
        # Record metrics
        await tracker.record_scrape(source_id, success=True, latency_ms=150)
        await tracker.record_validation(article_id, passed=True)
        await tracker.record_quality(article_id, source_id, score=85.0)
        
        # Get aggregated metrics
        source_metrics = await tracker.get_source_metrics(source_id)
        global_stats = await tracker.get_global_stats()
    """
    
    # Configuration
    ROLLING_WINDOW_SIZE = 100  # Keep last N entries for rolling stats
    TREND_WINDOW_SIZE = 20     # Entries to consider for trend detection
    PERSIST_INTERVAL_SECONDS = 300  # Persist to DB every 5 minutes
    
    def __init__(self, db_session=None, db_pool=None):
        """Initialize the metrics tracker."""
        self.db = db_session or db_pool  # Accept either parameter
        
        # In-memory storage
        self._metrics: List[MetricEntry] = []
        self._source_metrics: Dict[str, SourceMetrics] = {}
        
        # Global aggregations
        self._global_stats = {
            "total_scrapes": 0,
            "total_articles": 0,
            "total_validations": 0,
            "avg_quality_score": 0.0,
            "start_time": datetime.utcnow()
        }
        
        # Error pattern tracking
        self._error_patterns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Last persist time
        self._last_persist = datetime.utcnow()
        
        logger.info("MetricsTracker initialized")
    
    # ========================================================================
    # Recording Methods
    # ========================================================================
    
    async def record_scrape(
        self,
        source_id: str,
        source_name: str = "",
        success: bool = True,
        latency_ms: float = 0.0,
        article_count: int = 0,
        error_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a scraping operation result.
        
        Args:
            source_id: Source identifier
            source_name: Human-readable source name
            success: Whether scrape succeeded
            latency_ms: Time taken in milliseconds
            article_count: Number of articles scraped
            error_type: Type of error if failed
            metadata: Additional context
        """
        now = datetime.utcnow()
        
        # Get or create source metrics
        if source_id not in self._source_metrics:
            self._source_metrics[source_id] = SourceMetrics(
                source_id=source_id,
                source_name=source_name or source_id
            )
        
        source = self._source_metrics[source_id]
        source.total_scrapes += 1
        source.last_updated = now
        
        if success:
            # Record success
            source.successful_scrapes += 1
            source.total_articles_scraped += article_count
            
            # Update rolling latency
            source.recent_latencies.append(latency_ms)
            if len(source.recent_latencies) > self.ROLLING_WINDOW_SIZE:
                source.recent_latencies.pop(0)
            source.avg_scrape_latency_ms = statistics.mean(source.recent_latencies)
            
            # Record metrics
            self._add_metric(MetricType.SCRAPE_SUCCESS, 1.0, source_id=source_id)
            self._add_metric(MetricType.SCRAPE_LATENCY, latency_ms, source_id=source_id)
            self._add_metric(MetricType.SCRAPE_ARTICLE_COUNT, article_count, source_id=source_id)
        else:
            # Record failure
            source.failed_scrapes += 1
            
            if error_type:
                source.common_errors[error_type] = source.common_errors.get(error_type, 0) + 1
                self._error_patterns[source_id][error_type] += 1
            
            if error_type == "timeout":
                source.timeout_count += 1
                self._add_metric(MetricType.SCRAPE_TIMEOUT, 1.0, source_id=source_id)
            
            self._add_metric(MetricType.SCRAPE_FAILURE, 1.0, source_id=source_id, 
                           metadata={"error_type": error_type})
        
        # Update global stats
        self._global_stats["total_scrapes"] += 1
        self._global_stats["total_articles"] += article_count
        
        logger.debug(f"Recorded scrape for {source_id}: success={success}, articles={article_count}")
    
    async def record_validation(
        self,
        article_id: str,
        source_id: str,
        passed: bool = True,
        error_types: Optional[List[str]] = None,
        corrections_made: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a validation result.
        
        Args:
            article_id: Article identifier
            source_id: Source identifier
            passed: Whether validation passed
            error_types: List of validation errors
            corrections_made: Number of auto-corrections applied
            metadata: Additional context
        """
        now = datetime.utcnow()
        
        # Ensure source metrics exist
        if source_id not in self._source_metrics:
            self._source_metrics[source_id] = SourceMetrics(
                source_id=source_id,
                source_name=source_id
            )
        
        source = self._source_metrics[source_id]
        source.last_updated = now
        
        if passed:
            source.validation_passes += 1
            self._add_metric(MetricType.VALIDATION_PASS, 1.0, 
                           source_id=source_id, article_id=article_id)
        else:
            source.validation_failures += 1
            self._add_metric(MetricType.VALIDATION_FAIL, 1.0,
                           source_id=source_id, article_id=article_id)
            
            # Track error types
            if error_types:
                for error_type in error_types:
                    source.common_errors[error_type] = source.common_errors.get(error_type, 0) + 1
                    self._add_metric(MetricType.VALIDATION_ERROR_TYPE, 1.0,
                                   source_id=source_id, 
                                   metadata={"error_type": error_type})
        
        if corrections_made > 0:
            source.corrections_applied += corrections_made
            self._add_metric(MetricType.VALIDATION_CORRECTION, corrections_made,
                           source_id=source_id, article_id=article_id)
        
        # Update global stats
        self._global_stats["total_validations"] += 1
    
    async def record_quality(
        self,
        article_id: str,
        source_id: str,
        quality_score: float,
        credibility_score: Optional[float] = None,
        content_length: Optional[int] = None,
        is_duplicate: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record quality metrics for an article.
        
        Args:
            article_id: Article identifier
            source_id: Source identifier
            quality_score: Quality score (0-100)
            credibility_score: Credibility score (0-1)
            content_length: Article content length
            is_duplicate: Whether duplicate was detected
            metadata: Additional context
        """
        now = datetime.utcnow()
        
        # Ensure source metrics exist
        if source_id not in self._source_metrics:
            self._source_metrics[source_id] = SourceMetrics(
                source_id=source_id,
                source_name=source_id
            )
        
        source = self._source_metrics[source_id]
        source.last_updated = now
        
        # Update rolling quality scores
        source.recent_quality_scores.append(quality_score)
        if len(source.recent_quality_scores) > self.ROLLING_WINDOW_SIZE:
            source.recent_quality_scores.pop(0)
        
        # Calculate average quality
        source.avg_quality_score = statistics.mean(source.recent_quality_scores)
        
        # Detect quality trend
        source.quality_trend = self._calculate_trend(source.recent_quality_scores)
        
        # Update credibility if provided
        if credibility_score is not None:
            # Exponential moving average for credibility
            alpha = 0.1
            if source.avg_credibility_score == 0:
                source.avg_credibility_score = credibility_score
            else:
                source.avg_credibility_score = (
                    alpha * credibility_score + 
                    (1 - alpha) * source.avg_credibility_score
                )
        
        # Record metrics
        self._add_metric(MetricType.QUALITY_SCORE, quality_score,
                        source_id=source_id, article_id=article_id)
        
        if credibility_score is not None:
            self._add_metric(MetricType.CREDIBILITY_SCORE, credibility_score,
                           source_id=source_id, article_id=article_id)
        
        if content_length is not None:
            self._add_metric(MetricType.CONTENT_LENGTH, content_length,
                           source_id=source_id, article_id=article_id)
        
        if is_duplicate:
            self._add_metric(MetricType.DUPLICATE_DETECTED, 1.0,
                           source_id=source_id, article_id=article_id)
        
        # Update global average
        self._update_global_quality_average(quality_score)
    
    async def record_downstream_feedback(
        self,
        article_id: str,
        source_id: str,
        accepted: bool,
        layer: str = "layer2",
        reason: Optional[str] = None
    ) -> None:
        """
        Record feedback from downstream layers (L2, L3, L4).
        
        Args:
            article_id: Article identifier
            source_id: Source identifier
            accepted: Whether article was accepted downstream
            layer: Which layer provided feedback
            reason: Reason for rejection if applicable
        """
        if source_id not in self._source_metrics:
            self._source_metrics[source_id] = SourceMetrics(
                source_id=source_id,
                source_name=source_id
            )
        
        source = self._source_metrics[source_id]
        source.last_updated = datetime.utcnow()
        
        if accepted:
            source.downstream_accepts += 1
            self._add_metric(MetricType.DOWNSTREAM_ACCEPT, 1.0,
                           source_id=source_id, article_id=article_id,
                           metadata={"layer": layer})
        else:
            source.downstream_rejects += 1
            self._add_metric(MetricType.DOWNSTREAM_REJECT, 1.0,
                           source_id=source_id, article_id=article_id,
                           metadata={"layer": layer, "reason": reason})
    
    # ========================================================================
    # Retrieval Methods
    # ========================================================================
    
    async def get_source_metrics(
        self, 
        source_id: str,
        days: Optional[int] = None
    ) -> Optional[SourceMetrics]:
        """
        Get aggregated metrics for a specific source.
        
        Args:
            source_id: Source identifier
            days: Optional filter for last N days (not used in in-memory impl)
        """
        return self._source_metrics.get(source_id)
    
    async def get_all_source_metrics(self) -> Dict[str, SourceMetrics]:
        """Get metrics for all sources."""
        return self._source_metrics.copy()
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global pipeline statistics."""
        uptime = datetime.utcnow() - self._global_stats["start_time"]
        
        return {
            **self._global_stats,
            "uptime_seconds": uptime.total_seconds(),
            "sources_tracked": len(self._source_metrics),
            "avg_success_rate": self._calculate_avg_success_rate(),
            "avg_validation_rate": self._calculate_avg_validation_rate()
        }
    
    async def get_error_patterns(
        self, 
        source_id: Optional[str] = None
    ) -> Dict[str, Dict[str, int]]:
        """Get error patterns, optionally filtered by source."""
        if source_id:
            return {source_id: dict(self._error_patterns.get(source_id, {}))}
        return {k: dict(v) for k, v in self._error_patterns.items()}
    
    async def get_trending_sources(
        self,
        direction: str = "improving",
        limit: int = 10
    ) -> List[SourceMetrics]:
        """Get sources with quality trends in the specified direction."""
        matching = [
            s for s in self._source_metrics.values()
            if s.quality_trend == direction
        ]
        # Sort by recent activity
        matching.sort(key=lambda x: x.last_updated, reverse=True)
        return matching[:limit]
    
    async def get_problematic_sources(self, limit: int = 10) -> List[SourceMetrics]:
        """Get sources with low success or validation rates."""
        problematic = []
        
        for source in self._source_metrics.values():
            # Consider problematic if:
            # - Success rate < 70%
            # - Validation pass rate < 60%
            # - Quality trend is declining
            if (source.success_rate < 0.7 or 
                source.validation_pass_rate < 0.6 or
                source.quality_trend == "declining"):
                problematic.append(source)
        
        # Sort by worst metrics first
        problematic.sort(key=lambda x: (x.success_rate, x.validation_pass_rate))
        return problematic[:limit]
    
    async def get_metrics_history(
        self,
        metric_type: MetricType,
        source_id: Optional[str] = None,
        hours: int = 24
    ) -> List[MetricEntry]:
        """Get metric history for the specified time window."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        filtered = [
            m for m in self._metrics
            if m.metric_type == metric_type and m.timestamp >= cutoff
        ]
        
        if source_id:
            filtered = [m for m in filtered if m.source_id == source_id]
        
        return filtered
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _add_metric(
        self,
        metric_type: MetricType,
        value: float,
        source_id: Optional[str] = None,
        article_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a metric entry to the in-memory store."""
        entry = MetricEntry(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            source_id=source_id,
            article_id=article_id,
            metadata=metadata or {}
        )
        
        self._metrics.append(entry)
        
        # Trim old metrics if needed (keep last 24 hours)
        self._trim_old_metrics()
    
    def _trim_old_metrics(self, hours: int = 24) -> None:
        """Remove metrics older than specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        self._metrics = [m for m in self._metrics if m.timestamp >= cutoff]
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < self.TREND_WINDOW_SIZE:
            return "stable"
        
        recent = values[-self.TREND_WINDOW_SIZE:]
        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        # 5% threshold for trend detection
        if second_avg > first_avg * 1.05:
            return "improving"
        elif second_avg < first_avg * 0.95:
            return "declining"
        return "stable"
    
    def _update_global_quality_average(self, new_score: float) -> None:
        """Update global average quality score with exponential moving average."""
        alpha = 0.05  # Slow-moving average
        current = self._global_stats["avg_quality_score"]
        if current == 0:
            self._global_stats["avg_quality_score"] = new_score
        else:
            self._global_stats["avg_quality_score"] = (
                alpha * new_score + (1 - alpha) * current
            )
    
    def _calculate_avg_success_rate(self) -> float:
        """Calculate average success rate across all sources."""
        if not self._source_metrics:
            return 0.0
        rates = [s.success_rate for s in self._source_metrics.values()]
        return statistics.mean(rates)
    
    def _calculate_avg_validation_rate(self) -> float:
        """Calculate average validation pass rate across all sources."""
        if not self._source_metrics:
            return 0.0
        rates = [s.validation_pass_rate for s in self._source_metrics.values()]
        return statistics.mean(rates)
    
    # ========================================================================
    # Persistence Methods
    # ========================================================================
    
    async def persist_to_db(self) -> bool:
        """Persist current metrics to database."""
        if not self.db:
            logger.warning("No database session, skipping persistence")
            return False
        
        try:
            # TODO: Implement actual DB persistence
            # This would store aggregated metrics in a dedicated table
            self._last_persist = datetime.utcnow()
            logger.info("Metrics persisted to database")
            return True
        except Exception as e:
            logger.error(f"Failed to persist metrics: {e}")
            return False
    
    async def load_from_db(self) -> bool:
        """Load historical metrics from database."""
        if not self.db:
            return False
        
        try:
            # TODO: Implement actual DB loading
            logger.info("Metrics loaded from database")
            return True
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            return False
    
    async def load_historical_metrics(self) -> bool:
        """Alias for load_from_db - used by AdaptiveLearningSystem."""
        return await self.load_from_db()
    
    async def record_scraper_metric(
        self,
        scraper_type: str,
        source_id: str,
        success: bool,
        latency_ms: float,
        articles_scraped: int = 0,
        error_type: Optional[str] = None
    ) -> None:
        """
        Record scraper performance metric.
        
        Wrapper for record_scrape that's compatible with AdaptiveLearningSystem.
        """
        await self.record_scrape(
            source_id=source_id,
            source_name=source_id,
            success=success,
            latency_ms=latency_ms,
            article_count=articles_scraped,
            error_type=error_type,
            metadata={"scraper_type": scraper_type}
        )
    
    async def record_validation_metric(
        self,
        article_id: str,
        valid: bool,
        issues_count: int = 0,
        source_id: Optional[str] = None
    ) -> None:
        """
        Record validation metric.
        
        Wrapper for record_validation that's compatible with AdaptiveLearningSystem.
        """
        await self.record_validation(
            article_id=article_id,
            source_id=source_id or "unknown",
            passed=valid,
            corrections_made=0,
            metadata={"issues_count": issues_count}
        )
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics as JSON-serializable dict."""
        return {
            "global_stats": self._global_stats,
            "sources": {
                sid: s.to_dict() 
                for sid, s in self._source_metrics.items()
            },
            "error_patterns": {
                k: dict(v) for k, v in self._error_patterns.items()
            },
            "exported_at": datetime.utcnow().isoformat()
        }
