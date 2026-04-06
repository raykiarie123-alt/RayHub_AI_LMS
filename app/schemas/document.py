from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentResponse(BaseModel):
    id: int
    user_id: Optional[int]
    title: str
    file_name: str
    file_path: str
    source_type: str
    content_type: Optional[str]
    upload_status: str
    created_at: datetime

    class Config:
        from_attributes = True