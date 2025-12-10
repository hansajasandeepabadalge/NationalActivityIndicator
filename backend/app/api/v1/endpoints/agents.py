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


# ============================================
# Business Impact Scorer Endpoints
# ============================================

class ImpactScoreRequest(BaseModel):
    """Request model for business impact scoring."""
    title: str
    body: str
    source: Optional[str] = "unknown"
    publish_time: Optional[str] = None
    target_sectors: Optional[list] = None


class BatchScoreRequest(BaseModel):
    """Request model for batch scoring."""
    articles: list  # List of ImpactScoreRequest-like dicts


@router.post("/impact/score")
async def score_article_impact(request: ImpactScoreRequest):
    """
    Calculate business impact score for an article.
    
    Uses multi-factor analysis for prioritization:
    - Severity (25%): Event magnitude (crisis → minor)
    - Sector Relevance (25%): Match to target industries
    - Source Credibility (15%): Government → Unverified scale
    - Geographic Scope (10%): National → Local coverage
    - Temporal Urgency (15%): Breaking → Historical timeline
    - Volume/Momentum (10%): Mention frequency and trends
    
    Returns:
        - impact_score: 0-100 weighted score
        - priority_rank: 1-5 (1 = critical, 5 = minimal)
        - factor_breakdown: Individual factor scores
        - sector_analysis: Primary/secondary sectors affected
        - processing_guidance: Fast-track and notification recommendations
    """
    try:
        from app.impact_scorer import get_impact_scorer
        
        scorer = await get_impact_scorer()
        
        article = {
            "title": request.title,
            "content": request.body,
            "source": request.source,
            "publish_time": request.publish_time
        }
        
        result = await scorer.score_article(article, request.target_sectors)
        
        return {
            "success": True,
            "impact_score": result.impact_score,
            "impact_level": result.impact_level.value,
            "priority_rank": result.priority_rank,
            "requires_fast_track": result.requires_fast_track,
            "requires_notification": result.requires_notification,
            "factors": result.factors.to_dict(),
            "factor_contributions": result.factor_contributions,
            "primary_sectors": result.primary_sectors,
            "secondary_sectors": result.secondary_sectors,
            "cascade_effects": result.cascade_effects,
            "confidence": result.confidence,
            "detected_signals": result.detected_signals,
            "processing_guidance": result.processing_guidance
        }
        
    except Exception as e:
        logger.error(f"Error scoring impact: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to score article impact: {str(e)}"
        )


@router.post("/impact/batch")
async def score_batch_impact(request: BatchScoreRequest):
    """
    Score multiple articles and return sorted by priority.
    
    Efficiently processes a batch of articles and returns them
    sorted by priority (highest priority first).
    
    Useful for:
    - Processing a feed of new articles
    - Re-prioritizing a queue
    - Comparing article importance
    
    Returns:
        List of scored articles sorted by priority_rank, then impact_score
    """
    try:
        from app.impact_scorer import get_impact_scorer
        
        scorer = await get_impact_scorer()
        
        articles = [
            {
                "title": a.get("title", ""),
                "content": a.get("body", a.get("content", "")),
                "source": a.get("source", "unknown"),
                "publish_time": a.get("publish_time")
            }
            for a in request.articles
        ]
        
        results = await scorer.score_batch(articles)
        
        return {
            "success": True,
            "total_scored": len(results),
            "critical_count": sum(1 for r in results if r.priority_rank == 1),
            "high_count": sum(1 for r in results if r.priority_rank == 2),
            "results": [
                {
                    "title": articles[i].get("title", "")[:100],
                    "impact_score": r.impact_score,
                    "impact_level": r.impact_level.value,
                    "priority_rank": r.priority_rank,
                    "primary_sectors": [s.get("sector") for s in r.primary_sectors[:2]]
                }
                for i, r in enumerate(results)
            ]
        }
        
    except Exception as e:
        logger.error(f"Error batch scoring: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to batch score articles: {str(e)}"
        )


