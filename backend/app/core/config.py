import os
from pydantic_settings import BaseSettings
from typing import Optional

def get_database_url():
    """Get database URL based on environment"""
    # Check if running inside Docker
    in_docker = os.path.exists('/.dockerenv') or os.getenv('DATABASE_URL') or os.getenv('DOCKER_ENV') == 'true'

    if in_docker and os.getenv('DATABASE_URL'):
        # Use environment variable (for Docker container)
        return os.getenv('DATABASE_URL')
    elif in_docker:
        # Use Docker service name
        return 'postgresql://postgres:postgres_secure_2024@timescaledb:5432/national_indicator'
    else:
        # Use 127.0.0.1 (for host machine - forces IPv4)
        return 'postgresql://postgres:postgres_secure_2024@127.0.0.1:5432/national_indicator'

class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str = "National Activity Indicator"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database Passwords (for Docker)
    POSTGRES_PASSWORD: str = "postgres_secure_2024"
    MONGO_PASSWORD: str = "mongo_secure_2024"
    PGADMIN_EMAIL: str = "admin@indicator.local"
    PGADMIN_PASSWORD: str = "admin_secure_2024"
    MONGO_EXPRESS_PASSWORD: str = "admin"

    # Database URLs (dynamically adjusted for Docker/host)
    DATABASE_URL: str = get_database_url()
    TIMESCALEDB_URL: str = get_database_url()
    MONGODB_URL: str = "mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # Performance Settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # Redis Settings
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DEFAULT_TTL: int = 300

    # ML Model Settings
    ML_MODEL_PATH: str = "ml_models/indicator_classifier_v1.pkl"
    BATCH_SIZE: int = 32

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
