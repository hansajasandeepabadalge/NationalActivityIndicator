"""
Layer 5 Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Layer5Settings(BaseSettings):
    """Layer 5 Dashboard Configuration"""
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password hashing
    PASSWORD_HASH_ROUNDS: int = 12
    
    # Dashboard settings
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Cache settings
    DASHBOARD_CACHE_TTL: int = 60  # seconds
    
    # Feature flags
    ENABLE_WEBSOCKET: bool = False
    ENABLE_REALTIME_UPDATES: bool = False
    
    class Config:
        env_prefix = "LAYER5_"


layer5_settings = Layer5Settings()
