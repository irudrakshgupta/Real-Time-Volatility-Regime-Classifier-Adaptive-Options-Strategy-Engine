from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "v1"
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Market Data API Keys
    ALPHA_VANTAGE_API_KEY: str
    POLYGON_API_KEY: str = ""

    # Model Configuration
    MODEL_PATH: str = "models/regime_classifier.pkl"
    FEATURE_SCALER_PATH: str = "models/feature_scaler.pkl"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Cache Configuration
    CACHE_TIMEOUT: int = 300  # 5 minutes
    REDIS_CACHE_ENABLED: bool = True

    # Market Data Configuration
    DEFAULT_TICKER: str = "SPX"
    UPDATE_INTERVAL: int = 60  # seconds
    HISTORICAL_DAYS: int = 252  # ~1 trading year

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 