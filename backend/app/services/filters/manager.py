import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.services.reputation import ReputationManager, FilterAction, FilterResult
from app.services.filters.config import FilterConfig, FilterStats
from app.services.filters.pre_filter import PreProcessor
from app.services.filters.post_filter import PostProcessor


logger = logging.getLogger(__name__)

class QualityFilter:
    """Facade for article filtering."""
    
    def __init__(self, db: Session, config: Optional[FilterConfig] = None, reputation_manager: Optional[ReputationManager] = None):
        self.db = db
        self.config = config or FilterConfig()
        self.reputation_manager = reputation_manager or ReputationManager(db)
        
        self.pre_processor = PreProcessor(self.db, self.config, self.reputation_manager, logger)
        self.post_processor = PostProcessor(self.db, self.config, self.reputation_manager, logger)
        
        self._stats = FilterStats()
        self._session_start = datetime.utcnow()
        
    async def pre_filter(self, article_id: str, source_name: str, article_metadata: Optional[Dict[str, Any]] = None) -> FilterResult:
        result = await self.pre_processor.process(article_id, source_name, article_metadata)
        source = await self.reputation_manager.get_or_create_source(source_name)
        await self._log_decision(article_id, source.id, result)
        self._update_stats(result)
        return result
        
    async def post_filter(self, article_id: str, source_name: str, quality_score: float, confidence_score: Optional[float] = None) -> FilterResult:
        result = await self.post_processor.process(article_id, source_name, quality_score, confidence_score)
        source = await self.reputation_manager.get_or_create_source(source_name)
        await self._log_decision(article_id, source.id, result)
        self._update_stats(result, quality_score, result.source_reputation)
        return result
        
    async def filter_batch(self, articles: List[Dict[str, Any]], quality_scores: Optional[Dict[str, float]] = None) -> Dict[str, FilterResult]:
        results = {}
        for article in articles:
            article_id = article.get('id') or article.get('article_id')
            source_name = article.get('source_name') or article.get('source', {}).get('name')
            if not article_id or not source_name:
                continue
            if quality_scores and article_id in quality_scores:
                result = await self.post_filter(article_id, source_name, quality_scores[article_id])
            else:
                result = await self.pre_filter(article_id, source_name, article)
            results[article_id] = result
        return results

    async def _log_decision(self, article_id: str, source_id: int, result: FilterResult) -> None:
        from app.models.source_reputation_models import QualityFilterLog
        if not self.config.log_all_decisions:
            if self.config.log_rejections_only and result.action != FilterAction.REJECTED:
                return
        
        log_entry = QualityFilterLog(
            article_id=article_id,
            source_id=source_id,
            action=result.action.value,
            action_reason=result.reason,
            source_reputation_score=result.source_reputation,
            article_quality_score=result.article_quality,
            threshold_applied=self.config.min_quality_score,
            weight_multiplier=result.weight_multiplier,
            filter_latency_ms=result.processing_time_ms
        )
        self.db.add(log_entry)
        
    def _update_stats(self, result: FilterResult, quality_score: Optional[float] = None, reputation_score: Optional[float] = None) -> None:
        self._stats.total_processed += 1
        if result.action == FilterAction.ACCEPTED:
            self._stats.accepted += 1
        elif result.action == FilterAction.REJECTED:
            self._stats.rejected += 1
        elif result.action == FilterAction.FLAGGED:
            self._stats.flagged += 1
        elif result.action == FilterAction.BOOSTED:
            self._stats.boosted += 1
        elif result.action == FilterAction.DOWNGRADED:
            self._stats.downgraded += 1
            
        self._stats.total_filter_time_ms += result.processing_time_ms
        self._stats.avg_filter_time_ms = self._stats.total_filter_time_ms / self._stats.total_processed
        
        if quality_score is not None:
            n = self._stats.total_processed
            self._stats.avg_quality_score = ((self._stats.avg_quality_score * (n - 1)) + quality_score) / n
        if reputation_score is not None:
            n = self._stats.total_processed
            self._stats.avg_reputation_score = ((self._stats.avg_reputation_score * (n - 1)) + reputation_score) / n

    def get_session_stats(self) -> FilterStats:
        return self._stats
        
    def reset_session_stats(self) -> None:
        self._stats = FilterStats()
        self._session_start = datetime.utcnow()
        
    async def get_filter_analytics(self, hours: int = 24) -> Dict[str, Any]:
        from app.models.source_reputation_models import QualityFilterLog
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        action_counts = self.db.query(QualityFilterLog.action, func.count(QualityFilterLog.id)).filter(QualityFilterLog.created_at >= cutoff).group_by(QualityFilterLog.action).all()
        action_dict = {action: count for action, count in action_counts}
        
        avg_quality = self.db.query(func.avg(QualityFilterLog.article_quality_score)).filter(and_(QualityFilterLog.created_at >= cutoff, QualityFilterLog.article_quality_score != None)).scalar() or 0.0
        avg_latency = self.db.query(func.avg(QualityFilterLog.filter_latency_ms)).filter(QualityFilterLog.created_at >= cutoff).scalar() or 0.0
        
        return {
            "period_hours": hours,
            "actions": action_dict,
            "total_decisions": sum(action_dict.values()),
            "avg_quality": float(avg_quality),
            "avg_latency_ms": float(avg_latency)
        }
