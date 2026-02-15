"""Configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://kazuba:kazuba@db:5432/kazuba_saas"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_HOBBY: str = ""
    STRIPE_PRICE_PRO: str = ""
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Rate limits (per day)
    RATE_LIMIT_FREE: int = 50
    RATE_LIMIT_HOBBY: int = 500
    RATE_LIMIT_PRO: int = 5000
    
    # Doc limits (per month)
    DOC_LIMIT_FREE: int = 100
    DOC_LIMIT_HOBBY: int = 5000
    DOC_LIMIT_PRO: int = 50000
    
    class Config:
        env_file = ".env"


settings = Settings()
