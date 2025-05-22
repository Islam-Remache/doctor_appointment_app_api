import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models.appointment_models import Notification, DeviceToken 
from api.schemas.appointment_schemas import NotificationCreate
from typing import List, Tuple, Optional
import httpx
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import json

class NotificationService:
    @staticmethod
    def get_notification_by_id(db: Session, notification_id: int):
        return db.query(Notification).filter(Notification.id == notification_id).first()
    
    @staticmethod
    async def send_push_notification(token: str, title: str, body: str):
        SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "admin.json")

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token

        # Construire l'appel FCM avec ce token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }

        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }

        response = requests.post(
            'https://fcm.googleapis.com/v1/projects/doctorappointmentapp-b2b59/messages:send',
            headers=headers,
            json=message
        )

        print("Status:", response.status_code)
        print("Response:", response.json())

    @staticmethod
    def get_user_fcm_token(db: Session, user_id: int) -> str | None:
        """Fetch the latest FCM token for a given user_id"""
        token_entry = (
            db.query(DeviceToken)
            .filter(DeviceToken.user_id == user_id)
            .order_by(DeviceToken.created_at.desc())
            .first()
        )
        return token_entry.token if token_entry else None
    
    @staticmethod
    async def create_notification(db: Session, notification: NotificationCreate) -> Notification:
        """Create a new notification in the database"""
        db_notification = Notification(
            user_id=notification.user_id,
            user_type=notification.user_type,
            title=notification.title,
            message=notification.message,
            type=notification.type  # must match the Enum
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        # Retrieve the user’s FCM token from DB
        token = NotificationService.get_user_fcm_token(db, notification.user_id)  # you must implement this

        if token:
            await NotificationService.send_push_notification(token, notification.title, notification.message)
        return db_notification
    
    @staticmethod
    def get_user_notifications(
        db: Session, user_id: int, user_type: str, 
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[Notification], int, int]:
        """Get notifications for a specific user with pagination"""
        # Query for notifications
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .filter(Notification.user_type == user_type)
            .order_by(Notification.sent_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Get total count
        total_count = (
            db.query(func.count(Notification.id))
            .filter(Notification.user_id == user_id)
            .filter(Notification.user_type == user_type)
            .scalar()
        )
        
        # Get unread count
        unread_count = (
            db.query(func.count(Notification.id))
            .filter(Notification.user_id == user_id)
            .filter(Notification.user_type == user_type)
            .filter(Notification.is_read == False)
            .scalar()
        )


        
        
        return notifications, total_count, unread_count
    
    @staticmethod
    def mark_notification_as_read(db: Session, notification_id: int) -> Optional[Notification]:
        """Mark a specific notification as read"""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        
        return notification
    
    @staticmethod
    def mark_all_notifications_as_read(db: Session, user_id: int, user_type: str) -> int:
        """Mark all notifications for a user as read and return count of updated records"""
        result = (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .filter(Notification.user_type == user_type)
            .filter(Notification.is_read == False)
            .update({"is_read": True})
        )
        db.commit()
        return result
    
    @staticmethod
    async def delete_notification(db: Session, notification_id: int):
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            db.delete(notification)
            db.commit()
        
        token = NotificationService.get_user_fcm_token(db, notification.user_id)  # you must implement this

        if token:
            await NotificationService.send_push_notification(token, "Notification deleted", "You just deleted a notification")




    

