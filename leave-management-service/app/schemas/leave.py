"""
Leave Pydantic schemas.
Defines request/response models for Leave API endpoints.
Separates API contracts from database models for better flexibility.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime

from app.models.leave import LeaveType, LeaveStatus


class LeaveBase(SQLModel):
    """
    Base leave schema with shared fields.
    Used as foundation for other leave schemas.
    """

    employee_id: int = Field(gt=0)
    leave_type: LeaveType = Field(default=LeaveType.ANNUAL)
    start_date: datetime
    end_date: datetime
    reason: str | None = Field(default=None, max_length=500)


class LeaveCreate(LeaveBase):
    """
    Schema for creating a new leave request.
    Inherits all required fields from LeaveBase.
    """

    pass


class LeaveStatusUpdate(SQLModel):
    """
    Schema for updating leave status.
    Used for approval and rejection workflows.
    """

    status: LeaveStatus
    rejection_reason: str | None = Field(default=None, max_length=500)
    approved_by: int | None = None


class LeavePublic(LeaveBase):
    """
    Schema for leave responses.
    Includes all fields returned to clients.
    """

    id: int
    status: LeaveStatus = Field(default=LeaveStatus.PENDING)
    approved_by: int | None = None
    rejection_reason: str | None = None
    created_at: datetime
    updated_at: datetime
