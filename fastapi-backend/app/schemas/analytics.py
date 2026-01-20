from pydantic import BaseModel
from typing import Dict, Any


class TaskAnalytics(BaseModel):
    """Schema for task analytics"""
    total: int
    completed: int
    pending: int = 0
    in_progress: int = 0


class AnalyticsResponse(BaseModel):
    """Schema for analytics response"""
    my_tasks: TaskAnalytics
    team_tasks: Dict[str, int]
    efficiency_score: float
