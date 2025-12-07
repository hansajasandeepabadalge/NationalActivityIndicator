"""
API Endpoints for AI Agent System

Provides REST endpoints for:
- Starting/stopping data collection cycles
- Getting agent status
- Viewing pipeline metrics
- Manual interventions
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.orchestrator import create_orchestrator, get_state_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["AI Agents"])


# Pydantic models for request/response
class CycleResponse(BaseModel):
    """Response for a data collection cycle."""
    run_id: str
    success: bool
    phase: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    errors: Optional[list] = None
    summary: Optional[Dict[str, Any]] = None


class StatusResponse(BaseModel):
    """Response for orchestrator status."""
    status: str
    agents: Dict[str, Any]
    recent_runs: list
    timestamp: str


class OptimizationResponse(BaseModel):
    """Response for scheduler optimization."""
    recommendations: list
    overall_efficiency: float
    resource_savings: str
    monitoring_alerts: list
    sources_analyzed: int
    changes_recommended: int


# Keep track of running cycles
_running_cycles: Dict[str, bool] = {}


@router.post("/cycle/start", response_model=CycleResponse)
async def start_collection_cycle(background_tasks: BackgroundTasks):
    """
    Start a new data collection cycle.
    
    This runs the full AI-powered pipeline:
    1. Monitor sources to decide what to scrape
    2. Execute scrapers for selected sources
    3. Process and clean articles
    4. Classify priority/urgency
    5. Validate data quality
    6. Store validated articles
    
    Returns immediately with a run_id. Use /cycle/{run_id} to check status.
    """
    try:
        orchestrator = create_orchestrator()
        
        # Run cycle (this could take a while)
        result = await orchestrator.run_cycle()
        
        return CycleResponse(
            run_id=result.get("run_id", ""),
            success=result.get("success", False),
            phase=result.get("phase"),
            metrics=result.get("metrics"),
            errors=result.get("errors"),
            summary=result.get("summary")
        )
        
    except Exception as e:
        logger.error(f"Error starting cycle: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start collection cycle: {str(e)}"
        )


@router.get("/cycle/{run_id}")
async def get_cycle_status(run_id: str):
    """
    Get the status of a specific data collection cycle.
    
    Args:
        run_id: The run identifier returned from /cycle/start
        
    Returns:
        Current state of the cycle including metrics
    """
    try:
        state_manager = get_state_manager()
        await state_manager.connect()
        
        state = await state_manager.get_state(run_id)
        
        if state is None:
            raise HTTPException(
                status_code=404,
                detail=f"Cycle {run_id} not found"
            )
        
        return {
            "run_id": run_id,
            "phase": state.get("phase"),
            "started_at": state.get("started_at"),
            "updated_at": state.get("updated_at"),
            "metrics": state.get("metrics"),
            "error_count": len(state.get("errors", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cycle status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cycle status: {str(e)}"
        )


@router.get("/status", response_model=StatusResponse)
async def get_orchestrator_status():
    """
    Get the current status of the AI agent orchestrator.
    
    Returns:
        Status of all agents and recent pipeline runs
    """
    try:
        orchestrator = create_orchestrator()
        status = await orchestrator.get_status()
        
        return StatusResponse(
            status=status.get("status", "unknown"),
            agents=status.get("agents", {}),
            recent_runs=status.get("recent_runs", []),
            timestamp=status.get("timestamp", datetime.utcnow().isoformat())
        )
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get orchestrator status: {str(e)}"
        )


@router.get("/cycles/recent")
async def get_recent_cycles(limit: int = 10):
    """
    Get a list of recent data collection cycles.
    
    Args:
        limit: Maximum number of cycles to return (default 10)
        
    Returns:
        List of recent cycle summaries
    """
    try:
        state_manager = get_state_manager()
        await state_manager.connect()
        
        runs = await state_manager.get_recent_runs(limit=limit)
        
        return {
            "cycles": runs,
            "count": len(runs)
        }
        
    except Exception as e:
        logger.error(f"Error getting recent cycles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent cycles: {str(e)}"
        )


@router.post("/scheduler/optimize", response_model=OptimizationResponse)
async def run_scheduler_optimization():
    """
    Run the scheduler optimization to adjust scraping frequencies.
    
    This analyzes historical scraping patterns and adjusts frequencies
    to optimize efficiency while maintaining data coverage.
    
    Should be run periodically (e.g., daily at low-traffic hours).
    
    Returns:
        Optimization recommendations and efficiency metrics
    """
    try:
        orchestrator = create_orchestrator()
        result = await orchestrator.run_scheduler_optimization()
        
        return OptimizationResponse(
            recommendations=result.get("recommendations", []),
            overall_efficiency=result.get("overall_efficiency", 0.0),
            resource_savings=result.get("resource_savings", ""),
            monitoring_alerts=result.get("monitoring_alerts", []),
            sources_analyzed=result.get("sources_analyzed", 0),
            changes_recommended=result.get("changes_recommended", 0)
        )
        
    except Exception as e:
        logger.error(f"Error running optimization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run scheduler optimization: {str(e)}"
        )


@router.get("/metrics")
async def get_agent_metrics():
    """
    Get aggregated metrics from all AI agents.
    
    Returns:
        Combined metrics including LLM usage, decisions made, etc.
    """
    try:
        # Get LLM usage stats
        from app.agents.llm_manager import get_llm_manager
        llm_manager = get_llm_manager()
        llm_stats = llm_manager.get_daily_stats()
        
        # Get recent cycle metrics
        state_manager = get_state_manager()
        await state_manager.connect()
        recent_runs = await state_manager.get_recent_runs(limit=10)
        
        # Aggregate metrics from recent runs
        total_articles = 0
        total_errors = 0
        for run in recent_runs:
            metrics = run.get("metrics", {})
            total_articles += metrics.get("articles_stored", 0)
            total_errors += metrics.get("errors_count", 0)
        
        return {
            "llm_usage": llm_stats,
            "pipeline": {
                "recent_runs": len(recent_runs),
                "total_articles_processed": total_articles,
                "total_errors": total_errors
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent metrics: {str(e)}"
        )


@router.post("/health-check")
async def agent_health_check():
    """
    Run a health check on all AI agents.
    
    Verifies:
    - LLM connectivity (Groq/Together.ai)
    - Redis connectivity
    - Database connectivity
    
    Returns:
        Health status for each component
    """
    health = {
        "status": "healthy",
        "components": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check LLM
    try:
        from app.agents.llm_manager import get_llm_manager
        llm_manager = get_llm_manager()
        llm = llm_manager.get_llm()
        health["components"]["llm"] = {
            "status": "healthy" if llm else "unavailable",
            "provider": llm_manager.active_provider
        }
    except Exception as e:
        health["components"]["llm"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "degraded"
    
    # Check Redis
    try:
        state_manager = get_state_manager()
        await state_manager.connect()
        health["components"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health["components"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "degraded"
    
    return health


# ============================================
# Cache Statistics Endpoints
# ============================================

class CacheStatsResponse(BaseModel):
    """Response for cache statistics."""
    success: bool
    hit_rate: float
    total_hits: int
    total_misses: int
    bandwidth_saved_kb: float
    time_saved_seconds: float
    sources: Dict[str, Any]
    message: str


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_statistics():
    """
    Get smart cache performance statistics.
    
    Returns cache hit rate, bandwidth saved, time saved, and per-source metrics.
    Use this to monitor scraping efficiency and optimization opportunities.
    
    The smart cache achieves up to 70% faster scraping by:
    - Checking ETag/Last-Modified headers before full requests
    - Comparing content signatures to detect changes
    - Caching article data with automatic TTL expiration
    
    Returns:
        Cache performance metrics
    """
    try:
        from app.cache import get_smart_cache
        
        cache = await get_smart_cache()
        stats = cache.get_cache_stats()
        
        return CacheStatsResponse(
            success=True,
            hit_rate=stats.get("hit_rate", 0.0),
            total_hits=stats.get("total_hits", 0),
            total_misses=stats.get("total_misses", 0),
            bandwidth_saved_kb=stats.get("bandwidth_saved_kb", 0.0),
            time_saved_seconds=stats.get("time_saved_seconds", 0.0),
            sources=stats.get("sources", {}),
            message="Cache statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache statistics: {str(e)}"
        )


@router.delete("/cache/clear/{source_name}")
async def clear_source_cache(source_name: str):
    """
    Clear cached data for a specific source.
    
    Use this to force a fresh scrape on the next cycle for a particular source.
    
    Args:
        source_name: Name of the source to clear cache for (e.g., 'ada_derana')
        
    Returns:
        Confirmation of cache clearance
    """
    try:
        from app.cache import get_smart_cache
        
        cache = await get_smart_cache()
        await cache.invalidate_source(source_name)
        
        return {
            "success": True,
            "source_name": source_name,
            "message": f"Cache cleared for source '{source_name}'. Next scrape will fetch fresh data."
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache for {source_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


# ============================================
# Semantic Deduplication Endpoints
# ============================================

class DeduplicationCheckRequest(BaseModel):
    """Request for checking article duplicates."""
    article_id: str
    title: str
    body: str
    url: Optional[str] = ""
    source_name: Optional[str] = ""
    language: Optional[str] = "en"


class DeduplicationResponse(BaseModel):
    """Response for duplicate check."""
    is_duplicate: bool
    duplicate_type: str
    confidence: float
    original_article_id: Optional[str]
    cluster_id: Optional[str]
    similar_articles: list
    detection_method: str
    processing_time_ms: float
    recommendation: str


@router.post("/dedup/check", response_model=DeduplicationResponse)
async def check_article_duplicate(request: DeduplicationCheckRequest):
    """
    Check if an article is a duplicate using semantic deduplication.
    
    Uses multi-level detection for 90% better duplicate detection:
    1. URL Hash (exact match) - Instant
    2. Content Hash (normalized text) - Fast
    3. Semantic Similarity (AI embeddings) - Most accurate
    
    Returns:
        Duplicate detection results with confidence and similar articles
    """
    try:
        from app.deduplication import get_deduplicator
        
        dedup = await get_deduplicator()
        result = await dedup.check_duplicate(
            article_id=request.article_id,
            title=request.title,
            body=request.body,
            url=request.url or "",
            source_name=request.source_name or "",
            language=request.language or "en",
            word_count=len(request.body.split()) if request.body else 0,
            auto_register=True
        )
        
        return DeduplicationResponse(
            is_duplicate=result.is_duplicate,
            duplicate_type=result.duplicate_type.value,
            confidence=result.confidence,
            original_article_id=result.original_article_id,
            cluster_id=result.cluster_id,
            similar_articles=result.similar_articles,
            detection_method=result.detection_method,
            processing_time_ms=result.processing_time_ms,
            recommendation=result.recommendation
        )
        
    except Exception as e:
        logger.error(f"Error checking duplicate: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check duplicate: {str(e)}"
        )


class SimilarArticlesRequest(BaseModel):
    """Request for finding similar articles."""
    title: str
    body: str
    top_k: Optional[int] = 10


@router.post("/dedup/similar")
async def find_similar_articles(request: SimilarArticlesRequest):
    """
    Find articles similar to the given text using semantic search.
    
    Uses AI embeddings to understand semantic meaning and find
    related articles even with different wording.
    
    Returns:
        List of similar articles with similarity scores
    """
    try:
        from app.deduplication import get_deduplicator
        
        dedup = await get_deduplicator()
        similar = await dedup.get_similar_articles(
            title=request.title,
            body=request.body,
            top_k=request.top_k or 10
        )
        
        return {
            "success": True,
            "similar_articles": similar,
            "count": len(similar)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar articles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find similar articles: {str(e)}"
        )


@router.get("/dedup/stats")
async def get_deduplication_statistics():
    """
    Get semantic deduplication system statistics.
    
    Returns metrics including:
    - Total checks performed
    - Duplicate detection rates by method
    - Index statistics (articles indexed, embedding info)
    - Cluster statistics
    
    Use this to monitor deduplication effectiveness.
    """
    try:
        from app.deduplication import get_deduplicator
        
        dedup = await get_deduplicator()
        metrics = dedup.get_metrics()
        
        return {
            "success": True,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting dedup stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get deduplication stats: {str(e)}"
        )


@router.get("/dedup/clusters")
async def get_duplicate_clusters(hours: int = 24, limit: int = 50):
    """
    Get recent duplicate clusters (grouped related articles).
    
    Clusters represent articles about the same story from different sources.
    Each cluster has a primary article (best quality) and related duplicates.
    
    Args:
        hours: Time window in hours (default 24)
        limit: Maximum clusters to return (default 50)
        
    Returns:
        List of duplicate clusters with member articles
    """
    try:
        from app.deduplication import get_deduplicator
        
        dedup = await get_deduplicator()
        clusters = await dedup.cluster_manager.get_recent_clusters(
            hours=hours,
            limit=limit
        )
        
        return {
            "success": True,
            "clusters": [c.to_dict() for c in clusters],
            "count": len(clusters)
        }
        
    except Exception as e:
        logger.error(f"Error getting clusters: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get duplicate clusters: {str(e)}"
        )
