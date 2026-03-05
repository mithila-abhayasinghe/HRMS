"""
Database models for the Compliance Service.
Exports all models for database table creation.
"""

from app.models.data_inventory import DataInventory, DataCategory
from app.models.employee_data_access import EmployeeDataAccess, DataRetention

__all__ = [
    "DataInventory",
    "DataCategory",
    "EmployeeDataAccess",
    "DataRetention",
]
