from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bridge Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://bridge_user:bridge_password@localhost:5432/bridge_platform_dev"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # External Services
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@bridgeplatform.com"
    
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    
    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Bridge-specific settings
    DEFAULT_ORGANIZATION_ID: int = 1
    MASTERPOINTS_CALCULATION_METHOD: str = "standard"
    RATING_SYSTEM: str = "openskill"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()