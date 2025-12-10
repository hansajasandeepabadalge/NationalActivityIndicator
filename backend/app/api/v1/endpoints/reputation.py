"""
Source Reputation API Endpoints

REST API for managing source reputation, quality filtering,
and viewing reputation analytics.

Endpoints:
- GET /reputation/sources - List all sources with reputation
- GET /reputation/sources/{source_name} - Get source reputation
- POST /reputation/sources/{source_name}/override - Manually override source
- GET /reputation/summary - Get reputation system summary
- GET /reputation/analytics - Get filtering analytics
- GET /reputation/tiers - Get sources by tier
- POST /reputation/filter - Filter articles (batch)
- PUT /reputation/thresholds - Update thresholds
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.reputation_manager import (
    ReputationManager,
    ReputationConfig,
    ReputationTier,
    create_reputation_manager
)
from app.services.quality_filter import (
    QualityFilter,
    FilterConfig,
    create_quality_filter
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reputation", tags=["Source Reputation"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SourceReputationResponse(BaseModel):
    """Response model for source reputation."""
    id: int
    source_name: str
    source_type: str
    reputation_score: float
    reputation_tier: str
    avg_quality_score: float
    acceptance_rate: float
    total_articles: int
    is_active: bool
    is_improving: bool
    last_evaluated_at: Optional[str]


class SourceOverrideRequest(BaseModel):
    """Request to override source status."""
    is_active: bool = Field(..., description="Enable or disable the source")
    reason: str = Field(..., min_length=5, description="Reason for override")
    override_by: str = Field(..., description="Admin username")
    duration_days: Optional[int] = Field(None, description="Override duration in days (None = permanent)")


class ReputationSummaryResponse(BaseModel):
    """Response model for reputation summary."""
    total_sources: int
    active_sources: int
    disabled_sources: int
    tier_distribution: Dict[str, int]
    average_reputation: float
    average_quality_score: float
    config: Dict[str, Any]


class FilterAnalyticsResponse(BaseModel):
    """Response model for filter analytics."""
    time_period_hours: int
    total_filtered: int
    action_breakdown: Dict[str, int]
    acceptance_rate: float
    rejection_rate: float
    avg_quality_score: float
    avg_reputation_score: float
    avg_latency_ms: float
    config: Dict[str, Any]


class BatchFilterRequest(BaseModel):
    """Request to filter multiple articles."""
    articles: List[Dict[str, Any]] = Field(..., description="List of articles with id and source_name")
    quality_scores: Optional[Dict[str, float]] = Field(None, description="Quality scores by article_id")


class BatchFilterResponse(BaseModel):
    """Response for batch filtering."""
    total: int
    accepted: int
    rejected: int
    flagged: int
    results: Dict[str, Dict[str, Any]]


class ThresholdUpdateRequest(BaseModel):
    """Request to update a threshold."""
    threshold_name: str = Field(..., description="Name of threshold to update")
    value: float = Field(..., description="New threshold value")
    updated_by: str = Field(default="admin", description="Who is updating")


# ============================================================================
# Dependency Injection
# ============================================================================

def get_reputation_manager(db: Session = Depends(get_db)) -> ReputationManager:
    """Get ReputationManager instance."""
    return create_reputation_manager(db)


def get_quality_filter(db: Session = Depends(get_db)) -> QualityFilter:
    """Get QualityFilter instance."""
    return create_quality_filter(db)


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/sources", response_model=List[SourceReputationResponse])
async def list_sources(
    tier: Optional[str] = Query(None, description="Filter by tier"),
    active_only: bool = Query(True, description="Only show active sources"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    manager: ReputationManager = Depends(get_reputation_manager)
):
    """
    List all sources with their reputation scores.
    
    Optionally filter by tier or active status.
    """
    from app.models.source_reputation_models import SourceReputation
    
    query = db.query(SourceReputation)
    
    if tier:
        query = query.filter(SourceReputation.reputation_tier == tier)
    
    if active_only:
        query = query.filter(SourceReputation.is_active == True)
    
    sources = query.order_by(
        SourceReputation.reputation_score.desc()
    ).offset(offset).limit(limit).all()
    
    return [
        SourceReputationResponse(
            id=s.id,
            source_name=s.source_name,
            source_type=s.source_type,
            reputation_score=round(s.reputation_score, 3),
            reputation_tier=s.reputation_tier,
            avg_quality_score=round(s.avg_quality_score, 1),
            acceptance_rate=round(s.acceptance_rate, 3),
            total_articles=s.total_articles,
            is_active=s.is_active,
            is_improving=s.is_improving,
            last_evaluated_at=s.last_evaluated_at.isoformat() if s.last_evaluated_at else None
        )
        for s in sources
    ]


@router.get("/sources/{source_name}", response_model=SourceReputationResponse)
async def get_source_reputation(
    source_name: str,
    manager: ReputationManager = Depends(get_reputation_manager)
):
    """Get reputation details for a specific source."""
    from app.models.source_reputation_models import SourceReputation
    
    source = await manager.get_or_create_source(source_name)
    
    return SourceReputationResponse(
        id=source.id,
        source_name=source.source_name,
        source_type=source.source_type,
        reputation_score=round(source.reputation_score, 3),
        reputation_tier=source.reputation_tier,
        avg_quality_score=round(source.avg_quality_score, 1),
        acceptance_rate=round(source.acceptance_rate, 3),
        total_articles=source.total_articles,
        is_active=source.is_active,
        is_improving=source.is_improving,
        last_evaluated_at=source.last_evaluated_at.isoformat() if source.last_evaluated_at else None
    )


@router.post("/sources/{source_name}/override")
async def override_source(
    source_name: str,
    request: SourceOverrideRequest,
    manager: ReputationManager = Depends(get_reputation_manager)
):
    """
    Manually override source status.
    
    Use this to enable/disable sources regardless of reputation score.
    """
    await manager.manually_override_source(
        source_name=source_name,
        is_active=request.is_active,
        reason=request.reason,
        override_by=request.override_by,
        duration_days=request.duration_days
    )
    
    action = "enabled" if request.is_active else "disabled"
    return {
        "message": f"Source '{source_name}' has been {action}",
        "source_name": source_name,
        "is_active": request.is_active,
        "reason": request.reason,
        "override_by": request.override_by,
        "duration_days": request.duration_days
    }


@router.get("/summary", response_model=ReputationSummaryResponse)
async def get_reputation_summary(
    manager: ReputationManager = Depends(get_reputation_manager)
):
    """Get overall reputation system summary."""
    summary = await manager.get_reputation_summary()
    return ReputationSummaryResponse(**summary)


@router.get("/analytics", response_model=FilterAnalyticsResponse)
async def get_filter_analytics(
    hours: int = Query(24, ge=1, le=720, description="Time period in hours"),
    quality_filter: QualityFilter = Depends(get_quality_filter)
):
    """Get filtering analytics for the specified time period."""
    analytics = await quality_filter.get_filter_analytics(hours=hours)
    return FilterAnalyticsResponse(**analytics)


@router.get("/tiers/{tier}")
async def get_sources_by_tier(
    tier: str,
    manager: ReputationManager = Depends(get_reputation_manager)
):
    """Get all sources in a specific tier."""
    try:
        tier_enum = ReputationTier(tier.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier: {tier}. Valid tiers: {[t.value for t in ReputationTier]}"
        )
    
    sources = await manager.get_sources_by_tier(tier_enum)
    return {
        "tier": tier,
        "count": len(sources),
        "sources": sources
    }


@router.post("/filter", response_model=BatchFilterResponse)
async def filter_articles_batch(
    request: BatchFilterRequest,
    quality_filter: QualityFilter = Depends(get_quality_filter)
):
    """
    Filter a batch of articles.
    
    Provide articles with 'id' and 'source_name' fields.
    Optionally provide quality_scores for post-filtering.
    """
    results = await quality_filter.filter_batch(
        articles=request.articles,
        quality_scores=request.quality_scores
    )
    
    # Count outcomes
    accepted = sum(1 for r in results.values() if r.action.value in ['accepted', 'boosted'])
    rejected = sum(1 for r in results.values() if r.action.value == 'rejected')
    flagged = sum(1 for r in results.values() if r.action.value == 'flagged')
    
    return BatchFilterResponse(
        total=len(results),
        accepted=accepted,
        rejected=rejected,
        flagged=flagged,
        results={k: v.to_dict() for k, v in results.items()}
    )


@router.put("/thresholds")
async def update_threshold(
    request: ThresholdUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update a reputation/quality threshold.
    
    Changes take effect immediately for new filtering decisions.
    """
    from app.models.source_reputation_models import ReputationThreshold
    
    threshold = db.query(ReputationThreshold).filter(
        ReputationThreshold.threshold_name == request.threshold_name
    ).first()
    
    if not threshold:
        raise HTTPException(
            status_code=404,
            detail=f"Threshold '{request.threshold_name}' not found"
        )
    
    old_value = threshold.value
    threshold.value = request.value
    threshold.updated_by = request.updated_by
    threshold.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Threshold '{request.threshold_name}' updated: {old_value} → {request.value}")
    
    return {
        "message": f"Threshold '{request.threshold_name}' updated",
        "threshold_name": request.threshold_name,
        "old_value": old_value,
        "new_value": request.value,
        "updated_by": request.updated_by
    }


