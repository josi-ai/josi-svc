"""
Application configuration management.

This module centralizes all environment variables and configuration settings
for the Josi application. All settings can be overridden via environment
variables or a .env file.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden by setting the corresponding environment
    variable. For example, to set the database URL, set DATABASE_URL env var.
    """
    
    # Application settings
    app_name: str = Field(default="Josi API")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=True)
    environment: str = Field(default="development")
    
    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=1)
    
    # Database settings
    database_url: str = Field(default="postgresql://josi:josi@localhost:5432/josi")
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)
    auto_db_migration: bool = Field(default=False)
    
    # Auth provider: "clerk" or "descope"
    auth_provider: str = Field(default="clerk")

    # Descope settings
    descope_project_id: str = Field(default="")
    descope_management_key: str = Field(default="")
    descope_webhook_secret: str = Field(default="")

    # Clerk settings
    clerk_secret_key: str = Field(default="")
    clerk_publishable_key: str = Field(default="")
    clerk_webhook_secret: str = Field(default="")

    # Keep api_key_header
    api_key_header: str = Field(default="X-API-Key")
    
    # CORS settings
    cors_origins: List[str] = Field(default=["*"])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])
    
    # External services
    redis_url: Optional[str] = Field(default=None)
    
    # Logging settings
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Swiss Ephemeris settings
    ephemeris_path: str = Field(default="/usr/share/swisseph")
    
    # Geocoding settings
    geocoding_timeout: int = Field(default=10)
    geocoding_cache_ttl: int = Field(default=86400)  # 24 hours
    
    # API rate limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60)
    
    # Response compression
    gzip_minimum_size: int = Field(default=1000)
    
    
    # AI service settings
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    
    # Twilio settings for video consultations
    twilio_account_sid: Optional[str] = Field(default=None)
    twilio_auth_token: Optional[str] = Field(default=None)
    twilio_api_key: Optional[str] = Field(default=None)
    twilio_api_secret: Optional[str] = Field(default=None)
    
    # Base URL for webhooks
    base_url: str = Field(default="http://localhost:8000")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v):
        """Parse CORS methods from comma-separated string."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v):
        """Parse CORS headers from comma-separated string."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        """Ensure database URL is valid."""
        if not v.startswith(("postgresql://", "postgres://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must be a PostgreSQL connection string")
        return v
    
    model_config = ConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Create a singleton instance
settings = Settings()