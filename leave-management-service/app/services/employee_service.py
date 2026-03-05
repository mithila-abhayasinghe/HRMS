"""
Leave Management Service - Employee Service Integration.
Handles communication with the Employee Service for employee validation.
Provides methods to verify employee existence.
"""

from app.core.config import settings
from app.core.logging import get_logger
import httpx

logger = get_logger(__name__)

# Cache for employee verification (can be enhanced with TTL)
_employee_cache = {}


def verify_employee_exists(employee_id: int) -> bool:
    """
    Verify that an employee exists via Employee Service.

    Integration Strategy:
    1. Check local cache first for performance
    2. Call Employee Service API if configured
    3. Return False if service unavailable or employee not found

    Args:
        employee_id: The ID of the employee to verify

    Returns:
        True if employee exists, False otherwise
    """
    # Check cache first
    if employee_id in _employee_cache:
        logger.debug(f"Employee {employee_id} found in cache")
        return _employee_cache[employee_id]

    # Call Employee Service API
    try:
        if not settings.EMPLOYEE_SERVICE_URL:
            logger.warning(
                f"EMPLOYEE_SERVICE_URL not configured, cannot verify employee {employee_id}"
            )
            return False

        result = _verify_via_employee_service(employee_id)
        _employee_cache[employee_id] = result
        return result

    except Exception as e:
        logger.error(f"Failed to verify employee {employee_id}: {e}")
        return False


def _verify_via_employee_service(employee_id: int) -> bool:
    """
    Verify employee existence by calling the Employee Service API.

    Args:
        employee_id: The ID of the employee to verify

    Returns:
        True if employee exists, False otherwise
    """
    try:
        employee_service_url = settings.EMPLOYEE_SERVICE_URL
        url = f"{employee_service_url}/api/v1/employees/{employee_id}"

        with httpx.Client(timeout=settings.EMPLOYEE_SERVICE_TIMEOUT) as client:
            response = client.get(url)

            if response.status_code == 200:
                logger.info(f"Employee {employee_id} verified via Employee Service")
                return True
            elif response.status_code == 404:
                logger.info(f"Employee {employee_id} not found in Employee Service")
                return False
            else:
                logger.warning(
                    f"Employee Service returned status {response.status_code} "
                    f"for employee {employee_id}"
                )
                return False

    except httpx.ConnectError as e:
        logger.error(f"Failed to connect to Employee Service: {e}")
        return False
    except httpx.TimeoutException as e:
        logger.error(f"Employee Service request timed out: {e}")
        return False
    except Exception as e:
        logger.error(f"Error calling Employee Service: {e}")
        return False


def get_employee_name(employee_id: int) -> str | None:
    """
    Retrieve the name of an employee by ID from Employee Service.

    This is a helper function for enriching leave data with employee information.

    Args:
        employee_id: The ID of the employee

    Returns:
        Employee name if found, None otherwise
    """
    try:
        if not settings.EMPLOYEE_SERVICE_URL:
            logger.debug(f"EMPLOYEE_SERVICE_URL not configured")
            return None

        name = _get_employee_name_from_service(employee_id)
        return name

    except Exception as e:
        logger.warning(f"Failed to get employee name: {e}")
        return None


def _get_employee_name_from_service(employee_id: int) -> str | None:
    """
    Get employee name from Employee Service API.

    Args:
        employee_id: The ID of the employee

    Returns:
        Employee name if found, None otherwise
    """
    try:
        employee_service_url = settings.EMPLOYEE_SERVICE_URL
        url = f"{employee_service_url}/api/v1/employees/{employee_id}"

        with httpx.Client(timeout=settings.EMPLOYEE_SERVICE_TIMEOUT) as client:
            response = client.get(url)

            if response.status_code == 200:
                data = response.json()
                return data.get("name")
            return None

    except Exception as e:
        logger.debug(f"Failed to get employee name from service: {e}")
        return None


def clear_employee_cache():
    """
    Clear the employee verification cache.

    Useful for testing or when employee data has been updated.
    """
    global _employee_cache
    _employee_cache.clear()
    logger.info("Employee cache cleared")
