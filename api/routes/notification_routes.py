from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from api.schemas.appointment_schemas import NotificationResponse, NotificationList, NotificationCreate
from services.notification_service import NotificationService
from db.session import get_db
from api.dependencies.auth import get_current_user_id, get_current_user_type

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=NotificationList)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_type: str = Depends(get_current_user_type)
):
    """
    Get all notifications for the current user with pagination
    """
    notifications, total, unread_count = NotificationService.get_user_notifications(
        db, user_id, user_type, skip, limit
    )
    
    return {
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count
    }

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_type: str = Depends(get_current_user_type)
):
    """
    Mark a specific notification as read
    """
    notification = await NotificationService.mark_notification_as_read(db, notification_id)
    print(notification.user_type, user_type)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Check if notification belongs to the current user
    if notification.user_id != user_id or notification.user_type != user_type:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification"
        )
    
    return notification

@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_type: str = Depends(get_current_user_type)
):
    """
    Mark all notifications for the current user as read
    """
    updated_count = NotificationService.mark_all_notifications_as_read(db, user_id, user_type)
    
    return {"message": f"{updated_count} notifications marked as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    user_type: str = Depends(get_current_user_type)
):
    """
    Delete a specific notification
    """
    notification = NotificationService.get_notification_by_id(db, notification_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != user_id or notification.user_type != user_type:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification"
        )

    await NotificationService.delete_notification(db, notification_id)
    return  # 204 No Content