@router.get("/impact/sectors/{sector}")
async def get_sector_details(sector: str):
    """
    Get information about a specific industry sector.
    
    Returns keywords, dependencies, and impact multipliers
    for the specified sector.
    
    Args:
        sector: Sector name (e.g., 'tourism', 'finance', 'manufacturing')
    """
    try:
        from app.impact_scorer.sector_engine import SectorImpactEngine, IndustrySector
        
        engine = SectorImpactEngine()
        
        # Validate sector
        try:
            sector_enum = IndustrySector(sector.lower())
        except ValueError:
            available = [s.value for s in IndustrySector]
            raise HTTPException(
                status_code=400,
                detail=f"Unknown sector '{sector}'. Available sectors: {available}"
            )
        
        # Get sector keywords
        keywords = list(engine.SECTOR_KEYWORDS.get(sector_enum, set()))
        
        # Get dependencies
        dependencies = []
        if sector_enum in engine.SECTOR_DEPENDENCIES:
            dependencies = [
                {"sector": dep.value, "strength": strength}
                for dep, strength in engine.SECTOR_DEPENDENCIES[sector_enum]
            ]
        
        # Get sectors that depend on this one
        dependent_on_this = []
        for source_sector, deps in engine.SECTOR_DEPENDENCIES.items():
            for dep, strength in deps:
                if dep == sector_enum:
                    dependent_on_this.append({
                        "sector": source_sector.value,
                        "strength": strength
                    })
        
        return {
            "sector": sector_enum.value,
            "keywords": keywords[:20],
            "keyword_count": len(keywords),
            "impacts_sectors": dependencies,
            "impacted_by_sectors": dependent_on_this
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sector details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sector details: {str(e)}"
        )


@router.get("/impact/stats")
async def get_impact_scorer_statistics():
    """
    Get business impact scorer statistics.
    
    Returns:
        - articles_scored: Total articles processed
        - avg_score: Average impact score
        - critical_count: Articles with critical priority
        - high_count: Articles with high priority
        - avg_processing_time_ms: Average scoring time
        - scoring_profile: Current weight profile
    """
    try:
        from app.impact_scorer import get_impact_scorer
        
        scorer = await get_impact_scorer()
        stats = scorer.get_stats()
        
        return {
            "success": True,
            **stats
        }
        
    except Exception as e:
        logger.error(f"Error getting impact stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get impact scorer stats: {str(e)}"
        )


