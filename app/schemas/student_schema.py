from pydantic import BaseModel
from datetime import date, time

class StudentProfileCreate(BaseModel):
    study_hours_per_day: int
    preferred_learning_style: str | None = None
    target_exam_date: date
    daily_reminder_time: time | None = None


class StudentProfileUpdate(BaseModel):
    study_hours_per_day: int | None = None
    preferred_learning_style: str | None = None
    target_exam_date: date | None = None
    daily_reminder_time: time | None = None


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    study_hours_per_day: int
    preferred_learning_style: str | None
    target_exam_date: date
    daily_reminder_time: time | None

    class Config:
        from_attributes = True

class TopicMasteryResponse(BaseModel):
    topic_id: int
    average_score: float
    attempts: int
    mastery_level: str

    class Config:
        from_attributes = True