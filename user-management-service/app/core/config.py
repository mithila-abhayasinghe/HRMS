"""
Application configuration module.
Centralized settings for database, CORS, Asgardeo integration, and service URLs.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings.
    Uses pydantic-settings for environment variable management.
    """

    # Application Settings
    APP_NAME: str = "User Management Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database Settings
    DB_NAME: str = "user_management_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_CHARSET: str = "utf8mb4"

    # CORS Settings
    CORS_ORIGINS: str = "https://localhost,http://localhost:3000,http://localhost:3000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS from comma-separated string."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return [self.CORS_ORIGINS]

    # JWT/JWKS Settings
    JWKS_URL: str = "https://api.asgardeo.io/t/pookieland/oauth2/jwks"
    JWT_AUDIENCE: str | None = None
    JWT_ISSUER: str | None = None
    JWT_SECRET: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_SECONDS: int = 3600

    # Asgardeo Configuration
    ASGARDEO_DOMAIN: str = "https://api.asgardeo.io/t/pookieland"
    ASGARDEO_CLIENT_ID: str = "your-client-id"
    ASGARDEO_CLIENT_SECRET: str = "your-client-secret"
    ASGARDEO_BEARER_TOKEN: str = "your-bearer-token"
    ASGARDEO_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    ASGARDEO_SCOPES: str = "openid email profile"

    # Service URLs for Integration
    EMPLOYEE_SERVICE_URL: str = "http://employee-service:8001"
    COMPLIANCE_SERVICE_URL: str = "http://compliance-service:8006"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8004"
    AUDIT_SERVICE_URL: str = "http://audit-service:8005"

    # Service Integration Settings
    SERVICE_REQUEST_TIMEOUT: int = 30  # seconds
    SERVICE_RETRY_COUNT: int = 3
    SERVICE_RETRY_DELAY: int = 1  # seconds

    # Role Definitions
    VALID_ROLES: List[str] = ["admin", "hr_manager", "manager", "employee"]
    DEFAULT_ROLE: str = "employee"

    # User Status Definitions
    VALID_STATUSES: List[str] = ["active", "suspended", "deleted"]
    DEFAULT_STATUS: str = "active"

    # Password Requirements
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_NUMBERS: bool = True
    REQUIRE_SPECIAL_CHARS: bool = True

    @property
    def database_url(self) -> str:
        """Generate MySQL database URL."""
        return f"mysql+mysqldb://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset={self.DB_CHARSET}"

    @property
    def database_url_without_db(self) -> str:
        """Generate MySQL URL without database name (for initial connection)."""
        return f"mysql+mysqldb://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}?charset={self.DB_CHARSET}"

    class Config:
        env_file = ".env.development"
        case_sensitive = True


# Create global settings instance
settings = Settings()
