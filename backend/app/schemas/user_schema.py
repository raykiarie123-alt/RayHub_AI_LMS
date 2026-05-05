from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: Optional[str] = "student"
    cpa_level: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    available_hours_per_day: Optional[int] = 3


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    cpa_level: Optional[str] = None
    available_hours_per_day: Optional[int] = None
    exam_date: Optional[datetime] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True