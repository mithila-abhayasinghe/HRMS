"""
FastAPI Application Entry Point.
User Management Service - Main application configuration and initialization.
Handles all routing, middleware setup, and lifecycle management.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.logging import get_logger
from app.api.users import router as users_router
from app.api.auth import router as auth_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 Starting User Management Service")
    logger.info("=" * 80)
    logger.info(f"Environment: DEBUG={settings.DEBUG}")
    logger.info(f"Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    logger.info(f"Asgardeo Domain: {settings.ASGARDEO_DOMAIN}")
    logger.info(f"Employee Service: {settings.EMPLOYEE_SERVICE_URL}")
    logger.info(f"Audit Service: {settings.AUDIT_SERVICE_URL}")
    logger.info(f"Compliance Service: {settings.COMPLIANCE_SERVICE_URL}")
    logger.info(f"Notification Service: {settings.NOTIFICATION_SERVICE_URL}")

    try:
        logger.info("Creating database and tables...")
        create_db_and_tables()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

    logger.info("=" * 80)
    logger.info("✅ Application startup complete")
    logger.info("=" * 80)

    yield

    # Shutdown
    logger.info("=" * 80)
    logger.info("🛑 Shutting down User Management Service")
    logger.info("=" * 80)


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="User Management Service - Authentication, Authorization, and User Lifecycle Management",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
app.include_router(users_router, prefix="/api/v1")


# Health check endpoints
@app.get("/", tags=["health"])
async def root():
    """
    Root endpoint - Simple health check.

    Returns basic service information.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Detailed health check endpoint.

    Returns comprehensive service status including database connectivity.

    Returns:
        Health status with service details
    """
    try:
        from app.core.database import engine

        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")

        database_status = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = "error"

    return {
        "status": "healthy" if database_status == "ok" else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": database_status,
        "asgardeo": "configured",
        "employee_service": settings.EMPLOYEE_SERVICE_URL,
        "audit_service": settings.AUDIT_SERVICE_URL,
        "compliance_service": settings.COMPLIANCE_SERVICE_URL,
        "notification_service": settings.NOTIFICATION_SERVICE_URL,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/ready", tags=["health"])
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.

    Indicates if the service is ready to accept traffic.

    Returns:
        200 if ready, 503 if not ready
    """
    try:
        from app.core.database import engine

        with engine.connect() as conn:
            conn.execute("SELECT 1")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ready": True, "service": settings.APP_NAME},
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"ready": False, "error": str(e)},
        )


@app.get("/health/live", tags=["health"])
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.

    Indicates if the service is alive and should continue running.

    Returns:
        200 if alive
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"alive": True, "service": settings.APP_NAME},
    )


# OpenAPI documentation customization
def custom_openapi():
    """
    Customize OpenAPI schema with additional documentation.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = app.openapi()

    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    openapi_schema["info"]["description"] = """
    # User Management Service

    A comprehensive REST API service for user authentication, authorization, and lifecycle management.

    ## Features

    - **OAuth 2.0 / OpenID Connect Integration** with Asgardeo
    - **User Authentication** - Signup and login flows
    - **User Lifecycle Management** - Create, update, suspend, delete users
    - **Role-Based Access Control (RBAC)** - Admin, HR Manager, Manager, Employee roles
    - **Profile Management** - Update user profiles and change passwords
    - **Integration** with Employee, Compliance, Notification, and Audit services
    - **Audit Logging** - Track all user-related operations
    - **Health Checks** - Readiness and liveness probes

    ## Authentication

    All protected endpoints require a valid JWT token in the Authorization header:

    ```
    Authorization: Bearer <token>
    ```

    ## API Endpoints

    ### Authentication (`/api/v1/auth`)
    - `POST /auth/signup` - Register new user
    - `POST /auth/callback` - OAuth callback
    - `POST /auth/logout` - Logout
    - `GET /auth/users/me` - Get current user profile
    - `PUT /auth/users/me` - Update profile
    - `PUT /auth/users/me/change-password` - Change password
    - `GET /auth/verify` - Verify token
    - `GET /auth/whoami` - Get current user info

    ### User Management (`/api/v1/users`)
    - `GET /users/` - List users (admin only)
    - `GET /users/{user_id}` - Get user details
    - `POST /users/{user_id}/role` - Update user role (admin only)
    - `PUT /users/{user_id}/suspend` - Suspend user (admin only)
    - `PUT /users/{user_id}/activate` - Activate user (admin only)
    - `DELETE /users/{user_id}` - Delete user (admin only)
    - `GET /users/permissions/roles` - List available roles
    - `GET /users/{user_id}/permissions` - Get user permissions

    ## Error Responses

    All errors follow a standard format:

    ```json
    {
        "detail": "Error message describing what went wrong"
    }
    ```

    Common HTTP status codes:
    - `200` - Success
    - `201` - Created
    - `400` - Bad Request (validation error)
    - `401` - Unauthorized (missing or invalid token)
    - `403` - Forbidden (insufficient permissions)
    - `404` - Not Found
    - `500` - Internal Server Error

    ## Integration with Other Services

    The User Management Service integrates with:

    - **Employee Service** - Creates employee records on user signup, terminates on deletion
    - **Audit Service** - Logs all user operations for compliance
    - **Compliance Service** - Validates policies before critical operations
    - **Notification Service** - Sends emails for account events

    ## Documentation

    - Swagger UI: `/docs`
    - ReDoc: `/redoc`
    - OpenAPI Schema: `/openapi.json`
    """

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
