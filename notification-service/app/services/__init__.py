"""
Services package initialization.
Exports service utilities for sending notifications.
"""

from app.services.email import send_email, send_notification_email

__all__ = ["send_email", "send_notification_email"]
