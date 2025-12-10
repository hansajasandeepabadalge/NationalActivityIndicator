"""
Layer 5: Dashboard System

Provides authentication, user management, and dashboard APIs for
displaying indicators and business insights.

Two Role System:
- ADMIN: Access to all national indicators, industry views, and all business insights
- USER: Access to their company profile, operational indicators, and company-specific insights
"""

from .config import layer5_settings

__all__ = ['layer5_settings']
