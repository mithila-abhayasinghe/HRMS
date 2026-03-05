"""
API module for FastAPI application.
Contains route definitions and API dependencies.
"""

from app.api.routes import notifications_router

__all__ = ["notifications_router"]