@router.put("/impact/profile/{profile}")
async def set_scoring_profile(profile: str):
    """
    Change the scoring weight profile.
    
    Available profiles:
    - balanced: Equal emphasis on all factors (default)
    - urgency: Prioritize time-sensitive events (30% severity, 30% temporal)
    - business: Prioritize sector relevance (35% sector)
    - credibility: Prioritize source reliability (30% credibility)
    
    Args:
        profile: Profile name to activate
    """
    try:
        from app.impact_scorer import get_impact_scorer
        from app.impact_scorer.score_aggregator import ScoringProfile
        
        # Validate profile
        try:
            profile_enum = ScoringProfile(profile.lower())
        except ValueError:
            available = [p.value for p in ScoringProfile]
            raise HTTPException(
                status_code=400,
                detail=f"Unknown profile '{profile}'. Available profiles: {available}"
            )
        
        scorer = await get_impact_scorer()
        scorer.set_scoring_profile(profile_enum)
        
        return {
            "success": True,
            "message": f"Scoring profile changed to '{profile}'",
            "profile": profile_enum.value,
            "description": {
                "balanced": "Equal emphasis on all factors",
                "urgency": "Prioritize time-sensitive events",
                "business": "Prioritize sector relevance",
                "credibility": "Prioritize source reliability"
            }.get(profile_enum.value, "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set scoring profile: {str(e)}"
        )


@router.post("/impact/compare-profiles")
async def compare_scoring_profiles(request: ImpactScoreRequest):
    """
    Compare impact scores across all scoring profiles.
    
    Useful for understanding how different weight configurations
    would affect article prioritization.
    
    Returns scores for each profile with a recommendation.
    """
    try:
        from app.impact_scorer.multi_factor_analyzer import MultiFactorAnalyzer
        from app.impact_scorer.sector_engine import SectorImpactEngine
        from app.impact_scorer.score_aggregator import ScoreAggregator, ScoringProfile
        
        analyzer = MultiFactorAnalyzer()
        sector_engine = SectorImpactEngine()
        
        factor_scores = analyzer.analyze(
            title=request.title,
            content=request.body,
            source=request.source or "unknown"
        )
        
        sector_result = sector_engine.analyze_sectors(
            title=request.title,
            content=request.body
        )
        
        # Compare across profiles
        profile_results = {}
        for profile in ScoringProfile:
            aggregator = ScoreAggregator(profile=profile)
            result = aggregator.aggregate(factor_scores, sector_result)
            profile_results[profile.value] = {
                "final_score": result.final_score,
                "priority_rank": result.priority_rank,
                "priority_label": result.priority_label,
                "weights": result.weights_used
            }
        
        # Determine best profile
        scores = [(k, v["final_score"]) for k, v in profile_results.items()]
        max_profile = max(scores, key=lambda x: x[1])[0]
        min_profile = min(scores, key=lambda x: x[1])[0]
        variance = max(s[1] for s in scores) - min(s[1] for s in scores)
        
        return {
            "success": True,
            "factor_scores": factor_scores.to_dict(),
            "sector_score": sector_result.overall_sector_score,
            "profile_comparison": profile_results,
            "analysis": {
                "highest_score_profile": max_profile,
                "lowest_score_profile": min_profile,
                "score_variance": round(variance, 1),
                "recommendation": (
                    "balanced" if variance < 10 
                    else f"{max_profile} for maximum impact visibility"
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing profiles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare profiles: {str(e)}"
        )


# ============================================
# Cross-Source Validation Endpoints
# ============================================

class ValidationRequest(BaseModel):
    """Request model for article validation."""
    article_id: str
    title: str
    body: str
    source: Optional[str] = None
    publish_time: Optional[str] = None


class BatchValidationRequest(BaseModel):
    """Request model for batch validation."""
    articles: list  # List of ValidationRequest-like dicts


@router.post("/validation/validate")
async def validate_article_trust(request: ValidationRequest):
    """
    Validate article credibility through cross-source validation.
    
    Calculates trust score based on:
    - Source reputation (30%)
    - Corroboration from other sources (35%)
    - Source diversity (20%)
    - Recency match (15%)
    
    Returns trust level: VERIFIED, HIGH_TRUST, MODERATE, LOW_TRUST, UNVERIFIED
    """
    try:
        from app.cross_validation import get_validator
        from datetime import datetime
        
        # Parse publish time
        published_at = None
        if request.publish_time:
            try:
                published_at = datetime.fromisoformat(
                    request.publish_time.replace('Z', '+00:00')
                )
            except:
                published_at = datetime.utcnow()
        
        validator = get_validator()
        result = validator.validate_article(
            article_id=request.article_id,
            content=request.body,
            title=request.title,
            source_name=request.source or "unknown",
            published_at=published_at
        )
        
        return {
            "success": True,
            "article_id": result.article_id,
            "trust_score": round(result.score, 1),
            "trust_level": result.trust_level.value,
            "source": result.source_name,
            "corroboration": {
                "count": len(result.corroboration.corroborating_articles) if result.corroboration else 0,
                "sources": [
                    a.source_name for a in result.corroboration.corroborating_articles
                ][:5] if result.corroboration else [],
                "has_conflicts": result.trust_score.has_conflicts,
                "conflict_count": len(result.corroboration.conflicting_articles) if result.corroboration else 0
            },
            "claims_extracted": len(result.claims),
            "source_reputation": {
                "score": round(result.source_reputation.current_reputation, 1) if result.source_reputation else 0,
                "tier": result.source_reputation.tier.value if result.source_reputation else "unknown"
            },
            "factor_breakdown": {
                "source_reputation": {
                    "score": round(result.trust_score.source_reputation_score.score, 1),
                    "weight": result.trust_score.source_reputation_score.weight
                },
                "corroboration": {
                    "score": round(result.trust_score.corroboration_score.score, 1),
                    "weight": result.trust_score.corroboration_score.weight
                },
                "source_diversity": {
                    "score": round(result.trust_score.source_diversity_score.score, 1),
                    "weight": result.trust_score.source_diversity_score.weight
                },
                "recency": {
                    "score": round(result.trust_score.recency_score.score, 1),
                    "weight": result.trust_score.recency_score.weight
                }
            },
            "processing_time_ms": round(result.processing_time_ms, 2)
        }
        
    except Exception as e:
        logger.error(f"Error validating article: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/validation/batch")
async def batch_validate_trust(request: BatchValidationRequest):
    """
    Validate trust for multiple articles at once.
    
    More efficient than individual calls as articles can be
    cross-referenced against each other.
    """
    try:
        from app.cross_validation import get_validator
        
        validator = get_validator()
        results = validator.validate_batch(request.articles)
        
        return {
            "success": True,
            "articles_validated": len(results),
            "results": [
                {
                    "article_id": r.article_id,
                    "trust_score": round(r.score, 1),
                    "trust_level": r.trust_level.value,
                    "source": r.source_name,
                    "corroboration_count": len(r.corroboration.corroborating_articles) if r.corroboration else 0,
                    "has_conflicts": r.trust_score.has_conflicts,
                    "claims_count": len(r.claims)
                }
                for r in results
            ],
            "summary": validator.get_trust_summary(results)
        }
        
    except Exception as e:
        logger.error(f"Error in batch validation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch validation failed: {str(e)}"
        )


@router.get("/validation/source/{source_name}")
async def get_source_reputation(source_name: str):
    """
    Get reputation information for a specific source.
    
    Returns dynamic reputation based on historical accuracy,
    tier classification, and tracking metrics.
    """
    try:
        from app.cross_validation import get_validator
        
        validator = get_validator()
        reputation = validator.get_source_reputation(source_name)
        
        return {
            "success": True,
            "source": reputation.source_name,
            "source_id": reputation.source_id,
            "reputation_score": round(reputation.current_reputation, 1),
            "base_reputation": reputation.base_reputation,
            "tier": reputation.tier.value,
            "category": reputation.category.value,
            "metrics": {
                "total_articles": reputation.total_articles,
                "confirmed_reports": reputation.confirmed_reports,
                "contradicted_reports": reputation.contradicted_reports,
                "corrections_issued": reputation.corrections_issued,
                "first_to_report": reputation.first_to_report
            },
            "accuracy_rate": round(reputation.accuracy_rate, 3),
            "correction_rate": round(reputation.correction_rate, 3)
        }
        
    except Exception as e:
        logger.error(f"Error getting source reputation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get source reputation: {str(e)}"
        )


@router.post("/validation/extract-claims")
async def extract_claims(request: ValidationRequest):
    """
    Extract verifiable claims from an article.
    
    Identifies numeric claims, statements/quotes, and events
    that can be cross-referenced with other sources.
    """
    try:
        from app.cross_validation import ClaimExtractor
        
        extractor = ClaimExtractor()
        claims = extractor.extract_claims(
            content=request.body,
            title=request.title,
            article_id=request.article_id,
            source_name=request.source or ""
        )
        
        return {
            "success": True,
            "article_id": request.article_id,
            "total_claims": len(claims),
            "claims_by_type": {
                "numeric": sum(1 for c in claims if c.claim_type.value == "numeric"),
                "attribution": sum(1 for c in claims if c.claim_type.value == "attribution"),
                "event": sum(1 for c in claims if c.claim_type.value == "event")
            },
            "claims": [
                {
                    "claim_id": claim.claim_id,
                    "type": claim.claim_type.value,
                    "text": claim.text[:300],
                    "normalized": claim.normalized[:200],
                    "subject": claim.subject,
                    "predicate": claim.predicate,
                    "object": claim.object[:100] if claim.object else None,
                    "numeric": {
                        "value": claim.numeric_value,
                        "unit": claim.numeric_unit,
                        "context": claim.numeric_context
                    } if claim.claim_type.value == "numeric" else None,
                    "entities": [e.to_dict() for e in claim.entities[:5]],
                    "confidence": round(claim.confidence, 2)
                }
                for claim in claims[:20]  # Limit to 20 claims
            ]
        }
        
    except Exception as e:
        logger.error(f"Error extracting claims: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Claim extraction failed: {str(e)}"
        )


@router.get("/validation/stats")
async def get_validation_stats():
    """
    Get cross-source validation system statistics.
    
    Includes validation metrics, source reputation stats,
    and corroboration engine stats.
    """
    try:
        from app.cross_validation import get_validator
        
        validator = get_validator()
        stats = validator.get_statistics()
        metrics = validator.get_metrics()
        
        return {
            "success": True,
            "validation_metrics": metrics.to_dict(),
            "reputation_stats": stats.get("reputation_stats", {}),
            "corroboration_stats": stats.get("corroboration_stats", {}),
            "cache_size": stats.get("cache_size", 0),
            "top_sources": stats.get("top_sources", [])
        }
        
    except Exception as e:
        logger.error(f"Error getting validation stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get validation stats: {str(e)}"
        )


@router.get("/validation/sources/top")
async def get_top_sources(limit: int = 10):
    """
    Get top sources by reputation score.
    
    Returns the most reputable sources tracked by the system.
    """
    try:
        from app.cross_validation import get_validator
        
        validator = get_validator()
        top_sources = validator._reputation_tracker.get_top_sources(limit)
        
        return {
            "success": True,
            "count": len(top_sources),
            "sources": [
                {
                    "source": s.source_name,
                    "reputation_score": round(s.current_reputation, 1),
                    "tier": s.tier.value,
                    "category": s.category.value,
                    "total_articles": s.total_articles,
                    "accuracy_rate": round(s.accuracy_rate, 3)
                }
                for s in top_sources
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting top sources: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get top sources: {str(e)}"
        )
