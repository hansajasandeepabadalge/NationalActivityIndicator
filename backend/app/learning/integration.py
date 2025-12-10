"""
Learning Integration Module for MasterOrchestrator

This module provides seamless integration between the Adaptive Learning System
and the MasterOrchestrator without modifying the orchestrator's core logic.

Usage:
    from app.learning.integration import LearningOrchestrator
    
    # Wrap existing orchestrator
    learning_orchestrator = LearningOrchestrator(master_orchestrator)
    
    # Run with learning enabled
    result = await learning_orchestrator.run_cycle_with_learning()
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from functools import wraps

from app.learning.adaptive_system import (
    AdaptiveLearningSystem,
    LearningSystemConfig,
    LearningMode
)
from app.learning.performance_optimizer import RetryStrategy

logger = logging.getLogger(__name__)


class LearningHooks:
    """
    Provides hook methods that can be called at various pipeline stages.
    
    These hooks integrate learning without modifying existing code.
    """
    
    def __init__(self, learning_system: AdaptiveLearningSystem):
        self.learning = learning_system
        self._cycle_start: Optional[datetime] = None
        self._cycle_metrics: Dict[str, Any] = {}
    
    async def on_cycle_start(self, run_id: str) -> None:
        """Called when a new pipeline cycle starts."""
        self._cycle_start = datetime.now()
        self._cycle_metrics = {
            "run_id": run_id,
            "sources_scraped": 0,
            "articles_processed": 0,
            "articles_validated": 0,
            "articles_stored": 0,
            "errors": []
        }
        logger.debug(f"Learning: Cycle {run_id} started")
    
    async def on_cycle_end(
        self,
        run_id: str,
        final_state: Dict[str, Any]
    ) -> None:
        """Called when a pipeline cycle completes."""
        if self._cycle_start:
            duration_ms = (datetime.now() - self._cycle_start).total_seconds() * 1000
            self._cycle_metrics["duration_ms"] = duration_ms
        
        # Record overall metrics
        metrics = final_state.get("metrics", {})
        self._cycle_metrics.update({
            "sources_scraped": metrics.get("sources_to_scrape", 0),
            "articles_scraped": metrics.get("articles_scraped", 0),
            "articles_processed": metrics.get("articles_processed", 0),
            "articles_validated": metrics.get("articles_validated", 0),
            "articles_stored": metrics.get("articles_stored", 0),
            "articles_rejected": metrics.get("articles_rejected", 0),
            "articles_filtered": metrics.get("articles_filtered", 0),
        })
        
        logger.info(
            f"Learning: Cycle {run_id} completed - "
            f"scraped={self._cycle_metrics['articles_scraped']}, "
            f"stored={self._cycle_metrics['articles_stored']}"
        )
    
    async def on_scrape_complete(
        self,
        source_id: str,
        scraper_type: str,
        success: bool,
        articles_count: int,
        latency_ms: float,
        error_type: Optional[str] = None
    ) -> None:
        """Called after each scraping operation."""
        await self.learning.record_scrape_result(
            source_id=source_id,
            scraper_type=scraper_type,
            success=success,
            articles_count=articles_count,
            latency_ms=latency_ms,
            error_type=error_type
        )
        
        if success:
            self._cycle_metrics["sources_scraped"] = (
                self._cycle_metrics.get("sources_scraped", 0) + 1
            )
    
    async def on_validation_complete(
        self,
        article_id: str,
        source_id: str,
        valid: bool,
        issues: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Called after article validation."""
        await self.learning.record_validation_result(
            article_id=article_id,
            source_id=source_id,
            valid=valid,
            issues=issues
        )
    
    async def on_article_stored(
        self,
        article_id: str,
        source_id: str,
        quality_score: float
    ) -> None:
        """Called after an article is successfully stored."""
        await self.learning.record_article_outcome(
            article_id=article_id,
            source_id=source_id,
            used_by_downstream=True,
            quality_rating=quality_score / 100.0  # Normalize to 0-1
        )
    
    async def on_article_rejected(
        self,
        article_id: str,
        source_id: str,
        reason: str
    ) -> None:
        """Called when an article is rejected."""
        await self.learning.record_article_outcome(
            article_id=article_id,
            source_id=source_id,
            used_by_downstream=False,
            feedback_type="article_discarded"
        )
    
    async def get_optimal_params(self, source_id: str) -> Dict[str, Any]:
        """Get optimized parameters for a source."""
        return await self.learning.get_optimal_parameters(source_id)
    
    async def get_retry_strategy(self, source_id: str) -> RetryStrategy:
        """Get optimized retry strategy for a source."""
        return await self.learning.get_retry_strategy(source_id)


