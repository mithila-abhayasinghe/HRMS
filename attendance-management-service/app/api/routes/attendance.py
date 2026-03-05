"""
Attendance API routes.
Handles all operations for attendance records including check-in, check-out, and manual entries.
"""

from typing import Annotated
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query

from app.api.dependencies import SessionDep
from app.api.clients.employee_service import employee_service
from app.models.attendance import (
    Attendance,
    AttendancePublic,
    AttendanceCreate,
    AttendanceUpdate,
    CheckInRequest,
    CheckOutRequest,
    MonthlySummary,
)
from app.core.logging import get_logger
from sqlmodel import select

logger = get_logger(__name__)

# Create router with prefix and tags for better organization
router = APIRouter(
    prefix="/attendance",
    tags=["attendance"],
    responses={404: {"description": "Attendance record not found"}},
)


@router.post("/check-in", response_model=AttendancePublic, status_code=201)
async def check_in(request: CheckInRequest, session: SessionDep) -> Attendance:
    """
    Employee check-in endpoint.
    Records the check-in time for an employee on the current date.

    Args:
        request: Check-in request with employee_id
        session: Database session (injected)

    Returns:
        Created or updated attendance record with check-in time

    Raises:
        HTTPException: 400 if employee doesn't exist, 404 if not found
    """
    # Verify employee exists in employee service
    employee_exists = await employee_service.verify_employee_exists(request.employee_id)
    if not employee_exists:
        logger.warning(
            f"Check-in attempted for non-existent employee {request.employee_id}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Employee {request.employee_id} does not exist",
        )

    # Get today's date in YYYY-MM-DD format
    today = datetime.utcnow().date().isoformat()
    check_in_time = datetime.utcnow()

    # Check if attendance record already exists for today
    statement = select(Attendance).where(
        (Attendance.employee_id == request.employee_id) & (Attendance.date == today)
    )
    existing_record = session.exec(statement).first()

    if existing_record:
        # Update existing record with check-in time
        logger.info(f"Updating check-in for employee {request.employee_id} on {today}")
        existing_record.check_in_time = check_in_time
        existing_record.status = "present"
        existing_record.updated_at = datetime.utcnow()
        session.add(existing_record)
        session.commit()
        session.refresh(existing_record)
        logger.info(f"Employee {request.employee_id} checked in at {check_in_time}")
        return existing_record
    else:
        # Create new attendance record
        logger.info(
            f"Creating new check-in for employee {request.employee_id} on {today}"
        )
        new_record = Attendance(
            employee_id=request.employee_id,
            date=today,
            check_in_time=check_in_time,
            status="present",
        )
        session.add(new_record)
        session.commit()
        session.refresh(new_record)
        logger.info(f"Employee {request.employee_id} checked in at {check_in_time}")
        return new_record


@router.post("/check-out", response_model=AttendancePublic, status_code=200)
async def check_out(request: CheckOutRequest, session: SessionDep) -> Attendance:
    """
    Employee check-out endpoint.
    Records the check-out time for an employee on the current date.

    Args:
        request: Check-out request with employee_id
        session: Database session (injected)

    Returns:
        Updated attendance record with check-out time

    Raises:
        HTTPException: 400 if employee doesn't exist, 404 if no check-in found
    """
    # Verify employee exists in employee service
    employee_exists = await employee_service.verify_employee_exists(request.employee_id)
    if not employee_exists:
        logger.warning(
            f"Check-out attempted for non-existent employee {request.employee_id}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Employee {request.employee_id} does not exist",
        )

    # Get today's date in YYYY-MM-DD format
    today = datetime.utcnow().date().isoformat()
    check_out_time = datetime.utcnow()

    # Find today's attendance record
    statement = select(Attendance).where(
        (Attendance.employee_id == request.employee_id) & (Attendance.date == today)
    )
    record = session.exec(statement).first()

    if not record:
        logger.warning(
            f"Check-out attempted but no check-in found for employee {request.employee_id} on {today}"
        )
        raise HTTPException(
            status_code=404,
            detail="No check-in record found for today. Please check in first.",
        )

    # Update record with check-out time
    logger.info(f"Updating check-out for employee {request.employee_id} on {today}")
    record.check_out_time = check_out_time
    record.updated_at = datetime.utcnow()
    session.add(record)
    session.commit()
    session.refresh(record)
    logger.info(f"Employee {request.employee_id} checked out at {check_out_time}")
    return record


