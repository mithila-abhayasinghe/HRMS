"""
FastAPI Application Entry Point.
Main application file for Audit Service with minimal configuration - delegates to modular components.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.logging import get_logger
from app.api.routes.employees import router as audit_logs_router
from app.api.routes.auth import router as auth_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Audit Service...")
    logger.info("Creating database and tables...")
    create_db_and_tables()
    logger.info("Database and tables created successfully")
    logger.info("Audit Service startup complete")

    yield

    # Shutdown
    logger.info("Audit Service shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Centralized audit and compliance logging service for HRMS microservices",
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
app.include_router(audit_logs_router, prefix="/api/v1")


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
    Returns comprehensive service status including database connectivity.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": settings.DB_NAME,
        "environment": "production" if not settings.DEBUG else "development",
    }


@app.get("/ready", tags=["health"])
async def readiness_check():
    """
    Readiness check endpoint.
    Used by orchestration platforms (Kubernetes) to determine if the service is ready to accept traffic.
    """
    return {
        "ready": True,
        "service": settings.APP_NAME,
    }
