"""
External Employee Service Client.
Handles communication with the dedicated employee management service.
"""

import httpx
from typing import Optional
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class EmployeeServiceClient:
    """
    Client for communicating with the external employee management service.
    Provides methods to verify employee existence and retrieve employee details.
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize the employee service client.

        Args:
            base_url: Base URL of the employee management service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def verify_employee_exists(self, employee_id: int) -> bool:
        """
        Verify if an employee exists in the employee management service.

        Args:
            employee_id: The ID of the employee to verify

        Returns:
            True if employee exists, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/employees/{employee_id}"
                )
                exists = response.status_code == 200
                logger.info(f"Employee {employee_id} existence check: {exists}")
                return exists
        except httpx.RequestError as e:
            logger.error(f"Error verifying employee {employee_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying employee {employee_id}: {str(e)}")
            return False

    async def get_employee(self, employee_id: int) -> Optional[dict]:
        """
        Retrieve employee details from the employee management service.

        Args:
            employee_id: The ID of the employee to retrieve

        Returns:
            Employee data if found, None otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/employees/{employee_id}"
                )
                if response.status_code == 200:
                    employee_data = response.json()
                    logger.info(f"Retrieved employee {employee_id} details")
                    return employee_data
                else:
                    logger.warning(
                        f"Employee {employee_id} not found (status: {response.status_code})"
                    )
                    return None
        except httpx.RequestError as e:
            logger.error(f"Error retrieving employee {employee_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error retrieving employee {employee_id}: {str(e)}"
            )
            return None

    async def get_employees_list(
        self, offset: int = 0, limit: int = 100
    ) -> Optional[list]:
        """
        Retrieve list of employees from the employee management service.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of employees if successful, None otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/employees/",
                    params={"offset": offset, "limit": limit},
                )
                if response.status_code == 200:
                    employees = response.json()
                    logger.info(f"Retrieved {len(employees)} employees")
                    return employees
                else:
                    logger.warning(
                        f"Failed to retrieve employees list (status: {response.status_code})"
                    )
                    return None
        except httpx.RequestError as e:
            logger.error(f"Error retrieving employees list: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving employees list: {str(e)}")
            return None


# Create a singleton instance
# URL should be set via environment variable: EMPLOYEE_SERVICE_URL
employee_service = EmployeeServiceClient(
    base_url=getattr(settings, "EMPLOYEE_SERVICE_URL", "http://localhost:8001")
)
