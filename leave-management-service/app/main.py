"""
FastAPI Application Entry Point.
Leave Management Service - Microservice for managing employee leave requests.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.logging import get_logger
from app.api.routes.leaves import router as leaves_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Leave Management Service...")
    logger.info("Creating database and tables...")
    create_db_and_tables()
    logger.info("Database and tables created successfully")
    logger.info("Leave Management Service startup complete")

    yield

    # Shutdown
    logger.info("Leave Management Service shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="Leave Management Service",
    description="Microservice for managing employee leave requests",
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
app.include_router(leaves_router, prefix="/api/v1")


# Health check endpoint
@app.get("/", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns service status and basic information.
    """
    return {
        "status": "healthy",
        "service": "Leave Management Service",
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["health"])
async def detailed_health_check():
    """
    Detailed health check endpoint.
    Returns service status with database information.
    """
    return {
        "status": "healthy",
        "service": "Leave Management Service",
        "version": settings.APP_VERSION,
        "database": settings.DB_NAME,
    }
