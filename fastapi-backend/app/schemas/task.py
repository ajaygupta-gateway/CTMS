from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.task import TaskStatus, TaskPriority


# Tag Schemas
class TagBase(BaseModel):
    """Base tag schema"""
    name: str = Field(..., min_length=1, max_length=50)


class TagCreate(TagBase):
    """Schema for tag creation"""
    pass


class TagResponse(TagBase):
    """Schema for tag response"""
    id: int
    
    class Config:
        from_attributes = True


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_hours: Decimal = Field(..., ge=0, decimal_places=2)
    actual_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    deadline: datetime
    assigned_to: int
    parent_task: Optional[int] = None
    tags: List[int] = []


class TaskCreate(TaskBase):
    """Schema for task creation"""
    pass


class TaskUpdate(BaseModel):
    """Schema for task update (partial)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    estimated_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    actual_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    deadline: Optional[datetime] = None
    assigned_to: Optional[int] = None
    parent_task: Optional[int] = None
    tags: Optional[List[int]] = None


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    estimated_hours: Decimal
    actual_hours: Optional[Decimal]
    deadline: datetime
    priority_escalated: bool
    assigned_to: int
    assigned_to_user: str
    created_by: int
    created_by_user: str
    parent_task: Optional[int]
    tags: List[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Bulk Operations
class BulkUpdateRequest(BaseModel):
    """Schema for bulk status update"""
    task_ids: List[int] = Field(..., min_items=1)
    status: TaskStatus


class BulkUpdateResponse(BaseModel):
    """Schema for bulk update response"""
    updated_count: int


# Task History
class TaskHistoryResponse(BaseModel):
    """Schema for task history response"""
    id: int
    task_id: int
    action: str
    from_status: str
    to_status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
