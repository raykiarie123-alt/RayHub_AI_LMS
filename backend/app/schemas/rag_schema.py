from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class RAGAskRequest(BaseModel):
    question: str
    resource_id: Optional[int] = None
    topic_id: Optional[int] = None
    top_k: Optional[int] = 5


class RAGSource(BaseModel):
    resource_title: str
    chunk_id: int
    chunk_text: Optional[str] = None


class RAGAskResponse(BaseModel):
    answer: str
    sources: Optional[List[RAGSource]] = []
    question: str


class RAGChatResponse(BaseModel):
    id: int
    question: str
    answer: Optional[str] = None
    sources: Optional[Any] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True