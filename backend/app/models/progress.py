from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    study_time_minutes = Column(Integer, default=0)
    quiz_attempts_count = Column(Integer, default=0)
    best_quiz_score = Column(Float, default=0.0)
    average_quiz_score = Column(Float, default=0.0)
    last_studied_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="progress_records")
    topic = relationship("Topic", back_populates="progress_records")