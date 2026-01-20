from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    STATUS_CHANGE = "status_change"
    DEADLINE_WARNING = "deadline_warning"
    TASK_ASSIGNED = "task_assigned"
    TASK_UNASSIGNED = "task_unassigned"


class Notification(Base):
    """Notification model for user notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    notification_type = Column(SQLEnum(NotificationType), default=NotificationType.STATUS_CHANGE, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    is_delivered = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    task = relationship("Task", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_created_at", "user_id", "created_at"),
        Index("idx_user_read", "user_id", "read"),
    )
