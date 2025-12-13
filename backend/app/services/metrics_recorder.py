"""
Metrics Recorder Service

Records scraping and processing metrics to TimescaleDB for observability.
Implements the Data Observability patterns from the Layer 1 blueprint.

Hypertables used:
- source_health_metrics: Scraper performance and source reliability
- mention_timeseries: Track keyword/topic mentions over time
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

# Try to import database dependencies
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import text
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    AsyncSession = None


@dataclass
class SourceHealthMetric:
    """Metrics for source scraping performance."""
    source_id: int
    source_name: str
    scrape_duration_seconds: int
    articles_collected: int
    errors_count: int
    success_rate: float
    avg_credibility: Optional[float] = None
    avg_word_count: Optional[int] = None
    duplicate_rate: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class MentionMetric:
    """Metrics for keyword/topic mentions."""
    keyword: str
    source_type: str  # 'news', 'social', 'all'
    mention_count: int
    unique_sources: int
    avg_sentiment: Optional[float] = None
    sentiment_variance: Optional[float] = None
    top_location: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class MetricsRecorder:
    """
    Records metrics to TimescaleDB for data observability.
    
    Usage:
        recorder = MetricsRecorder(db_session)
        await recorder.record_source_health(metric)
        await recorder.record_mention(keyword, count, sources)
    """
    
    # SQL for creating hypertables (run once during setup)
    CREATE_TABLES_SQL = """
    -- Source health metrics hypertable
    CREATE TABLE IF NOT EXISTS source_health_metrics (
        time TIMESTAMPTZ NOT NULL,
        source_id INTEGER NOT NULL,
        source_name VARCHAR(100),
        
        scrape_duration_seconds INTEGER,
        articles_collected INTEGER,
        errors_count INTEGER,
        success_rate DECIMAL(4,3),
        
        avg_credibility DECIMAL(3,2),
        avg_word_count INTEGER,
        duplicate_rate DECIMAL(4,3),
        
        PRIMARY KEY (time, source_id)
    );
    
    -- Convert to hypertable if not already
    SELECT create_hypertable('source_health_metrics', 'time', 
        if_not_exists => TRUE);
    
    -- Mention timeseries hypertable
    CREATE TABLE IF NOT EXISTS mention_timeseries (
        time TIMESTAMPTZ NOT NULL,
        keyword VARCHAR(100) NOT NULL,
        source_type VARCHAR(20) NOT NULL,
        
        mention_count INTEGER NOT NULL,
        unique_sources INTEGER,
        
        avg_sentiment DECIMAL(4,3),
        sentiment_variance DECIMAL(4,3),
        
        top_location VARCHAR(50),
        
        PRIMARY KEY (time, keyword, source_type)
    );
    
    SELECT create_hypertable('mention_timeseries', 'time',
        if_not_exists => TRUE);
    
    -- Create indexes for fast keyword lookups
    CREATE INDEX IF NOT EXISTS idx_mention_keyword 
        ON mention_timeseries(keyword, time DESC);
    """
    
    def __init__(self, db_session: Optional['AsyncSession'] = None):
        """
        Initialize the metrics recorder.
        
        Args:
            db_session: Async database session for TimescaleDB
        """
        self.db = db_session
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_size = 50  # Batch insert threshold
    
    async def record_source_health(self, metric: SourceHealthMetric) -> bool:
        """
        Record source health metrics.
        
        Args:
            metric: SourceHealthMetric dataclass
            
        Returns:
            True if recorded successfully
        """
        if not self.db:
            logger.debug(f"No DB session - buffering metric for {metric.source_name}")
            self._buffer.append({
                "type": "source_health",
                "data": metric
            })
            return False
        
        try:
            sql = text("""
                INSERT INTO source_health_metrics (
                    time, source_id, source_name,
                    scrape_duration_seconds, articles_collected, errors_count,
                    success_rate, avg_credibility, avg_word_count, duplicate_rate
                ) VALUES (
                    :time, :source_id, :source_name,
                    :scrape_duration, :articles, :errors,
                    :success_rate, :avg_credibility, :avg_word_count, :duplicate_rate
                )
                ON CONFLICT (time, source_id) DO UPDATE SET
                    articles_collected = EXCLUDED.articles_collected,
                    errors_count = EXCLUDED.errors_count
            """)
            
            await self.db.execute(sql, {
                "time": metric.timestamp,
                "source_id": metric.source_id,
                "source_name": metric.source_name,
                "scrape_duration": metric.scrape_duration_seconds,
                "articles": metric.articles_collected,
                "errors": metric.errors_count,
                "success_rate": metric.success_rate,
                "avg_credibility": metric.avg_credibility,
                "avg_word_count": metric.avg_word_count,
                "duplicate_rate": metric.duplicate_rate
            })
            await self.db.commit()
            
            logger.debug(f"Recorded health metric for {metric.source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record source health metric: {e}")
            return False
    
    async def record_mention(self, metric: MentionMetric) -> bool:
        """
        Record keyword/topic mention metric.
        
        Args:
            metric: MentionMetric dataclass
            
        Returns:
            True if recorded successfully
        """
        if not self.db:
            logger.debug(f"No DB session - buffering mention for {metric.keyword}")
            self._buffer.append({
                "type": "mention",
                "data": metric
            })
            return False
        
        try:
            sql = text("""
                INSERT INTO mention_timeseries (
                    time, keyword, source_type,
                    mention_count, unique_sources,
                    avg_sentiment, sentiment_variance, top_location
                ) VALUES (
                    :time, :keyword, :source_type,
                    :mention_count, :unique_sources,
                    :avg_sentiment, :sentiment_variance, :top_location
                )
                ON CONFLICT (time, keyword, source_type) DO UPDATE SET
                    mention_count = mention_timeseries.mention_count + EXCLUDED.mention_count,
                    unique_sources = GREATEST(mention_timeseries.unique_sources, EXCLUDED.unique_sources)
            """)
            
            await self.db.execute(sql, {
                "time": metric.timestamp,
                "keyword": metric.keyword,
                "source_type": metric.source_type,
                "mention_count": metric.mention_count,
                "unique_sources": metric.unique_sources,
                "avg_sentiment": metric.avg_sentiment,
                "sentiment_variance": metric.sentiment_variance,
                "top_location": metric.top_location
            })
            await self.db.commit()
            
            logger.debug(f"Recorded mention metric for '{metric.keyword}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record mention metric: {e}")
            return False
    
    async def record_scrape_cycle(
        self,
        source_name: str,
        source_id: int,
        duration_seconds: int,
        articles_found: int,
        articles_new: int,
        errors: int,
        avg_quality: float = None
    ) -> bool:
        """
        Convenience method to record a complete scrape cycle result.
        
        Args:
            source_name: Name of the source
            source_id: ID of the source
            duration_seconds: How long the scrape took
            articles_found: Total articles found
            articles_new: New articles (not duplicates)
            errors: Number of errors
            avg_quality: Average quality score
            
        Returns:
            True if recorded successfully
        """
        success_rate = 1.0 if errors == 0 else (articles_found / (articles_found + errors))
        duplicate_rate = (articles_found - articles_new) / articles_found if articles_found > 0 else 0
        
        metric = SourceHealthMetric(
            source_id=source_id,
            source_name=source_name,
            scrape_duration_seconds=duration_seconds,
            articles_collected=articles_new,
            errors_count=errors,
            success_rate=round(success_rate, 3),
            avg_credibility=avg_quality,
            duplicate_rate=round(duplicate_rate, 3)
        )
        
        return await self.record_source_health(metric)
    
    async def record_keyword_mentions(
        self,
        keywords: Dict[str, int],
        source_type: str = "news",
        unique_sources: int = 1
    ) -> int:
        """
        Record multiple keyword mentions from an article batch.
        
        Args:
            keywords: Dict mapping keyword to mention count
            source_type: Type of source ('news', 'social', 'all')
            unique_sources: Number of unique sources that mentioned keywords
            
        Returns:
            Number of successfully recorded keywords
        """
        recorded = 0
        for keyword, count in keywords.items():
            if count > 0:
                metric = MentionMetric(
                    keyword=keyword,
                    source_type=source_type,
                    mention_count=count,
                    unique_sources=unique_sources
                )
                if await self.record_mention(metric):
                    recorded += 1
        return recorded
    
    async def flush_buffer(self) -> int:
        """
        Flush buffered metrics (for when DB session becomes available).
        
        Returns:
            Number of metrics flushed
        """
        if not self._buffer or not self.db:
            return 0
        
        flushed = 0
        for item in self._buffer:
            try:
                if item["type"] == "source_health":
                    await self.record_source_health(item["data"])
                elif item["type"] == "mention":
                    await self.record_mention(item["data"])
                flushed += 1
            except Exception as e:
                logger.warning(f"Failed to flush metric: {e}")
        
        self._buffer.clear()
        return flushed
    
    def get_buffer_size(self) -> int:
        """Get number of buffered metrics."""
        return len(self._buffer)


# Singleton instance for easy access
_metrics_recorder: Optional[MetricsRecorder] = None


def get_metrics_recorder(db_session: Optional['AsyncSession'] = None) -> MetricsRecorder:
    """
    Get or create the metrics recorder singleton.
    
    Args:
        db_session: Optional async database session
        
    Returns:
        MetricsRecorder instance
    """
    global _metrics_recorder
    if _metrics_recorder is None:
        _metrics_recorder = MetricsRecorder(db_session)
    elif db_session is not None:
        _metrics_recorder.db = db_session
    return _metrics_recorder


# Convenience functions for recording metrics
async def record_scrape_health(
    source_name: str,
    source_id: int = 0,
    duration_seconds: int = 0,
    articles_new: int = 0,
    errors: int = 0
) -> bool:
    """Quick helper to record scrape health metrics."""
    recorder = get_metrics_recorder()
    return await recorder.record_scrape_cycle(
        source_name=source_name,
        source_id=source_id,
        duration_seconds=duration_seconds,
        articles_found=articles_new,
        articles_new=articles_new,
        errors=errors
    )
