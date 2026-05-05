from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime, date


class StudyPlanGenerateRequest(BaseModel):
    exam_date: Optional[str] = None
    available_hours_per_day: Optional[float] = 3.0
    selected_units: Optional[List[str]] = []
    weak_topics: Optional[List[str]] = []
    learning_style: Optional[str] = "balanced"
    title: Optional[str] = None


class StudyPlanTaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    task_type: Optional[str] = None
    week_number: int
    day_number: int
    estimated_hours: float
    is_completed: bool
    scheduled_date: Optional[date] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudyPlanResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    exam_date: Optional[date] = None
    available_hours_per_day: float
    selected_units: Optional[Any] = None
    weak_topics: Optional[Any] = None
    learning_style: Optional[str] = None
    completion_percentage: float
    is_active: bool
    tasks: Optional[List[StudyPlanTaskResponse]] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompleteTaskRequest(BaseModel):
    task_id: int