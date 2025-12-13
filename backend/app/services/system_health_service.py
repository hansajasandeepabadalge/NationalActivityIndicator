"""
System Health Monitoring Service
Collects system metrics, database stats, and performance data
"""

import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

# Store for tracking metrics
_metrics_store = {
    "start_time": time.time(),
    "request_count": 0,
    "error_count": 0,
    "response_times": [],
    "recent_errors": [],
    "endpoint_stats": {},
}


class SystemHealthService:
    """Service for monitoring system health and performance"""

    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        """Get overall system status"""
        uptime_seconds = time.time() - _metrics_store["start_time"]
        
        return {
            "status": "healthy",
            "uptime_seconds": int(uptime_seconds),
            "uptime_formatted": str(timedelta(seconds=int(uptime_seconds))),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }

    @staticmethod
    def get_api_metrics() -> Dict[str, Any]:
        """Get API performance metrics"""
        total_requests = _metrics_store["request_count"]
        total_errors = _metrics_store["error_count"]
        response_times = _metrics_store["response_times"][-100:]  # Last 100 requests
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        success_rate = ((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 100
        
        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "success_rate": round(success_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "requests_per_minute": round(total_requests / (time.time() - _metrics_store["start_time"]) * 60, 2),
        }

    @staticmethod
    async def get_database_health(db) -> Dict[str, Any]:
        """Get database connection and performance stats"""
        try:
            # Get database stats
            stats = await db.command("dbStats")
            
            # Get collection counts
            collections = await db.list_collection_names()
            
            return {
                "status": "connected",
                "database_name": db.name,
                "collections_count": len(collections),
                "data_size_mb": round(stats.get("dataSize", 0) / (1024 * 1024), 2),
                "storage_size_mb": round(stats.get("storageSize", 0) / (1024 * 1024), 2),
                "indexes_count": stats.get("indexes", 0),
                "objects_count": stats.get("objects", 0),
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    def get_resource_usage() -> Dict[str, Any]:
        """Get system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": round(cpu_percent, 1),
                "memory_used_mb": round(memory.used / (1024 * 1024), 2),
                "memory_total_mb": round(memory.total / (1024 * 1024), 2),
                "memory_percent": round(memory.percent, 1),
                "disk_used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
                "disk_total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "disk_percent": round(disk.percent, 1),
            }
        except Exception as e:
            logger.error(f"Resource usage check failed: {str(e)}")
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "error": str(e)
            }

    @staticmethod
    def get_recent_errors(limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent error logs"""
        return _metrics_store["recent_errors"][-limit:]

    @staticmethod
    def track_request(endpoint: str, response_time_ms: float, status_code: int):
        """Track API request metrics"""
        _metrics_store["request_count"] += 1
        _metrics_store["response_times"].append(response_time_ms)
        
        # Keep only last 1000 response times
        if len(_metrics_store["response_times"]) > 1000:
            _metrics_store["response_times"] = _metrics_store["response_times"][-1000:]
        
        # Track per-endpoint stats
        if endpoint not in _metrics_store["endpoint_stats"]:
            _metrics_store["endpoint_stats"][endpoint] = {
                "count": 0,
                "total_time": 0,
                "errors": 0
            }
        
        _metrics_store["endpoint_stats"][endpoint]["count"] += 1
        _metrics_store["endpoint_stats"][endpoint]["total_time"] += response_time_ms
        
        if status_code >= 400:
            _metrics_store["error_count"] += 1
            _metrics_store["endpoint_stats"][endpoint]["errors"] += 1

    @staticmethod
    def log_error(error_type: str, message: str, endpoint: str = None):
        """Log an error"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "endpoint": endpoint,
        }
        
        _metrics_store["recent_errors"].append(error_entry)
        
        # Keep only last 100 errors
        if len(_metrics_store["recent_errors"]) > 100:
            _metrics_store["recent_errors"] = _metrics_store["recent_errors"][-100:]

    @staticmethod
    def get_endpoint_performance() -> List[Dict[str, Any]]:
        """Get performance stats for each endpoint"""
        endpoint_list = []
        
        for endpoint, stats in _metrics_store["endpoint_stats"].items():
            avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            error_rate = (stats["errors"] / stats["count"] * 100) if stats["count"] > 0 else 0
            
            endpoint_list.append({
                "endpoint": endpoint,
                "request_count": stats["count"],
                "avg_response_time_ms": round(avg_time, 2),
                "error_rate": round(error_rate, 2),
            })
        
        # Sort by average response time (slowest first)
        endpoint_list.sort(key=lambda x: x["avg_response_time_ms"], reverse=True)
        
        return endpoint_list[:10]  # Top 10 slowest endpoints
