"""
API routes package.
Exports all route routers for registration in the main application.
"""

from app.api.routes.compliance import router as compliance_router
from app.api.routes.data_inventory_management import router as inventory_router
from app.api.routes.auth import router as auth_router

__all__ = [
    "compliance_router",
    "inventory_router",
    "auth_router",
]
