"""
Notification API routes.
Handles all operations for notification resources including sending and retrieving notifications.
"""

from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from sqlmodel import select, func, Session  # type: ignore

from app.api.deps import SessionDep
from app.models.notification import (
    Notification,
    NotificationCreate,
    NotificationPublic,
    NotificationUpdate,
    NotificationListResponse,
    NotificationStatus,
)
from app.core.logging import get_logger
from app.core.database import get_session
from app.services.email import send_notification_email

logger = get_logger(__name__)

# Create router with prefix and tags for better organization
router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Notification not found"}},
)


async def send_email_background(
    notification_id: int,
    recipient_email: str,
    recipient_name: str,
    subject: str,
    body: str,
) -> None:
    """
    Background task to send email and update notification status.

    Args:
        notification_id: ID of the notification
        recipient_email: Email address of recipient
        recipient_name: Name of recipient
        subject: Email subject
        body: Email body
    """
    session_gen = get_session()
    session = next(session_gen)

    try:
        success = await send_notification_email(
            to_email=recipient_email,
            to_name=recipient_name,
            subject=subject,
            body=body,
        )

        notification = session.get(Notification, notification_id)
        if notification:
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                logger.info(f"Notification {notification_id} sent successfully")
            else:
                notification.retry_count += 1
                if notification.retry_count >= 3:
                    notification.status = NotificationStatus.FAILED
                    notification.error_message = "Max retries exceeded"
                    logger.error(
                        f"Notification {notification_id} failed after max retries"
                    )
                else:
                    notification.status = NotificationStatus.RETRYING
                    notification.error_message = "Email send failed, will retry"
                    logger.warning(
                        f"Notification {notification_id} will be retried (attempt {notification.retry_count})"
                    )
            notification.updated_at = datetime.utcnow()
            session.add(notification)
            session.commit()
    except Exception as e:
        logger.error(
            f"Error in background email task for notification {notification_id}: {str(e)}"
        )
        try:
            notification = session.get(Notification, notification_id)
            if notification:
                notification.status = NotificationStatus.FAILED
                notification.error_message = str(e)
                notification.retry_count += 1
                notification.updated_at = datetime.utcnow()
                session.add(notification)
                session.commit()
        except Exception as db_error:
            logger.error(f"Failed to update notification status: {str(db_error)}")
    finally:
        session.close()


@router.post("/send", response_model=NotificationPublic, status_code=201)
async def send_notification(
    notification: NotificationCreate,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> Notification:
    """
    Send a new notification.

    Args:
        notification: Notification data from request body
        session: Database session (injected)
        background_tasks: FastAPI background tasks

    Returns:
        Created notification with generated ID
    """
    logger.info(
        f"Creating new notification for employee {notification.employee_id} to {notification.recipient_email}"
    )

    # Create notification in database
    db_notification = Notification.model_validate(notification)
    db_notification.status = NotificationStatus.PENDING
    db_notification.created_at = datetime.utcnow()
    db_notification.updated_at = datetime.utcnow()
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)

    logger.info(f"Notification {db_notification.id} created successfully")

    # Add background task to send email
    background_tasks.add_task(
        send_email_background,
        notification_id=db_notification.id,
        recipient_email=notification.recipient_email,
        recipient_name=notification.recipient_name,
        subject=notification.subject,
        body=notification.body,
    )

    return db_notification


@router.get("/{notification_id}", response_model=NotificationPublic)
def get_notification(notification_id: int, session: SessionDep) -> Notification:
    """
    Retrieve a single notification by ID.

    Args:
        notification_id: The ID of the notification to retrieve
        session: Database session (injected)

    Returns:
        Notification data

    Raises:
        HTTPException: 404 if notification not found
    """
    logger.info(f"Fetching notification with ID: {notification_id}")
    notification = session.get(Notification, notification_id)
    if not notification:
        logger.warning(f"Notification with ID {notification_id} not found")
        raise HTTPException(status_code=404, detail="Notification not found")
    logger.info(f"Notification {notification_id} found")
    return notification


@router.get("/employee/{employee_id}", response_model=NotificationListResponse)
def get_employee_notifications(
    employee_id: int,
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: Annotated[int, Query(le=100)] = 100,
) -> NotificationListResponse:
    """
    Retrieve all notifications for a specific employee with pagination.

    Args:
        employee_id: The ID of the employee
        session: Database session (injected)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)

    Returns:
        List of notifications with pagination info
    """
    logger.info(
        f"Fetching notifications for employee {employee_id} with offset={offset}, limit={limit}"
    )

    # Get total count
    total = session.exec(
        select(func.count(Notification.id)).where(
            Notification.employee_id == employee_id
        )
    ).first()

    # Get paginated results
    notifications = session.exec(
        select(Notification)
        .where(Notification.employee_id == employee_id)
        .offset(offset)
        .limit(limit)
    ).all()

    logger.info(
        f"Retrieved {len(notifications)} notification(s) for employee {employee_id}"
    )

    return NotificationListResponse(
        total=total or 0,
        offset=offset,
        limit=limit,
        items=list(notifications),
    )


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: Annotated[int, Query(le=100)] = 100,
    status: str | None = Query(None),
) -> NotificationListResponse:
    """
    List all notifications with optional filtering and pagination.

    Args:
        session: Database session (injected)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        status: Filter by notification status (optional)

    Returns:
        List of notifications with pagination info
    """
    logger.info(
        f"Fetching notifications with offset={offset}, limit={limit}, status={status}"
    )

    # Build query
    query = select(Notification)
    if status:
        try:
            # Validate status enum
            NotificationStatus(status)
            query = query.where(Notification.status == status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    # Get total count
    count_query = select(func.count(Notification.id))
    if status:
        count_query = count_query.where(Notification.status == status)
    total = session.exec(count_query).first()

    # Get paginated results
    notifications = session.exec(query.offset(offset).limit(limit)).all()

    logger.info(f"Retrieved {len(notifications)} notification(s)")

    return NotificationListResponse(
        total=total or 0,
        offset=offset,
        limit=limit,
        items=list(notifications),
    )


@router.put("/{notification_id}/retry", response_model=NotificationPublic)
async def retry_notification(
    notification_id: int,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> Notification:
    """
    Retry sending a failed notification.

    Args:
        notification_id: The ID of the notification to retry
        session: Database session (injected)
        background_tasks: FastAPI background tasks

    Returns:
        Updated notification data

    Raises:
        HTTPException: 404 if notification not found
    """
    logger.info(f"Attempting to retry notification with ID: {notification_id}")
    notification = session.get(Notification, notification_id)
    if not notification:
        logger.warning(f"Notification with ID {notification_id} not found for retry")
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.status not in [
        NotificationStatus.FAILED,
        NotificationStatus.RETRYING,
    ]:
        logger.warning(
            f"Cannot retry notification {notification_id} with status {notification.status}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry notification with status {notification.status}",
        )

    notification.status = NotificationStatus.RETRYING
    notification.updated_at = datetime.utcnow()
    session.add(notification)
    session.commit()
    session.refresh(notification)

    logger.info(f"Notification {notification_id} marked for retry")

    # Add background task to send email
    background_tasks.add_task(
        send_email_background,
        notification_id=notification_id,
        recipient_email=notification.recipient_email,
        recipient_name=notification.recipient_name,
        subject=notification.subject,
        body=notification.body,
    )

    return notification
