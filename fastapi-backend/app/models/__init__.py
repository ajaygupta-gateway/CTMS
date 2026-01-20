# Import all models here for Alembic to detect them
from app.models.user import User, UserSession, EmailVerificationToken, UserRole
from app.models.task import Task, Tag, TaskHistory, TaskStatus, TaskPriority, task_tags
from app.models.notification import Notification, NotificationType
from app.models.audit import APIAuditLog

__all__ = [
    "User",
    "UserSession",
    "EmailVerificationToken",
    "UserRole",
    "Task",
    "Tag",
    "TaskHistory",
    "TaskStatus",
    "TaskPriority",
    "task_tags",
    "Notification",
    "NotificationType",
    "APIAuditLog",
]
