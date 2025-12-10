"""
Layer 5: API Package
"""
from .auth_routes import router as auth_router
from .admin_routes import router as admin_router
from .user_routes import router as user_router
from .user_operations import router as operations_router

__all__ = ['auth_router', 'admin_router', 'user_router', 'operations_router']
