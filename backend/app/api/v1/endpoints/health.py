"""
System Health API Routes
Endpoints for monitoring system health and performance
"""

from fastapi import APIRouter
from typing import Dict, Any
import logging

from app.services.system_health_service import SystemHealthService
from app.db.mongodb import get_mongodb

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["System Health"])


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """
    Get overall system status
    
    Returns:
        - status: System health status
        - uptime: Server uptime
        - version: API version
    """
    return SystemHealthService.get_system_status()


@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """
    Get comprehensive system metrics
    
    Returns:
        - api_metrics: API performance stats
        - resource_usage: CPU, memory, disk usage
        - endpoint_performance: Per-endpoint statistics
    """
    api_metrics = SystemHealthService.get_api_metrics()
    resource_usage = SystemHealthService.get_resource_usage()
    endpoint_performance = SystemHealthService.get_endpoint_performance()
    
    return {
        "api_metrics": api_metrics,
        "resource_usage": resource_usage,
        "endpoint_performance": endpoint_performance,
    }


@router.get("/database")
async def get_database_health() -> Dict[str, Any]:
    """
    Get database health and statistics
    
    Returns:
        - status: Database connection status
        - collections: Number of collections
        - data_size: Database size in MB
        - performance: Query performance metrics
    """
    db = get_mongodb()
    return await SystemHealthService.get_database_health(db)


@router.get("/errors")
async def get_recent_errors(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent error logs
    
    Args:
        limit: Number of recent errors to return (default: 10)
    
    Returns:
        - errors: List of recent errors with timestamps
        - total_errors: Total error count
    """
    errors = SystemHealthService.get_recent_errors(limit)
    
    return {
        "errors": errors,
        "total_errors": len(errors),
    }


@router.get("/all")
async def get_all_health_data() -> Dict[str, Any]:
    """
    Get all health monitoring data in one call
    
    Returns comprehensive health dashboard data
    """
    system_status = SystemHealthService.get_system_status()
    api_metrics = SystemHealthService.get_api_metrics()
    db = get_mongodb()
    database_health = await SystemHealthService.get_database_health(db)
    resource_usage = SystemHealthService.get_resource_usage()
    recent_errors = SystemHealthService.get_recent_errors(10)
    endpoint_performance = SystemHealthService.get_endpoint_performance()
    
    return {
        "system_status": system_status,
        "api_metrics": api_metrics,
        "database_health": database_health,
        "resource_usage": resource_usage,
        "recent_errors": recent_errors,
        "endpoint_performance": endpoint_performance,
        "timestamp": system_status["timestamp"],
    }
