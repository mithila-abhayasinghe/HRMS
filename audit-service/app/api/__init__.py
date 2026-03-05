"""
API module for FastAPI application.
Contains route definitions and API dependencies.
"""

from app.api.routes import employees_router, auth_router

__all__ = ["employees_router", "auth_router"]
