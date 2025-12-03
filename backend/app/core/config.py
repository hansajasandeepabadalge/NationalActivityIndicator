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
    MONGODB_DB_NAME: str = "national_indicator"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # Performance Settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # Redis Settings
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DEFAULT_TTL: int = 300

    # ML Model Settings (Day 3)
    ML_MODEL_DIR: str = "backend/models/ml_classifier"
    ML_MODEL_PATH: str = "backend/models/ml_classifier/ml_models.pkl"
    FEATURE_EXTRACTOR_PATH: str = "backend/models/ml_classifier/feature_extractor.pkl"
    ML_MODEL_MIN_F1: float = 0.60
    BATCH_SIZE: int = 32

    # Adaptive Model Selection (Scaling Strategy)
    ML_MODEL_TYPE: str = "auto"  # "auto", "logistic", or "xgboost"
    ML_AUTO_THRESHOLD: int = 100  # Use XGBoost if n_samples >= threshold

    # Hybrid Classification Settings
    RULE_WEIGHT: float = 0.7  # Conservative: trust rule-based more initially
    ML_WEIGHT: float = 0.3
    HYBRID_MIN_CONFIDENCE: float = 0.3
    USE_HYBRID_CLASSIFICATION: bool = False  # Enable after training

    # Training Data Settings
    TRAINING_DATA_PATH: str = "backend/data/training/"
    TRAINING_SIZE: int = 100
    VALIDATION_SPLIT: float = 0.2

    # Entity Extraction Settings (Day 4)
    SPACY_MODEL: str = "en_core_web_sm"
    ENTITY_EXTRACTION_MAX_CHARS: int = 1_000_000
    ENTITY_MIN_CONFIDENCE: float = 0.3

    # MongoDB Entity Storage
    MONGODB_ENTITY_COLLECTION: str = "entity_extractions"
    MONGODB_INDICATOR_COLLECTION: str = "indicator_calculations"

    # Narrative Generation (Day 6)
    NARRATIVE_EMOJI_ENABLED: bool = True
    NARRATIVE_MIN_SUMMARY_LENGTH: int = 50

    # API Settings (Day 6)
    API_RESPONSE_CACHE_TTL: int = 300  # 5 minutes
    API_MAX_HISTORY_DAYS: int = 90

    # Data Source Toggle
    USE_MOCK_DATA: bool = True  # Set to False for production/real data

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
