"""
API clients package.
Contains clients for external services.
"""

from app.api.clients.employee_service import EmployeeServiceClient, employee_service

__all__ = ["EmployeeServiceClient", "employee_service"]
