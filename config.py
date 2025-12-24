import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "MindLens API"
    DEBUG: bool = os.getenv("ENVIRONMENT", "development") == "development"

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Optional email credentials
    EMAIL_SENDER: str = os.getenv("EMAIL_SENDER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")

    # Allow extra .env fields (IMPORTANT FIX)
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "allow"   # <--- FIXES YOUR ERROR
    }


settings = Settings()
