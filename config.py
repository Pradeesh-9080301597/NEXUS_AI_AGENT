"""
NEXUS AI Agent - Configuration Module
Manages application settings, environment variables, directory paths, and auth credentials.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""
    
    APP_NAME: str = "NEXUS - AI Career Intelligence Agent"
    APP_ENV: str = "development"
    
    # SQLite Database connection string
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'nexus.db'}"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(BASE_DIR / "logs" / "nexus.log")
    
    # LLM Settings
    GEMINI_API_KEY: str = ""
    LLM_MODEL_NAME: str = "gemini-2.5-flash"

    # Security & Authentication Settings
    SECRET_KEY: str = "nexus_super_secret_jwt_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # External Managed Auth (Supabase / Google OAuth)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure logs directory exists
os.makedirs(BASE_DIR / "logs", exist_ok=True)
