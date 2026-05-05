from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LevelBase(BaseModel):
    name: str
    description: Optional[str] = None
    order: Optional[int] = 0


class LevelCreate(LevelBase):
    pass


class LevelResponse(LevelBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    level_id: Optional[int] = None
    thumbnail_url: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    level_id: Optional[int] = None
    thumbnail_url: Optional[str] = None
    is_active: Optional[bool] = None


class CourseResponse(CourseBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UnitBase(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: int
    order: Optional[int] = 0


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class UnitResponse(UnitBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    unit_id: int
    order: Optional[int] = 0
    estimated_hours: Optional[int] = 1


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    estimated_hours: Optional[int] = None
    is_active: Optional[bool] = None


class TopicResponse(TopicBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True