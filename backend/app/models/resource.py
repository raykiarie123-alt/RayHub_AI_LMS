from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(50), nullable=False)  # pdf, text, youtube, website, past_paper
    file_path = Column(String(500), nullable=True)
    url = Column(String(1000), nullable=True)
    content_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    is_indexed = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)

    # Foreign keys
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    uploader = relationship("User", back_populates="resources")
    course = relationship("Course", back_populates="resources")
    unit = relationship("Unit", back_populates="resources")
    topic = relationship("Topic", back_populates="resources")
    chunks = relationship("ResourceChunk", back_populates="resource", cascade="all, delete-orphan")
    rag_chats = relationship("RAGChat", back_populates="resource")


class ResourceChunk(Base):
    __tablename__ = "resource_chunks"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_id = Column(String(255), nullable=True)  # ID in FAISS index
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resource = relationship("Resource", back_populates="chunks")