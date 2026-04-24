"""
Reputation System Module

Modularized representation of the Self-Learning source credibility system.
Exposes standard interfaces while abstracting DB, Math, and Tasks.
"""

from app.services.reputation.config import (
    ReputationTier, 
    FilterAction, 
    ReputationConfig, 
    FilterResult, 
    ReputationUpdate
)
from app.services.reputation.manager import ReputationManager, create_reputation_manager

__all__ = [
    "ReputationTier",
    "FilterAction",
    "ReputationConfig",
    "FilterResult",
    "ReputationUpdate",
    "ReputationManager",
    "create_reputation_manager"
]
