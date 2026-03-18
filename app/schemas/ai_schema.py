from pydantic import BaseModel
from typing import List

class Task(BaseModel):
    topic: str
    activity: str

class StudyPlanDay(BaseModel):
    date: str
    tasks: List[Task]