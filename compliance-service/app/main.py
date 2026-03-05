"""
FastAPI Application Entry Point.
Compliance Service - GDPR compliance management and data inventory tracking.
Main application file with modular configuration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.logging import get_logger
from app.api.routes.compliance import router as compliance_router
from app.api.routes.data_inventory_management import router as inventory_router
from app.api.routes.auth import router as auth_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Compliance Service...")
    logger.info("Creating database and tables...")
    create_db_and_tables()
    logger.info("Database and tables created successfully")
    logger.info("Compliance Service startup complete")

    yield

    # Shutdown
    logger.info("Compliance Service shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="GDPR Compliance Service - Data Inventory, Access Control, and Retention Management",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(compliance_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")


# Health check endpoints
@app.get("/", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns service status and basic information.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["health"])
async def detailed_health_check():
    """
    Detailed health check endpoint.
    Returns service status and database information.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": settings.DB_NAME,
        "endpoints": {
            "compliance": "/api/v1/compliance",
            "inventory": "/api/v1/compliance/inventory",
            "auth": "/api/v1/auth",
        },
    }


@app.get("/docs/endpoints", tags=["documentation"])
async def api_endpoints_info():
    """
    Get information about available API endpoints.
    """
    return {
        "service": "Compliance Service",
        "version": settings.APP_VERSION,
        "endpoints": {
            "data_inventory": {
                "GET /api/v1/compliance/data-inventory": "Complete map of all data (GDPR Article 30)",
                "GET /api/v1/compliance/employee/{employee_id}/data-about-me": "Employee's personal data summary (GDPR Article 15)",
                "GET /api/v1/compliance/employee/{employee_id}/access-controls": "What data employee can access and why",
                "GET /api/v1/compliance/data-retention-report": "Data age and deletion requirements (GDPR Article 5)",
            },
            "inventory_management": {
                "POST /api/v1/compliance/inventory/categories": "Create data category",
                "GET /api/v1/compliance/inventory/categories": "List all categories",
                "POST /api/v1/compliance/inventory/entries": "Create inventory entry",
                "GET /api/v1/compliance/inventory/entries": "List inventory entries",
            },
            "authentication": {
                "GET /api/v1/auth/whoami": "Get current user info",
                "GET /api/v1/auth/verify": "Verify JWT token",
                "GET /api/v1/auth/debug": "Debug token contents",
            },
        },
    }
