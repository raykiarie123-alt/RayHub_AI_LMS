from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    exam_date = Column(Date, nullable=True)
    available_hours_per_day = Column(Float, default=3.0)
    selected_units = Column(JSON, nullable=True)
    weak_topics = Column(JSON, nullable=True)
    learning_style = Column(String(100), nullable=True)
    ai_generated_plan = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    completion_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="study_plans")
    tasks = relationship("StudyPlanTask", back_populates="study_plan", cascade="all, delete-orphan")


class StudyPlanTask(Base):
    __tablename__ = "study_plan_tasks"

    id = Column(Integer, primary_key=True, index=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(50), nullable=True)  # topic, quiz, flashcard, resource, revision
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    scheduled_date = Column(Date, nullable=True)
    week_number = Column(Integer, default=1)
    day_number = Column(Integer, default=1)
    estimated_hours = Column(Float, default=1.0)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    study_plan = relationship("StudyPlan", back_populates="tasks")