@router.get("/thresholds")
async def list_thresholds(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """List all configurable thresholds."""
    from app.models.source_reputation_models import ReputationThreshold
    
    query = db.query(ReputationThreshold)
    
    if category:
        query = query.filter(ReputationThreshold.category == category)
    
    thresholds = query.filter(ReputationThreshold.is_active == True).all()
    
    return {
        "count": len(thresholds),
        "thresholds": [
            {
                "name": t.threshold_name,
                "description": t.description,
                "value": t.value,
                "type": t.threshold_type,
                "category": t.category,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                "updated_by": t.updated_by
            }
            for t in thresholds
        ]
    }


@router.post("/decay/apply")
async def apply_inactivity_decay(
    manager: ReputationManager = Depends(get_reputation_manager)
):
    """
    Apply inactivity decay to all inactive sources.
    
    This is typically run as a scheduled job, but can be triggered manually.
    """
    updates = await manager.apply_inactivity_decay()
    
    return {
        "message": f"Applied decay to {len(updates)} inactive sources",
        "updates": [u.to_dict() for u in updates]
    }


@router.get("/health")
async def reputation_system_health(
    manager: ReputationManager = Depends(get_reputation_manager),
    quality_filter: QualityFilter = Depends(get_quality_filter)
):
    """Check health of the reputation system."""
    summary = await manager.get_reputation_summary()
    stats = quality_filter.get_session_stats()
    
    return {
        "status": "healthy",
        "sources": {
            "total": summary["total_sources"],
            "active": summary["active_sources"]
        },
        "session_stats": stats.to_dict(),
        "filter_config": {
            "enabled": quality_filter.config.enabled,
            "soft_mode": quality_filter.config.soft_mode
        }
    }
