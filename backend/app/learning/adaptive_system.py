"""
Adaptive Learning System - Main Integration Module

This is the central controller that integrates all learning components
and provides a unified interface for the Layer 1 pipeline.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from app.learning.metrics_tracker import MetricsTracker, MetricType, SourceMetrics
from app.learning.feedback_loop import FeedbackLoop, FeedbackType, FeedbackSignal
from app.learning.auto_tuner import AutoTuner, TuningConfig
from app.learning.performance_optimizer import PerformanceOptimizer, RetryStrategy
from app.learning.quality_analyzer import QualityAnalyzer, QualityReport

logger = logging.getLogger(__name__)


class LearningMode(Enum):
    """Operating modes for the learning system."""
    PASSIVE = "passive"       # Only collect data, no auto-tuning
    ADVISORY = "advisory"     # Collect + provide recommendations
    ACTIVE = "active"         # Full auto-tuning enabled


@dataclass
class LearningSystemConfig:
    """Configuration for the Adaptive Learning System."""
    mode: LearningMode = LearningMode.ADVISORY
    
    # Component toggles
    enable_metrics: bool = True
    enable_feedback: bool = True
    enable_auto_tuning: bool = True
    enable_performance_optimization: bool = True
    enable_quality_analysis: bool = True
    
    # Learning parameters
    learning_interval_hours: int = 6
    min_samples_for_learning: int = 100
    
    # Auto-tuning limits
    max_change_per_cycle: float = 0.05  # 5% max change
    cooldown_hours: int = 24
    
    # Quality thresholds
    quality_alert_threshold: float = 0.7
    degradation_alert_threshold: float = 0.1


@dataclass
class SystemHealth:
    """Overall health status of the learning system."""
    status: str  # "healthy", "degraded", "unhealthy"
    quality_score: float
    quality_trend: str
    active_issues: int
    pending_recommendations: int
    last_learning_cycle: Optional[datetime]
    components_status: Dict[str, str]
    message: str


class AdaptiveLearningSystem:
    """
    Central controller for the Adaptive Learning System.
    
    Integrates all learning components and provides:
    - Unified API for recording events
    - Coordinated learning cycles
    - System-wide health monitoring
    - Graceful degradation handling
    """
    
    def __init__(
        self,
        db_pool=None,
        config: Optional[LearningSystemConfig] = None
    ):
        self.db_pool = db_pool
        self.config = config or LearningSystemConfig()
        
        # Initialize components
        self.metrics = MetricsTracker(db_pool=db_pool) if self.config.enable_metrics else None
        self.feedback = FeedbackLoop(db_pool=db_pool) if self.config.enable_feedback else None
        self.auto_tuner = AutoTuner(db_pool=db_pool) if self.config.enable_auto_tuning else None
        self.performance = PerformanceOptimizer(
            db_pool=db_pool
        ) if self.config.enable_performance_optimization else None
        self.quality = QualityAnalyzer(
            db_pool=db_pool
        ) if self.config.enable_quality_analysis else None
        
        # State tracking
        self._initialized = False
        self._last_learning_cycle: Optional[datetime] = None
        self._learning_lock = asyncio.Lock()
        self._component_errors: Dict[str, int] = {}
        
        # Learning interval
        self._learning_interval = timedelta(hours=self.config.learning_interval_hours)
        
        logger.info(
            f"AdaptiveLearningSystem initialized in {self.config.mode.value} mode"
        )
    
    async def initialize(self) -> None:
        """Initialize the learning system and load historical data."""
        if self._initialized:
            return
        
        try:
            # Load historical data for each component
            if self.metrics:
                await self.metrics.load_historical_metrics()
            
            if self.feedback:
                await self.feedback.load_historical_feedback()
            
            if self.auto_tuner:
                await self.auto_tuner.load_state()
            
            if self.performance:
                await self.performance.load_profiles()
            
            if self.quality:
                await self.quality.load_historical_data()
            
            self._initialized = True
            logger.info("AdaptiveLearningSystem fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize learning system: {e}")
            # Continue anyway - system can work without historical data
            self._initialized = True
    
    # ==========================================================================
    # Event Recording APIs
    # ==========================================================================
    
    async def record_scrape_result(
        self,
        source_id: str,
        scraper_type: str,
        success: bool,
        articles_count: int = 0,
        latency_ms: float = 0,
        error_type: Optional[str] = None
    ) -> None:
        """
        Record the result of a scraping operation.
        
        Called after each scraping attempt to track performance.
        """
        try:
            # Record in metrics tracker
            if self.metrics:
                await self.metrics.record_scraper_metric(
                    scraper_type=scraper_type,
                    source_id=source_id,
                    success=success,
                    latency_ms=latency_ms,
                    articles_scraped=articles_count
                )
            
            # Record in performance optimizer
            if self.performance:
                await self.performance.record_request(
                    entity_id=source_id,
                    entity_type="source",
                    success=success,
                    latency_ms=latency_ms,
                    error_type=error_type
                )
            
            self._clear_component_error("metrics")
            self._clear_component_error("performance")
            
        except Exception as e:
            self._record_component_error("metrics", e)
            logger.warning(f"Error recording scrape result: {e}")
    
    async def record_validation_result(
        self,
        article_id: str,
        source_id: str,
        valid: bool,
        issues: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Record the result of article validation.
        
        Called after validating an article to track quality.
        """
        try:
            # Record in metrics
            if self.metrics:
                await self.metrics.record_validation_metric(
                    article_id=article_id,
                    valid=valid,
                    issues_count=len(issues) if issues else 0
                )
            
            # Analyze quality issues
            if self.quality and issues:
                article_data = {"id": article_id, "source_id": source_id}
                for issue in issues:
                    article_data.update(issue)
                await self.quality.analyze_article(
                    article_data, source_id
                )
            
            self._clear_component_error("quality")
            
        except Exception as e:
            self._record_component_error("quality", e)
            logger.warning(f"Error recording validation result: {e}")
    
    async def record_article_outcome(
        self,
        article_id: str,
        source_id: str,
        used_by_downstream: bool,
        quality_rating: Optional[float] = None,
        feedback_type: Optional[str] = None
    ) -> None:
        """
        Record downstream usage of an article.
        
        Called when downstream layers process articles to provide feedback.
        """
        try:
            if self.feedback:
                signal = FeedbackSignal(
                    article_id=article_id,
                    source_id=source_id,
                    feedback_type=FeedbackType(feedback_type) if feedback_type else (
                        FeedbackType.ARTICLE_USEFUL if used_by_downstream 
                        else FeedbackType.ARTICLE_DISCARDED
                    ),
                    quality_rating=quality_rating,
                    timestamp=datetime.now()
                )
                await self.feedback.process_feedback(signal)
            
            self._clear_component_error("feedback")
            
        except Exception as e:
            self._record_component_error("feedback", e)
            logger.warning(f"Error recording article outcome: {e}")
    
    # ==========================================================================
    # Query APIs
    # ==========================================================================
    
    async def get_source_recommendations(
        self,
        source_id: str
    ) -> Dict[str, Any]:
        """
        Get all recommendations for a specific source.
        
        Aggregates recommendations from all learning components.
        """
        recommendations = {
            "source_id": source_id,
            "generated_at": datetime.now().isoformat(),
            "parameters": {},
            "performance": {},
            "quality": {},
            "actions": []
        }
        
        try:
            # Get performance recommendations
            if self.performance:
                timing = await self.performance.get_optimal_timing(source_id)
                concurrency = await self.performance.get_optimal_concurrency(source_id)
                retry = await self.performance.get_retry_strategy(source_id)
                
                recommendations["performance"] = {
                    "optimal_timing": timing,
                    "concurrency": concurrency,
                    "retry_strategy": {
                        "max_retries": retry.max_retries,
                        "base_delay_ms": retry.base_delay_ms,
                        "rate_limit_backoff_ms": retry.rate_limit_backoff_ms
                    }
                }
            
            # Get quality analysis
            if self.quality:
                quality_analysis = await self.quality.get_source_quality_analysis(source_id)
                recommendations["quality"] = quality_analysis
            
            # Get source metrics
            if self.metrics:
                metrics = await self.metrics.get_source_metrics(source_id, days=7)
                if metrics:
                    recommendations["parameters"] = {
                        "current_quality_score": metrics.avg_quality_score,
                        "success_rate": metrics.success_rate,
                        "avg_latency_ms": metrics.avg_scrape_latency_ms
                    }
            
            # Generate action items
            actions = self._generate_action_items(recommendations)
            recommendations["actions"] = actions
            
        except Exception as e:
            logger.error(f"Error getting recommendations for {source_id}: {e}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    async def get_optimal_parameters(
        self,
        source_id: str
    ) -> Dict[str, Any]:
        """
        Get optimal parameters for scraping a source.
        
        Used by scrapers to dynamically adjust their behavior.
        """
        params = {
            "source_id": source_id,
            "timeout_ms": 30000,
            "max_retries": 3,
            "retry_delay_ms": 1000,
            "concurrency": 5,
            "batch_size": 10,
            "quality_threshold": 0.5
        }
        
        if self.performance:
            try:
                retry = await self.performance.get_retry_strategy(source_id)
                concurrency = await self.performance.get_optimal_concurrency(source_id)
                
                params.update({
                    "timeout_ms": retry.base_delay_ms,
                    "max_retries": retry.max_retries,
                    "retry_delay_ms": retry.base_delay_ms,
                    "concurrency": concurrency
                })
            except Exception as e:
                logger.warning(f"Error getting optimal parameters: {e}")
        
        if self.auto_tuner:
            try:
                # Get auto-tuned quality threshold
                tuned_params = await self.auto_tuner.get_tuned_parameters(source_id)
                if tuned_params:
                    params.update(tuned_params)
            except Exception as e:
                logger.warning(f"Error getting tuned parameters: {e}")
        
        return params
    
    async def get_retry_strategy(self, source_id: str) -> RetryStrategy:
        """Get optimized retry strategy for a source."""
        if self.performance:
            return await self.performance.get_retry_strategy(source_id)
        return RetryStrategy()  # Default
    
    # ==========================================================================
    # Learning Cycle
    # ==========================================================================
    
    async def run_learning_cycle(self, force: bool = False) -> Dict[str, Any]:
        """
        Run a full learning cycle.
        
        This analyzes collected data and updates parameters/thresholds.
        Should be called periodically (e.g., every few hours).
        """
        async with self._learning_lock:
            now = datetime.now()
            
            # Check if it's time for a learning cycle
            if not force and self._last_learning_cycle:
                if now - self._last_learning_cycle < self._learning_interval:
                    return {
                        "status": "skipped",
                        "reason": "Not enough time since last cycle",
                        "next_cycle": (
                            self._last_learning_cycle + self._learning_interval
                        ).isoformat()
                    }
            
            logger.info("Starting learning cycle...")
            
            results = {
                "status": "completed",
                "started_at": now.isoformat(),
                "components": {},
                "recommendations_applied": 0,
                "parameters_adjusted": 0
            }
            
            try:
                # 1. Analyze performance patterns
                if self.performance:
                    perf_recs = await self.performance.analyze_and_optimize()
                    results["components"]["performance"] = {
                        "recommendations": len(perf_recs),
                        "summary": await self.performance.get_performance_summary()
                    }
                    
                    # Apply in active mode
                    if self.config.mode == LearningMode.ACTIVE:
                        for rec in perf_recs:
                            if rec.confidence > 0.7:
                                await self.performance.apply_recommendation(rec, dry_run=False)
                                results["recommendations_applied"] += 1
                
                # 2. Run auto-tuning
                if self.auto_tuner:
                    tuning_result = await self.auto_tuner.apply_learning()
                    results["components"]["auto_tuner"] = {
                        "parameters_adjusted": tuning_result.parameters_adjusted,
                        "sources_analyzed": tuning_result.sources_analyzed
                    }
                    results["parameters_adjusted"] = tuning_result.parameters_adjusted
                
                # 3. Generate quality report
                if self.quality:
                    quality_report = await self.quality.generate_quality_report()
                    results["components"]["quality"] = {
                        "score": quality_report.overall_quality_score,
                        "trend": quality_report.trend,
                        "issues_found": quality_report.total_issues_found,
                        "recommendations": quality_report.recommendations[:5]
                    }
                    
                    # Check for quality alerts
                    if quality_report.overall_quality_score < self.config.quality_alert_threshold:
                        logger.warning(
                            f"Quality alert: Score {quality_report.overall_quality_score:.2f} "
                            f"below threshold {self.config.quality_alert_threshold}"
                        )
                
                # 4. Persist learning
                await self._persist_learning_state()
                
                self._last_learning_cycle = now
                results["completed_at"] = datetime.now().isoformat()
                
                logger.info(
                    f"Learning cycle completed: "
                    f"{results['recommendations_applied']} recommendations applied, "
                    f"{results['parameters_adjusted']} parameters adjusted"
                )
                
            except Exception as e:
                logger.error(f"Error in learning cycle: {e}")
                results["status"] = "error"
                results["error"] = str(e)
            
            return results
    
    # ==========================================================================
    # Health & Monitoring
    # ==========================================================================
    
    async def get_system_health(self) -> SystemHealth:
        """Get overall health status of the learning system."""
        component_status = {}
        
        # Check each component
        if self.metrics:
            component_status["metrics"] = (
                "healthy" if self._component_errors.get("metrics", 0) < 5 
                else "degraded"
            )
        
        if self.feedback:
            component_status["feedback"] = (
                "healthy" if self._component_errors.get("feedback", 0) < 5 
                else "degraded"
            )
        
        if self.auto_tuner:
            component_status["auto_tuner"] = (
                "healthy" if self._component_errors.get("auto_tuner", 0) < 5 
                else "degraded"
            )
        
        if self.performance:
            component_status["performance"] = (
                "healthy" if self._component_errors.get("performance", 0) < 5 
                else "degraded"
            )
        
        if self.quality:
            component_status["quality"] = (
                "healthy" if self._component_errors.get("quality", 0) < 5 
                else "degraded"
            )
        
        # Get quality metrics
        quality_score = 1.0
        quality_trend = "stable"
        active_issues = 0
        
        if self.quality:
            try:
                report = await self.quality.generate_quality_report(period_days=1)
                quality_score = report.overall_quality_score
                quality_trend = report.trend
                active_issues = report.total_issues_found
            except Exception:
                pass
        
        # Get pending recommendations
        pending_recs = 0
        if self.performance:
            try:
                summary = await self.performance.get_performance_summary()
                pending_recs = summary.get("pending_recommendations", 0)
            except Exception:
                pass
        
        # Determine overall status
        degraded_count = sum(1 for s in component_status.values() if s == "degraded")
        if degraded_count == 0:
            status = "healthy"
            message = "All learning components operating normally"
        elif degraded_count < len(component_status) // 2:
            status = "degraded"
            message = f"{degraded_count} components experiencing issues"
        else:
            status = "unhealthy"
            message = "Majority of components degraded"
        
        return SystemHealth(
            status=status,
            quality_score=quality_score,
            quality_trend=quality_trend,
            active_issues=active_issues,
            pending_recommendations=pending_recs,
            last_learning_cycle=self._last_learning_cycle,
            components_status=component_status,
            message=message
        )
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for monitoring."""
        health = await self.get_system_health()
        
        dashboard = {
            "health": {
                "status": health.status,
                "quality_score": health.quality_score,
                "quality_trend": health.quality_trend,
                "message": health.message
            },
            "components": health.components_status,
            "metrics": {},
            "quality": {},
            "performance": {},
            "recent_activity": []
        }
        
        # Add performance summary
        if self.performance:
            try:
                dashboard["performance"] = await self.performance.get_performance_summary()
            except Exception:
                pass
        
        # Add quality summary
        if self.quality:
            try:
                report = await self.quality.generate_quality_report(period_days=7)
                dashboard["quality"] = {
                    "score": report.overall_quality_score,
                    "trend": report.trend,
                    "issues": report.total_issues_found,
                    "by_severity": report.issues_by_severity,
                    "recommendations": report.recommendations[:5]
                }
            except Exception:
                pass
        
        return dashboard
    
    # ==========================================================================
    # Private Helpers
    # ==========================================================================
    
    def _generate_action_items(
        self,
        recommendations: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action items from recommendations."""
        actions = []
        
        # Performance actions
        perf = recommendations.get("performance", {})
        timing = perf.get("optimal_timing", {})
        
        if timing.get("worst_hours"):
            actions.append({
                "priority": "medium",
                "category": "performance",
                "action": f"Avoid scraping during hours: {timing['worst_hours'][:3]}",
                "reason": "Higher failure rates during these hours"
            })
        
        # Quality actions
        quality = recommendations.get("quality", {})
        if quality.get("quality_score", 1.0) < 0.7:
            actions.append({
                "priority": "high",
                "category": "quality",
                "action": "Review source quality - score below threshold",
                "reason": f"Quality score: {quality.get('quality_score', 0):.1%}"
            })
        
        for rec in quality.get("recommendations", [])[:3]:
            actions.append({
                "priority": "medium",
                "category": "quality",
                "action": rec,
                "reason": "Identified quality pattern"
            })
        
        return sorted(actions, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])
    
    def _record_component_error(self, component: str, error: Exception) -> None:
        """Record a component error for health tracking."""
        self._component_errors[component] = self._component_errors.get(component, 0) + 1
        logger.debug(f"Component {component} error count: {self._component_errors[component]}")
    
    def _clear_component_error(self, component: str) -> None:
        """Clear component error count on success."""
        if component in self._component_errors:
            self._component_errors[component] = max(0, self._component_errors[component] - 1)
    
    async def _persist_learning_state(self) -> None:
        """Persist learning state to database."""
        try:
            if self.quality:
                await self.quality.persist_analysis()
            
            if self.auto_tuner:
                await self.auto_tuner.save_state()
                
        except Exception as e:
            logger.error(f"Error persisting learning state: {e}")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the learning system."""
        logger.info("Shutting down AdaptiveLearningSystem...")
        
        try:
            await self._persist_learning_state()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        logger.info("AdaptiveLearningSystem shutdown complete")
