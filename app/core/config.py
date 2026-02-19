"""
Core application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "NoTracePDF"
    DEBUG: bool = False
    
    # File handling
    MAX_FILE_SIZE_MB: int = 100
    UPLOAD_DIR: str = "/tmp/uploads"
    
    # Timeouts
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        """Convert MB to bytes for upload size limit."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
