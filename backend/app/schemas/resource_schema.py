from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    resource_type: str
    url: Optional[str] = None
    course_id: Optional[int] = None
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None
    is_public: Optional[bool] = True


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_approved: Optional[bool] = None


class ResourceResponse(ResourceBase):
    id: int
    is_indexed: bool
    is_approved: bool
    summary: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class YouTubeIngestRequest(BaseModel):
    url: str
    title: Optional[str] = None
    course_id: Optional[int] = None
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None


class WebIngestRequest(BaseModel):
    url: str
    title: Optional[str] = None
    course_id: Optional[int] = None
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None