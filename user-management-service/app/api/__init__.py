"""
API module for FastAPI application.
Contains route definitions and API dependencies.
"""

from app.api import users, auth

__all__ = ["users", "auth"]
