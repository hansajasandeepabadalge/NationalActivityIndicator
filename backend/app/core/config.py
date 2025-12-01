from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "National Activity Indicator"
    API_V1_STR: str = "/api/v1"
    
    # Database (Placeholder for now)
    # DATABASE_URL: str = "sqlite:///./sql_app.db"

    class Config:
        env_file = ".env"

settings = Settings()
