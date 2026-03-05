"""
Leave Management Service - Leave API routes.
Handles all CRUD operations for leave requests and status management.
"""

from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from sqlmodel import select

from app.api.deps import SessionDep
from app.models.leave import Leave, LeaveStatus
from app.schemas.leave import LeaveCreate, LeavePublic, LeaveStatusUpdate
from app.core.logging import get_logger
from app.services.employee_service import verify_employee_exists

logger = get_logger(__name__)

# Create router with prefix and tags for better organization
router = APIRouter(
    prefix="/leaves",
    tags=["leaves"],
    responses={404: {"description": "Leave not found"}},
)


@router.post("/", response_model=LeavePublic, status_code=201)
def create_leave(leave: LeaveCreate, session: SessionDep) -> Leave:
    """
    Create a new leave request.

    - Validates that the employee exists via employee service
    - Validates that start_date is before end_date
    - Sets initial status to PENDING

    Args:
        leave: Leave data from request body
        session: Database session (injected)

    Returns:
        Created leave request with generated ID

    Raises:
        HTTPException: 400 if validation fails, 404 if employee not found
    """
    logger.info(f"Creating new leave for employee {leave.employee_id}")

    # Validate dates
    if leave.start_date >= leave.end_date:
        logger.warning(f"Invalid date range: {leave.start_date} >= {leave.end_date}")
        raise HTTPException(
            status_code=400, detail="start_date must be before end_date"
        )

    # Verify employee exists
    if not verify_employee_exists(leave.employee_id):
        logger.warning(f"Employee {leave.employee_id} not found")
        raise HTTPException(status_code=404, detail="Employee not found")

    db_leave = Leave.model_validate(leave)
    db_leave.status = LeaveStatus.PENDING
    db_leave.created_at = datetime.now(timezone.utc)
    db_leave.updated_at = datetime.now(timezone.utc)

    session.add(db_leave)
    session.commit()
    session.refresh(db_leave)
    logger.info(f"Leave created successfully with ID: {db_leave.id}")
    return db_leave


@router.get("/", response_model=list[LeavePublic])
def list_leaves(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    status: str | None = None,
) -> list[Leave]:
    """
    List all leaves with optional filtering and pagination.

    Args:
        session: Database session (injected)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        status: Filter by leave status (optional)

    Returns:
        List of leave requests
    """
    logger.info(f"Fetching leaves with offset={offset}, limit={limit}, status={status}")

    query = select(Leave)

    if status:
        try:
            status_enum = LeaveStatus(status)
            query = query.where(Leave.status == status_enum)
        except ValueError:
            logger.warning(f"Invalid status filter: {status}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join([s.value for s in LeaveStatus])}",
            )

    leaves = session.exec(query.offset(offset).limit(limit)).all()
    logger.info(f"Retrieved {len(leaves)} leave(s)")
    return list(leaves)


@router.get("/{leave_id}", response_model=LeavePublic)
def get_leave(leave_id: int, session: SessionDep) -> Leave:
    """
    Retrieve a specific leave request by ID.

    Args:
        leave_id: The ID of the leave to retrieve
        session: Database session (injected)

    Returns:
        Leave request data

    Raises:
        HTTPException: 404 if leave not found
    """
    logger.info(f"Fetching leave with ID: {leave_id}")
    leave = session.get(Leave, leave_id)
    if not leave:
        logger.warning(f"Leave with ID {leave_id} not found")
        raise HTTPException(status_code=404, detail="Leave not found")
    logger.info(f"Leave found: {leave.id}")
    return leave


