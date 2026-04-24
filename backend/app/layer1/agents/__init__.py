"""
AI Agent System for Layer 1 - Intelligent Data Collection

This module provides AI-powered agents that intelligently orchestrate
the data collection, processing, and validation pipeline.

Agents:
    - SourceMonitorAgent: Decides WHEN to scrape each source
    - ProcessingAgent: Routes content to appropriate processors
    - PriorityDetectionAgent: Detects urgent/critical content
    - ValidationAgent: Ensures data quality
    - SchedulerAgent: Optimizes scraping frequencies

Usage:
    from app.layer1.agents import create_orchestrator
    
    orchestrator = create_orchestrator()
    result = await orchestrator.run_cycle()
"""

from app.layer1.agents.config import AgentConfig, get_agent_config
from app.core.llm.manager import LLMManager
from app.layer1.agents.base_agent import BaseAgent
from app.layer1.agents.source_monitor_agent import SourceMonitorAgent
from app.layer1.agents.processing_agent import ProcessingAgent
from app.layer1.agents.priority_agent import PriorityDetectionAgent
from app.layer1.agents.validation_agent import ValidationAgent
from app.layer1.agents.scheduler_agent import SchedulerAgent

__all__ = [
    # Config
    "AgentConfig",
    "get_agent_config",
    # LLM Manager
    "LLMManager",
    # Base
    "BaseAgent",
    # Agents
    "SourceMonitorAgent",
    "ProcessingAgent",
    "PriorityDetectionAgent",
    "ValidationAgent",
    "SchedulerAgent",
]
