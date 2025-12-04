"""
Layer 4: Opportunity Detection Module

Detects business opportunities based on operational indicators.
"""
from app.layer4.opportunity_detection.rule_based_detector import (
    RuleBasedOpportunityDetector,
    OpportunityRule
)

__all__ = [
    'RuleBasedOpportunityDetector',
    'OpportunityRule'
]