@router.get("/employee/{employee_id}", response_model=list[LeavePublic])
def get_employee_leaves(
    employee_id: int,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    status: str | None = None,
) -> list[Leave]:
    """
    Retrieve all leaves for a specific employee.

    Args:
        employee_id: The ID of the employee
        session: Database session (injected)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        status: Filter by leave status (optional)

    Returns:
        List of leave requests for the employee

    Raises:
        HTTPException: 404 if employee not found
    """
    logger.info(f"Fetching leaves for employee {employee_id}")

    # Verify employee exists
    if not verify_employee_exists(employee_id):
        logger.warning(f"Employee {employee_id} not found")
        raise HTTPException(status_code=404, detail="Employee not found")

    query = select(Leave).where(Leave.employee_id == employee_id)

    if status:
        try:
            status_enum = LeaveStatus(status)
            query = query.where(Leave.status == status_enum)
        except ValueError:
            logger.warning(f"Invalid status filter: {status}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join([s.value for s in LeaveStatus])}",
            )

    leaves = session.exec(query.offset(offset).limit(limit)).all()
    logger.info(f"Retrieved {len(leaves)} leave(s) for employee {employee_id}")
    return list(leaves)


@router.put("/{leave_id}", response_model=LeavePublic)
def update_leave_status(
    leave_id: int,
    status_update: LeaveStatusUpdate,
    session: SessionDep,
) -> Leave:
    """
    Update the status of a leave request.

    - Supports status transitions: PENDING -> APPROVED/REJECTED/CANCELLED
    - Requires approved_by when approving
    - Requires rejection_reason when rejecting

    Args:
        leave_id: The ID of the leave to update
        status_update: New status and related information
        session: Database session (injected)

    Returns:
        Updated leave request

    Raises:
        HTTPException: 404 if leave not found, 400 for invalid transitions
    """
    logger.info(
        f"Attempting to update leave {leave_id} status to {status_update.status}"
    )

    leave = session.get(Leave, leave_id)
    if not leave:
        logger.warning(f"Leave with ID {leave_id} not found for update")
        raise HTTPException(status_code=404, detail="Leave not found")

    # Validate status transition
    if (
        leave.status != LeaveStatus.PENDING
        and status_update.status != LeaveStatus.CANCELLED
    ):
        logger.warning(
            f"Invalid status transition from {leave.status} to {status_update.status}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change status from {leave.status.value} to {status_update.status.value}",
        )

    # Validate required fields for approval
    if status_update.status == LeaveStatus.APPROVED and not status_update.approved_by:
        logger.warning("Approval requires approved_by field")
        raise HTTPException(
            status_code=400, detail="approved_by is required when approving a leave"
        )

    # Validate required fields for rejection
    if (
        status_update.status == LeaveStatus.REJECTED
        and not status_update.rejection_reason
    ):
        logger.warning("Rejection requires rejection_reason field")
        raise HTTPException(
            status_code=400,
            detail="rejection_reason is required when rejecting a leave",
        )

    # Update leave
    leave.status = status_update.status
    leave.approved_by = status_update.approved_by
    leave.rejection_reason = status_update.rejection_reason
    leave.updated_at = datetime.now(timezone.utc)

    session.add(leave)
    session.commit()
    session.refresh(leave)
    logger.info(f"Leave {leave_id} status updated to {status_update.status.value}")
    return leave


@router.delete("/{leave_id}")
def cancel_leave(leave_id: int, session: SessionDep) -> dict[str, bool]:
    """
    Cancel a leave request.

    - Only allows cancellation of PENDING or APPROVED leaves
    - Changes status to CANCELLED

    Args:
        leave_id: The ID of the leave to cancel
        session: Database session (injected)

    Returns:
        Success confirmation

    Raises:
        HTTPException: 404 if leave not found, 400 if leave cannot be cancelled
    """
    logger.info(f"Attempting to cancel leave with ID: {leave_id}")

    leave = session.get(Leave, leave_id)
    if not leave:
        logger.warning(f"Leave with ID {leave_id} not found for cancellation")
        raise HTTPException(status_code=404, detail="Leave not found")

    # Check if leave can be cancelled
    if leave.status in [LeaveStatus.CANCELLED, LeaveStatus.REJECTED]:
        logger.warning(f"Cannot cancel leave with status {leave.status.value}")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel a leave with status {leave.status.value}",
        )

    leave.status = LeaveStatus.CANCELLED
    leave.updated_at = datetime.now(timezone.utc)

    session.add(leave)
    session.commit()
    logger.info(f"Leave with ID {leave_id} cancelled successfully")
    return {"ok": True}
