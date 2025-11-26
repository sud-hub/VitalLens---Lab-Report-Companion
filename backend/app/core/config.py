from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./lab_companion.db"
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GEMINI_API_KEY: str = ""
    BACKEND_CORS_ORIGINS: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra fields in .env file
    )


settings = Settings()
