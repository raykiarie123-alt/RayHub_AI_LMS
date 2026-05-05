from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ProgressUpdateRequest(BaseModel):
    topic_id: Optional[int] = None
    unit_id: Optional[int] = None
    course_id: Optional[int] = None
    study_time_minutes: Optional[int] = 0
    is_completed: Optional[bool] = False


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    course_id: Optional[int] = None
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None
    is_completed: bool
    completion_percentage: float
    study_time_minutes: int
    quiz_attempts_count: int
    best_quiz_score: float
    average_quiz_score: float
    last_studied_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WeakAreaResponse(BaseModel):
    topic_id: int
    topic_title: str
    unit_title: str
    average_score: float
    attempts: int


class RecommendationResponse(BaseModel):
    type: str  # topic, quiz, resource, flashcard
    title: str
    reason: str
    reference_id: Optional[int] = None