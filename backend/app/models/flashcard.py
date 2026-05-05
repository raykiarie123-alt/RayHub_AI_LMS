from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    is_ai_generated = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    review_count = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)  # Spaced repetition
    interval_days = Column(Integer, default=1)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", back_populates="flashcards")
    topic = relationship("Topic", back_populates="flashcards")
    