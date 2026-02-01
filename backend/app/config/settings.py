from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Centralized configuration using Pydantic Settings.
    All config values come from environment variables.
    """
    
    # Database
    DATABASE_URL: str = "sqlite:///./tts_saas.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # TTS Configuration
    TTS_ENGINE: str = "kokoro"  # Options: "kokoro", "xtts", "indicparler"
    USE_GPU: bool = False
    XTTS_MODEL_PATH: str = "./models/xtts_v2"
    MAX_CHARS_PER_REQUEST: int = 2000  # Increased since we now support chunking
    KOKORO_VOICE_PRESET: str = "af_sky"  # Default Kokoro voice
    
    # IndicParler-TTS Configuration
    INDICPARLER_MODEL: str = "ai4bharat/indic-parler-tts"
    SUPPORTED_INDIAN_LANGUAGES: list = [
        'hi', 'bn', 'ta', 'te', 'mr', 'gu', 'kn', 'ml',
        'pa', 'or', 'as', 'ur', 'sa', 'ks', 'ne', 'sd',
        'bo', 'doi', 'kok', 'mai', 'mni', 'sat'
    ]
    
    # Feature Flags
    ENABLE_VOICE_CLONING: bool = False  # Disabled for Kokoro (XTTS only)
    ENABLE_API_ACCESS: bool = True
    ENABLE_ADMIN_PANEL: bool = True
    
    # Pricing (characters) - Increased for unrestricted development
    FREE_DAILY_QUOTA: int = 1000000        # 1M characters per day
    STARTER_MONTHLY_QUOTA: int = 5000000   # 5M characters per month
    PRO_MONTHLY_QUOTA: int = 10000000      # 10M characters per month
    INDIC_LANGUAGE_MULTIPLIER: float = 2.0  # Indic languages cost 2x characters
    
    # Storage
    STORAGE_TYPE: str = "local"  # local, s3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = ""
    
    # Billing
    BILLING_PROVIDER: str = "razorpay"  # razorpay, stripe
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Use this function to get settings throughout the app.
    """
    return Settings()


# Pricing configuration (can be moved to database later)
# Use lambda or factory if we want these to be dynamic from settings at runtime,
# but for now we'll initialize them once.
_settings = get_settings()

PRICING_TIERS = {
    "free": {
        "price": 0,
        "quota_type": "daily",
        "quota": _settings.FREE_DAILY_QUOTA,
        "voice_cloning": False,
        "priority": 0
    },
    "starter": {
        "price": 299,
        "quota_type": "monthly",
        "quota": _settings.STARTER_MONTHLY_QUOTA,
        "voice_cloning": True,
        "priority": 1
    },
    "pro": {
        "price": 999,
        "quota_type": "monthly",
        "quota": _settings.PRO_MONTHLY_QUOTA,
        "voice_cloning": True,
        "priority": 2
    },
    "api": {
        "price": 0,  # Pay per use
        "quota_type": "unlimited",
        "quota": -1,
        "voice_cloning": True,
        "priority": 2
    }
}
