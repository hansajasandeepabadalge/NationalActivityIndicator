import os

class Settings:
    PROJECT_NAME: str = "National Activity Indicator"
    API_V1_STR: str = "/api/v1"
    
    # Database URLs
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "layer3_db")
    SQLALCHEMY_DATABASE_URI: str = f"postgresql+pg8000://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    MONGO_SERVER: str = os.getenv("MONGO_SERVER", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", 27017))
    MONGO_DB: str = os.getenv("MONGO_DB", "layer3_mongo")

settings = Settings()
