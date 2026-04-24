"""
AI Agent Orchestrator

Uses LangGraph to coordinate the AI agents in a directed graph workflow.
Manages state across the data collection pipeline.

Components:
    - MasterOrchestrator: Main LangGraph workflow controller
    - StateManager: Distributed state management with Redis

Usage:
    from app.layer1.orchestrator import create_orchestrator
    
    orchestrator = create_orchestrator()
    result = await orchestrator.run_cycle()
"""

from app.layer1.orchestrator.state import (
    StateManager,
    PipelinePhase,
    PipelineState,
    get_state_manager
)
from app.layer1.orchestrator.master import (
    MasterOrchestrator,
    create_orchestrator
)

__all__ = [
    # State Management
    "StateManager",
    "PipelinePhase",
    "PipelineState",
    "get_state_manager",
    # Orchestrator
    "MasterOrchestrator",
    "create_orchestrator"
]
