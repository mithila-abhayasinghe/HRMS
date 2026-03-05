"""
API routes module.
Contains all route handlers for the application.
"""

from app.api.routes.notifications import router as notifications_router

__all__ = ["notifications_router"]
