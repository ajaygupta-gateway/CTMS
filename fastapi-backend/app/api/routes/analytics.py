from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.schemas.analytics import AnalyticsResponse, TaskAnalytics
from app.api.dependencies import get_current_verified_user

router = APIRouter()


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """Get task analytics and metrics"""
    
    # My tasks analytics
    my_tasks_query = select(Task).where(Task.assigned_to_id == current_user.id)
    result = await db.execute(my_tasks_query)
    my_tasks = result.scalars().all()
    
    my_total = len(my_tasks)
    my_completed = sum(1 for task in my_tasks if task.status == TaskStatus.COMPLETED)
    my_pending = sum(1 for task in my_tasks if task.status == TaskStatus.PENDING)
    my_in_progress = sum(1 for task in my_tasks if task.status == TaskStatus.IN_PROGRESS)
    
    # Team tasks analytics
    if current_user.is_developer():
        # Developers see their team tasks (same as my tasks for now)
        team_total = my_total
        team_completed = my_completed
    else:
        # Managers and auditors see all tasks
        all_tasks_query = select(Task)
        result = await db.execute(all_tasks_query)
        all_tasks = result.scalars().all()
        
        team_total = len(all_tasks)
        team_completed = sum(1 for task in all_tasks if task.status == TaskStatus.COMPLETED)
    
    # Calculate efficiency score
    # Formula: (completed_tasks / total_tasks) * 100 if total > 0
    if my_total > 0:
        completion_rate = (my_completed / my_total) * 100
        
        # Factor in time estimates vs actual hours
        total_estimated = sum(float(task.estimated_hours) for task in my_tasks if task.status == TaskStatus.COMPLETED)
        total_actual = sum(float(task.actual_hours) for task in my_tasks if task.status == TaskStatus.COMPLETED and task.actual_hours)
        
        if total_estimated > 0 and total_actual > 0:
            time_efficiency = min((total_estimated / total_actual) * 100, 100)
            efficiency_score = (completion_rate * 0.6) + (time_efficiency * 0.4)
        else:
            efficiency_score = completion_rate
    else:
        efficiency_score = 0.0
    
    return AnalyticsResponse(
        my_tasks=TaskAnalytics(
            total=my_total,
            completed=my_completed,
            pending=my_pending,
            in_progress=my_in_progress,
        ),
        team_tasks={
            "total": team_total,
            "completed": team_completed,
        },
        efficiency_score=round(efficiency_score, 2)
    )
