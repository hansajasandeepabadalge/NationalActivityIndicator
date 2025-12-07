"""
State Manager for AI Agent Orchestrator

Manages the state of the data collection pipeline across agent executions.
Uses Redis for distributed state management.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum

import redis.asyncio as redis

from app.agents.config import get_agent_config

logger = logging.getLogger(__name__)


class PipelinePhase(str, Enum):
    """Phases of the data collection pipeline."""
    IDLE = "idle"
    MONITORING = "monitoring"
    SCRAPING = "scraping"
    PROCESSING = "processing"
    VALIDATION = "validation"
    STORAGE = "storage"
    COMPLETED = "completed"
    ERROR = "error"


class PipelineState(TypedDict):
    """TypedDict for pipeline state."""
    run_id: str
    phase: str
    started_at: str
    updated_at: str
    sources_to_scrape: List[str]
    scraped_content: List[Dict[str, Any]]
    processed_articles: List[Dict[str, Any]]
    validated_articles: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    metrics: Dict[str, Any]


class StateManager:
    """
    Manages distributed state for the AI agent orchestrator.
    
    Uses Redis for state persistence to support:
    - Distributed execution
    - Recovery from failures
    - State inspection/debugging
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize state manager with Redis connection."""
        config = get_agent_config()
        self.redis_url = redis_url or config.redis_url
        self._redis: Optional[redis.Redis] = None
        
        # State key prefix
        self.prefix = "agent_state:"
        
        # TTL for state entries (24 hours)
        self.state_ttl = 86400
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self._redis.ping()
                logger.info("StateManager connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                # Fall back to in-memory state
                self._redis = None
                self._memory_state: Dict[str, str] = {}
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    def _get_key(self, run_id: str, key: str) -> str:
        """Generate Redis key for a state entry."""
        return f"{self.prefix}{run_id}:{key}"
    
    async def create_run(self) -> str:
        """
        Create a new pipeline run.
        
        Returns:
            run_id: Unique identifier for this run
        """
        run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        
        initial_state: PipelineState = {
            "run_id": run_id,
            "phase": PipelinePhase.IDLE.value,
            "started_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "sources_to_scrape": [],
            "scraped_content": [],
            "processed_articles": [],
            "validated_articles": [],
            "errors": [],
            "metrics": {
                "sources_analyzed": 0,
                "articles_scraped": 0,
                "articles_processed": 0,
                "articles_validated": 0,
                "articles_stored": 0,
                "errors_count": 0
            }
        }
        
        await self._set_state(run_id, initial_state)
        logger.info(f"Created new pipeline run: {run_id}")
        
        return run_id
    
    async def get_state(self, run_id: str) -> Optional[PipelineState]:
        """
        Get the current state for a pipeline run.
        
        Args:
            run_id: The run identifier
            
        Returns:
            Current state or None if not found
        """
        key = self._get_key(run_id, "state")
        
        try:
            if self._redis:
                data = await self._redis.get(key)
            else:
                data = self._memory_state.get(key)
            
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Error getting state for {run_id}: {e}")
        
        return None
    
    async def _set_state(self, run_id: str, state: PipelineState) -> None:
        """Set the complete state for a run."""
        state["updated_at"] = datetime.utcnow().isoformat()
        key = self._get_key(run_id, "state")
        
        try:
            data = json.dumps(state, default=str)
            if self._redis:
                await self._redis.setex(key, self.state_ttl, data)
            else:
                self._memory_state[key] = data
        except Exception as e:
            logger.error(f"Error setting state for {run_id}: {e}")
    
    async def update_phase(
        self, 
        run_id: str, 
        phase: PipelinePhase
    ) -> None:
        """Update the current phase of the pipeline."""
        state = await self.get_state(run_id)
        if state:
            state["phase"] = phase.value
            await self._set_state(run_id, state)
            logger.info(f"Run {run_id}: Phase updated to {phase.value}")
    
    async def set_sources_to_scrape(
        self, 
        run_id: str, 
        sources: List[str]
    ) -> None:
        """Set the list of sources that should be scraped."""
        state = await self.get_state(run_id)
        if state:
            state["sources_to_scrape"] = sources
            state["metrics"]["sources_analyzed"] = len(sources)
            await self._set_state(run_id, state)
    
    async def add_scraped_content(
        self, 
        run_id: str, 
        content: Dict[str, Any]
    ) -> None:
        """Add scraped content to the state."""
        state = await self.get_state(run_id)
        if state:
            state["scraped_content"].append(content)
            state["metrics"]["articles_scraped"] += 1
            await self._set_state(run_id, state)
    
    async def add_processed_article(
        self, 
        run_id: str, 
        article: Dict[str, Any]
    ) -> None:
        """Add a processed article to the state."""
        state = await self.get_state(run_id)
        if state:
            state["processed_articles"].append(article)
            state["metrics"]["articles_processed"] += 1
            await self._set_state(run_id, state)
    
    async def add_validated_article(
        self, 
        run_id: str, 
        article: Dict[str, Any]
    ) -> None:
        """Add a validated article to the state."""
        state = await self.get_state(run_id)
        if state:
            state["validated_articles"].append(article)
            state["metrics"]["articles_validated"] += 1
            await self._set_state(run_id, state)
    
    async def add_error(
        self, 
        run_id: str, 
        error: Dict[str, Any]
    ) -> None:
        """Add an error to the state."""
        state = await self.get_state(run_id)
        if state:
            error["timestamp"] = datetime.utcnow().isoformat()
            state["errors"].append(error)
            state["metrics"]["errors_count"] += 1
            await self._set_state(run_id, state)
    
    async def increment_metric(
        self, 
        run_id: str, 
        metric_name: str, 
        amount: int = 1
    ) -> None:
        """Increment a metric counter."""
        state = await self.get_state(run_id)
        if state:
            if metric_name in state["metrics"]:
                state["metrics"][metric_name] += amount
            else:
                state["metrics"][metric_name] = amount
            await self._set_state(run_id, state)
    
    async def get_metrics(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a run."""
        state = await self.get_state(run_id)
        if state:
            return state["metrics"]
        return None
    
    async def complete_run(
        self, 
        run_id: str, 
        success: bool = True
    ) -> Dict[str, Any]:
        """
        Complete a pipeline run and return final metrics.
        
        Args:
            run_id: The run identifier
            success: Whether the run completed successfully
            
        Returns:
            Final run summary
        """
        state = await self.get_state(run_id)
        if not state:
            return {"error": "Run not found"}
        
        phase = PipelinePhase.COMPLETED if success else PipelinePhase.ERROR
        state["phase"] = phase.value
        state["updated_at"] = datetime.utcnow().isoformat()
        
        # Calculate duration
        started = datetime.fromisoformat(state["started_at"])
        duration = (datetime.utcnow() - started).total_seconds()
        state["metrics"]["duration_seconds"] = duration
        
        await self._set_state(run_id, state)
        
        return {
            "run_id": run_id,
            "success": success,
            "duration_seconds": duration,
            "metrics": state["metrics"],
            "errors": state["errors"] if not success else []
        }
    
    async def get_recent_runs(
        self, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get summaries of recent pipeline runs.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of run summaries
        """
        runs = []
        
        try:
            if self._redis:
                # Scan for all state keys
                pattern = f"{self.prefix}*:state"
                cursor = 0
                keys = []
                
                while True:
                    cursor, batch = await self._redis.scan(
                        cursor, 
                        match=pattern, 
                        count=100
                    )
                    keys.extend(batch)
                    if cursor == 0:
                        break
                
                # Get state for each run
                for key in keys[:limit]:
                    data = await self._redis.get(key)
                    if data:
                        state = json.loads(data)
                        runs.append({
                            "run_id": state["run_id"],
                            "phase": state["phase"],
                            "started_at": state["started_at"],
                            "metrics": state.get("metrics", {})
                        })
                
                # Sort by start time, most recent first
                runs.sort(key=lambda x: x["started_at"], reverse=True)
            else:
                # In-memory fallback
                for key, data in list(self._memory_state.items())[:limit]:
                    if key.endswith(":state"):
                        state = json.loads(data)
                        runs.append({
                            "run_id": state["run_id"],
                            "phase": state["phase"],
                            "started_at": state["started_at"],
                            "metrics": state.get("metrics", {})
                        })
                        
        except Exception as e:
            logger.error(f"Error getting recent runs: {e}")
        
        return runs[:limit]


# Singleton instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get the singleton StateManager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager
