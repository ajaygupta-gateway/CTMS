from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.task import Task, Tag, TaskStatus, TaskPriority
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    BulkUpdateRequest,
    BulkUpdateResponse,
)
from app.api.dependencies import (
    get_current_verified_user,
    require_working_hours_for_developers,
    check_working_hours,
)
from datetime import datetime

router = APIRouter()


def can_access_task(user: User, task: Task) -> bool:
    """Check if user can access a task"""
    if user.is_auditor() or user.is_manager():
        return True
    if user.is_developer():
        return task.assigned_to_id == user.id
    return False


def can_modify_task(user: User, task: Task) -> bool:
    """Check if user can modify a task (considering time restrictions)"""
    if user.is_auditor():
        return False  # Auditors are read-only
    
    if user.is_manager():
        return True  # Managers can modify anytime
    
    if user.is_developer():
        # Check if task is assigned to user
        if task.assigned_to_id != user.id:
            return False
        
        # Critical tasks can be modified anytime
        if task.priority == TaskPriority.CRITICAL:
            return True
        
        # Otherwise, check working hours
        return check_working_hours(user)
    
    return False


async def build_task_response(task: Task, db: AsyncSession) -> dict:
    """Build task response with additional fields"""
    # Load relationships if not already loaded
    await db.refresh(task, ["assigned_to_user", "created_by_user", "tags"])
    
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "deadline": task.deadline,
        "priority_escalated": task.priority_escalated,
        "assigned_to": task.assigned_to_id,
        "assigned_to_user": task.assigned_to_user.username,
        "created_by": task.created_by_id,
        "created_by_user": task.created_by_user.username,
        "parent_task": task.parent_task_id,
        "tags": [tag.id for tag in task.tags],
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """List tasks based on role permissions"""
    
    query = select(Task).options(
        selectinload(Task.assigned_to_user),
        selectinload(Task.created_by_user),
        selectinload(Task.tags)
    )
    
    if current_user.is_developer():
        # Developers only see their assigned tasks
        query = query.where(Task.assigned_to_id == current_user.id)
    # Managers and auditors see all tasks
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Build responses
    task_responses = []
    for task in tasks:
        task_data = await build_task_response(task, db)
        task_responses.append(task_data)
    
    return task_responses


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task"""
    
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.assigned_to_user),
            selectinload(Task.created_by_user),
            selectinload(Task.tags)
        )
        .where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not can_access_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )
    
    return await build_task_response(task, db)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(require_working_hours_for_developers),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task"""
    
    # Auditors cannot create tasks
    if current_user.is_auditor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auditors cannot create tasks"
        )
    
    # Developers can only assign tasks to themselves
    if current_user.is_developer() and task_data.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developers can only assign tasks to themselves"
        )
    
    # Verify assigned user exists
    result = await db.execute(select(User).where(User.id == task_data.assigned_to))
    assigned_user = result.scalar_one_or_none()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )
    
    # Verify parent task exists if provided
    if task_data.parent_task:
        result = await db.execute(select(Task).where(Task.id == task_data.parent_task))
        parent_task = result.scalar_one_or_none()
        if not parent_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent task not found"
            )
    
    # Create task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        estimated_hours=task_data.estimated_hours,
        actual_hours=task_data.actual_hours,
        deadline=task_data.deadline,
        assigned_to_id=task_data.assigned_to,
        created_by_id=current_user.id,
        parent_task_id=task_data.parent_task,
    )
    db.add(task)
    await db.flush()
    
    # Add tags
    if task_data.tags:
        result = await db.execute(select(Tag).where(Tag.id.in_(task_data.tags)))
        tags = result.scalars().all()
        task.tags = tags
    
    await db.commit()
    await db.refresh(task)
    
    return await build_task_response(task, db)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a task"""
    
    # Get task
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.assigned_to_user),
            selectinload(Task.created_by_user),
            selectinload(Task.tags)
        )
        .where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not can_access_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )
    
    if not can_modify_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task at this time"
        )
    
    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "tags":
            # Handle tags separately
            if value is not None:
                result = await db.execute(select(Tag).where(Tag.id.in_(value)))
                tags = result.scalars().all()
                task.tags = tags
        elif field == "assigned_to":
            # Verify user exists
            result = await db.execute(select(User).where(User.id == value))
            assigned_user = result.scalar_one_or_none()
            if not assigned_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assigned user not found"
                )
            task.assigned_to_id = value
        elif field == "parent_task":
            # Verify parent task exists
            if value is not None:
                result = await db.execute(select(Task).where(Task.id == value))
                parent_task = result.scalar_one_or_none()
                if not parent_task:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Parent task not found"
                    )
            task.parent_task_id = value
        else:
            setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return await build_task_response(task, db)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task"""
    
    # Get task
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not can_access_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )
    
    if not can_modify_task(current_user, task):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task at this time"
        )
    
    await db.delete(task)
    await db.commit()
    
    return None


@router.post("/bulk-update", response_model=BulkUpdateResponse)
async def bulk_update_tasks(
    bulk_data: BulkUpdateRequest,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk update task status"""
    
    # Get all tasks
    result = await db.execute(
        select(Task).where(Task.id.in_(bulk_data.task_ids))
    )
    tasks = result.scalars().all()
    
    if len(tasks) != len(bulk_data.task_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some tasks not found"
        )
    
    # Check permissions for all tasks
    updated_count = 0
    for task in tasks:
        if not can_access_task(current_user, task):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to access task {task.id}"
            )
        
        if not can_modify_task(current_user, task):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to modify task {task.id} at this time"
            )
        
        # Update status
        task.status = bulk_data.status
        updated_count += 1
    
    await db.commit()
    
    return BulkUpdateResponse(updated_count=updated_count)