@router.post("/manual", response_model=AttendancePublic, status_code=201)
async def create_manual_attendance(
    attendance: AttendanceCreate, session: SessionDep
) -> Attendance:
    """
    Create manual attendance entry.
    Allows admins to manually record attendance for employees.

    Args:
        attendance: Attendance data for manual entry
        session: Database session (injected)

    Returns:
        Created attendance record

    Raises:
        HTTPException: 400 if employee doesn't exist or date format invalid
    """
    # Verify employee exists in employee service
    employee_exists = await employee_service.verify_employee_exists(
        attendance.employee_id
    )
    if not employee_exists:
        logger.warning(
            f"Manual attendance creation attempted for non-existent employee {attendance.employee_id}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Employee {attendance.employee_id} does not exist",
        )

    # Validate date format
    try:
        datetime.fromisoformat(attendance.date)
    except ValueError:
        logger.warning(f"Invalid date format: {attendance.date}")
        raise HTTPException(
            status_code=400,
            detail="Date must be in YYYY-MM-DD format",
        )

    logger.info(
        f"Creating manual attendance for employee {attendance.employee_id} on {attendance.date}"
    )
    db_attendance = Attendance.model_validate(attendance)
    session.add(db_attendance)
    session.commit()
    session.refresh(db_attendance)
    logger.info(f"Manual attendance created successfully with ID: {db_attendance.id}")
    return db_attendance


@router.get("/{attendance_id}", response_model=AttendancePublic)
def get_attendance(attendance_id: int, session: SessionDep) -> Attendance:
    """
    Get a specific attendance record by ID.

    Args:
        attendance_id: The ID of the attendance record to retrieve
        session: Database session (injected)

    Returns:
        Attendance record data

    Raises:
        HTTPException: 404 if attendance record not found
    """
    logger.info(f"Fetching attendance record with ID: {attendance_id}")
    record = session.get(Attendance, attendance_id)
    if not record:
        logger.warning(f"Attendance record with ID {attendance_id} not found")
        raise HTTPException(status_code=404, detail="Attendance record not found")
    logger.info(f"Attendance record found: {record.id}")
    return record


