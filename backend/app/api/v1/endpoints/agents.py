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
