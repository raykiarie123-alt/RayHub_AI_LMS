from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
user = relationship("User", back_populates="documents")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    source_type = Column(String, nullable=False, default="student_upload")
    content_type = Column(String, nullable=True)
    upload_status = Column(String, nullable=False, default="uploaded")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