@router.get("/employee/{employee_id}", response_model=list[AttendancePublic])
def get_employee_attendance(
    employee_id: int,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[Attendance]:
    """
    Get all attendance records for a specific employee.
    Supports date range filtering for better query control.

    Args:
        employee_id: The ID of the employee
        session: Database session (injected)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format

    Returns:
        List of attendance records for the employee

    Raises:
        HTTPException: 400 if date format is invalid
    """
    logger.info(
        f"Fetching attendance records for employee {employee_id} "
        f"(offset={offset}, limit={limit})"
    )

    statement = select(Attendance).where(Attendance.employee_id == employee_id)

    # Apply date range filters if provided
    if start_date:
        try:
            datetime.fromisoformat(start_date)
            statement = statement.where(Attendance.date >= start_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="start_date must be in YYYY-MM-DD format",
            )

    if end_date:
        try:
            datetime.fromisoformat(end_date)
            statement = statement.where(Attendance.date <= end_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="end_date must be in YYYY-MM-DD format",
            )

    statement = statement.offset(offset).limit(limit)
    records = session.exec(statement).all()
    logger.info(
        f"Retrieved {len(records)} attendance record(s) for employee {employee_id}"
    )
    return list(records)


@router.put("/{attendance_id}", response_model=AttendancePublic)
def update_attendance(
    attendance_id: int, attendance: AttendanceUpdate, session: SessionDep
) -> Attendance:
    """
    Update an existing attendance record.

    Args:
        attendance_id: The ID of the attendance record to update
        attendance: Fields to update (only provided fields will be updated)
        session: Database session (injected)

    Returns:
        Updated attendance record

    Raises:
        HTTPException: 404 if attendance record not found, 400 if validation fails
    """
    logger.info(f"Attempting to update attendance record with ID: {attendance_id}")
    record = session.get(Attendance, attendance_id)
    if not record:
        logger.warning(
            f"Attendance record with ID {attendance_id} not found for update"
        )
        raise HTTPException(status_code=404, detail="Attendance record not found")

    # If employee_id is being updated, verify it exists
    if attendance.employee_id and attendance.employee_id != record.employee_id:
        employee_exists = employee_service.verify_employee_exists(
            attendance.employee_id
        )
        if not employee_exists:
            logger.warning(
                f"Update attempted with non-existent employee {attendance.employee_id}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Employee {attendance.employee_id} does not exist",
            )

    # Validate date format if being updated
    if attendance.date:
        try:
            datetime.fromisoformat(attendance.date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Date must be in YYYY-MM-DD format",
            )

    attendance_data = attendance.model_dump(exclude_unset=True)
    attendance_data["updated_at"] = datetime.utcnow()
    logger.info(f"Updating attendance {attendance_id} with data: {attendance_data}")
    record = record.sqlmodel_update(attendance_data)
    session.add(record)
    session.commit()
    session.refresh(record)
    logger.info(f"Attendance record with ID {attendance_id} updated successfully")
    return record


@router.get("/summary/{employee_id}/{month}", response_model=MonthlySummary)
def get_monthly_summary(
    employee_id: int, month: str, session: SessionDep
) -> MonthlySummary:
    """
    Get monthly attendance summary for a specific employee.
    Provides aggregated statistics for the specified month.

    Args:
        employee_id: The ID of the employee
        month: Month in YYYY-MM format
        session: Database session (injected)

    Returns:
        Monthly attendance summary with statistics and records

    Raises:
        HTTPException: 400 if month format is invalid
    """
    logger.info(f"Fetching monthly summary for employee {employee_id}, month {month}")

    # Validate month format
    try:
        datetime.fromisoformat(f"{month}-01")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Month must be in YYYY-MM format",
        )

    # Get all records for the month
    start_date = f"{month}-01"
    # Calculate last day of month
    first_of_month = datetime.fromisoformat(f"{month}-01")
    if first_of_month.month == 12:
        last_of_month = datetime(first_of_month.year + 1, 1, 1) - timedelta(days=1)
    else:
        last_of_month = datetime(
            first_of_month.year, first_of_month.month + 1, 1
        ) - timedelta(days=1)
    end_date = last_of_month.date().isoformat()

    statement = select(Attendance).where(
        (Attendance.employee_id == employee_id)
        & (Attendance.date >= start_date)
        & (Attendance.date <= end_date)
    )
    records = session.exec(statement).all()

    # Calculate statistics
    present_count = sum(1 for r in records if r.status == "present")
    absent_count = sum(1 for r in records if r.status == "absent")
    late_count = sum(1 for r in records if r.status == "late")

    # Calculate total working hours
    total_hours = 0.0
    for record in records:
        if record.check_in_time and record.check_out_time:
            duration = record.check_out_time - record.check_in_time
            total_hours += duration.total_seconds() / 3600

    logger.info(
        f"Monthly summary for employee {employee_id}: "
        f"{present_count} present, {absent_count} absent, {late_count} late"
    )

    return MonthlySummary(
        employee_id=employee_id,
        month=month,
        total_days_worked=present_count,
        total_present=present_count,
        total_absent=absent_count,
        total_late=late_count,
        working_hours=total_hours,
        records=[AttendancePublic.model_validate(r) for r in records],
    )


@router.get("/health", tags=["health"])
def attendance_health_check() -> dict:
    """
    Health check endpoint for attendance service.
    Verifies that the service is running and responsive.

    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "service": "attendance-management-service",
        "timestamp": datetime.utcnow().isoformat(),
    }
