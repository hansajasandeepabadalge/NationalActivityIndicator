"""
Layer 4 Data Module

Provides data aggregation and Layer 3 connectivity for LLM context building.
"""

from app.layer4.data.aggregator import DataAggregator, Layer3Connector

__all__ = ["DataAggregator", "Layer3Connector"]
