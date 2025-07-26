"""
Configuration for the Course Creation Agent.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Agent settings."""
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    host: str = "http://localhost:8000"
    gemini_model: str = "gemini-1.5-flash"
    gemini_max_tokens: int = 4000
    gemini_temperature: float = 0.7

    class Config:
        case_sensitive = False
        env_file = ".env"


settings = Settings() 