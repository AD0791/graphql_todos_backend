
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    DATABASE_URL: str = Field(
        ...,
        description="MySQL database connection URL. Format: mysql+aiomysql://user:password@host:port/database"
    )
    DB_NAME: str | None = Field(None, description="Database name")
    DB_USER: str | None = Field(None, description="Database user")
    DB_PASSWORD: str | None = Field(None, description="Database password")
    DB_ROOT_PASSWORD: str | None = Field(None, description="Database root password")

    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token signing. Generate with: openssl rand -hex 32"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        le=1440,
        description="Access token expiration time in minutes (1-1440)"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        ge=1,
        le=365,
        description="Refresh token expiration time in days (1-365)"
    )

    
    DEBUG: bool = Field(
        default=True,
        description="Debug mode. Must be False in production"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, or production"
    )
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )

    SUPERADMIN_EMAIL: str = Field(
        default="superadmin@example.com",
        description="Email for initial superadmin account"
    )
    SUPERADMIN_PASSWORD: str = Field(
        default="SuperAdmin123!",
        min_length=8,
        description="Password for initial superadmin account (min 8 characters)"
    )
    SUPERADMIN_FULL_NAME: str = Field(
        default="Super Administrator",
        description="Full name for initial superadmin account"
    )


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra env vars
    )

    # =========================================================================
    # VALIDATORS
    # =========================================================================
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure SECRET_KEY is strong enough for production."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator("DEBUG")
    @classmethod
    def validate_debug_in_production(cls, v: bool, info) -> bool:
        """Ensure DEBUG is False in production environment."""
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production" and v is True:
            raise ValueError("DEBUG must be False in production environment")
        return v
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Ensure environment is one of the allowed values."""
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(allowed)}")
        return v.lower()
    
    @field_validator("SUPERADMIN_PASSWORD")
    @classmethod
    def validate_superadmin_password(cls, v: str) -> str:
        """Ensure superadmin password meets security requirements."""
        if len(v) < 8:
            raise ValueError("SUPERADMIN_PASSWORD must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("SUPERADMIN_PASSWORD must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
           raise ValueError("SUPERADMIN_PASSWORD must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
           raise ValueError("SUPERADMIN_PASSWORD must contain at least one digit")
        return v

   
    @property
    def cors_origins_list(self) -> List[str] | List[None] :
        """
        Parse CORS_ORIGINS string into a list.
        
        Returns:
            List of allowed CORS origins
        """
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


# Create a singleton instance
settings = Settings()
