from pydantic_settings import BaseSettings

class LLMSettings(BaseSettings):
    """
    Configuration for Layer 2 AI/LLM Services.
    Loads from .env file.
    """
    # Core Provider Settings
    GROQ_API_KEY: str = ""
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.1-70b-versatile"
    LLM_TEMPERATURE: float = 0.1
    
    # Validation & Fallback
    ENABLE_LLM_VALIDATION: bool = True
    FALLBACK_TO_BASIC: bool = True
    
    # Caching
    ENABLE_LLM_CACHE: bool = True
    LLM_CACHE_TTL: int = 86400  # 24 hours
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,  # Environment variables are usually case-sensitive/uppercase
        "extra": "ignore"
    }

llm_settings = LLMSettings()
