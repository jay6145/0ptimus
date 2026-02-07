"""
Application configuration
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///data/inventory.db"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Security
    SECRET_KEY: str = "hackathon-demo-secret-key-change-in-production"
    
    # Demo Data
    DEMO_NUM_STORES: int = 5
    DEMO_NUM_SKUS: int = 200
    DEMO_DAYS_HISTORY: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
