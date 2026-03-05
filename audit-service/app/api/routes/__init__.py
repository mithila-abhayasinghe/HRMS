"""
API routes module.
Contains all API endpoint routers organized by resource.
"""

from app.api.routes.employees import router as employees_router
from app.api.routes.auth import router as auth_router

__all__ = ["employees_router", "auth_router"]
