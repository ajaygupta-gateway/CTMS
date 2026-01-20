# Import all schemas here for easy access
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    Token,
    TokenPayload,
    EmailVerificationRequest,
    EmailVerificationResponse,
    RegisterResponse,
)
from app.schemas.task import (
    TagBase,
    TagCreate,
    TagResponse,
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    BulkUpdateRequest,
    BulkUpdateResponse,
    TaskHistoryResponse,
)
from app.schemas.analytics import TaskAnalytics, AnalyticsResponse
from app.schemas.notification import NotificationResponse

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "Token",
    "TokenPayload",
    "EmailVerificationRequest",
    "EmailVerificationResponse",
    "RegisterResponse",
    # Task schemas
    "TagBase",
    "TagCreate",
    "TagResponse",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "BulkUpdateRequest",
    "BulkUpdateResponse",
    "TaskHistoryResponse",
    # Analytics schemas
    "TaskAnalytics",
    "AnalyticsResponse",
    # Notification schemas
    "NotificationResponse",
]