class LearningOrchestrator:
    """
    Wrapper that adds learning capabilities to MasterOrchestrator.
    
    This is a decorator pattern that enhances the orchestrator
    without modifying its internal code.
    """
    
    def __init__(
        self,
        orchestrator,
        config: Optional[LearningSystemConfig] = None,
        db_pool=None
    ):
        """
        Initialize learning wrapper.
        
        Args:
            orchestrator: MasterOrchestrator instance
            config: Learning system configuration
            db_pool: Database connection pool
        """
        self.orchestrator = orchestrator
        self.config = config or LearningSystemConfig(mode=LearningMode.ADVISORY)
        
        # Initialize learning system
        self.learning = AdaptiveLearningSystem(
            db_pool=db_pool,
            config=self.config
        )
        
        # Create hooks
        self.hooks = LearningHooks(self.learning)
        
        # Track state
        self._initialized = False
        
        logger.info(
            f"LearningOrchestrator initialized in {self.config.mode.value} mode"
        )
    
    async def initialize(self) -> None:
        """Initialize the learning system."""
        if not self._initialized:
            await self.learning.initialize()
            self._initialized = True
    
    async def run_cycle_with_learning(self) -> Dict[str, Any]:
        """
        Run a complete cycle with learning enabled.
        
        Wraps the orchestrator's run_cycle with learning hooks.
        """
        await self.initialize()
        
        # Generate run ID if orchestrator doesn't
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Pre-cycle: Notify learning system
        await self.hooks.on_cycle_start(run_id)
        
        try:
            # Execute the original cycle
            result = await self.orchestrator.run_cycle()
            
            # Post-cycle: Process learning
            await self._process_cycle_results(run_id, result)
            
            # Add learning metrics to result
            result["learning"] = {
                "mode": self.config.mode.value,
                "cycle_metrics": self.hooks._cycle_metrics
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in learning cycle: {e}")
            raise
        finally:
            # Ensure cycle end is always recorded
            await self.hooks.on_cycle_end(run_id, result if 'result' in dir() else {})
    
    async def _process_cycle_results(
        self,
        run_id: str,
        result: Dict[str, Any]
    ) -> None:
        """Process cycle results for learning."""
        # Extract and record scraping results
        metrics = result.get("metrics", {})
        
        # Record errors for learning
        for error in result.get("errors", []):
            phase = error.get("phase", "unknown")
            source = error.get("source", "unknown")
            
            if phase == "scrape_content":
                await self.hooks.on_scrape_complete(
                    source_id=source,
                    scraper_type="unknown",
                    success=False,
                    articles_count=0,
                    latency_ms=0,
                    error_type=error.get("error", "unknown")[:50]
                )
    
    async def get_recommendations(
        self,
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get learning recommendations."""
        await self.initialize()
        
        if source_id:
            return await self.learning.get_source_recommendations(source_id)
        
        # Return general health and recommendations
        health = await self.learning.get_system_health()
        dashboard = await self.learning.get_dashboard_data()
        
        return {
            "health": {
                "status": health.status,
                "quality_score": health.quality_score,
                "message": health.message
            },
            "dashboard": dashboard
        }
    
    async def run_learning_cycle(self, force: bool = False) -> Dict[str, Any]:
        """Manually trigger a learning cycle."""
        await self.initialize()
        return await self.learning.run_learning_cycle(force=force)
    
    async def get_health(self):
        """Get learning system health."""
        await self.initialize()
        return await self.learning.get_system_health()
    
    async def shutdown(self) -> None:
        """Shutdown learning system gracefully."""
        await self.learning.shutdown()


def with_learning(func):
    """
    Decorator to add learning to any pipeline function.
    
    Usage:
        @with_learning
        async def scrape_source(source_id: str) -> Dict:
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        success = False
        error_type = None
        
        try:
            result = await func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            error_type = type(e).__name__
            raise
        finally:
            # Record metrics if learning system is available
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Try to extract source_id from args/kwargs
            source_id = kwargs.get("source_id") or (args[0] if args else "unknown")
            
            logger.debug(
                f"Learning decorator: {func.__name__} for {source_id} - "
                f"success={success}, latency={latency_ms:.0f}ms"
            )
    
    return wrapper


# =============================================================================
# Factory Functions
# =============================================================================

def create_learning_orchestrator(
    orchestrator=None,
    mode: str = "advisory",
    db_pool=None
) -> LearningOrchestrator:
    """
    Factory function to create a learning-enabled orchestrator.
    
    Args:
        orchestrator: Existing MasterOrchestrator (creates one if None)
        mode: Learning mode ("passive", "advisory", "active")
        db_pool: Database connection pool
        
    Returns:
        LearningOrchestrator instance
    """
    if orchestrator is None:
        from app.orchestrator import MasterOrchestrator
        orchestrator = MasterOrchestrator()
    
    mode_enum = {
        "passive": LearningMode.PASSIVE,
        "advisory": LearningMode.ADVISORY,
        "active": LearningMode.ACTIVE
    }.get(mode.lower(), LearningMode.ADVISORY)
    
    config = LearningSystemConfig(mode=mode_enum)
    
    return LearningOrchestrator(
        orchestrator=orchestrator,
        config=config,
        db_pool=db_pool
    )


async def get_learning_system(db_pool=None) -> AdaptiveLearningSystem:
    """
    Get a standalone learning system instance.
    
    Useful for background jobs or analysis tasks.
    """
    config = LearningSystemConfig(mode=LearningMode.ADVISORY)
    system = AdaptiveLearningSystem(db_pool=db_pool, config=config)
    await system.initialize()
    return system
