from pydantic import BaseModel
from datetime import datetime
from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: int
    user_id: int
    task_id: int
    message: str
    notification_type: NotificationType
    read: bool
    is_delivered: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
