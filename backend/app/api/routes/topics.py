from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.course_schema import TopicCreate, TopicUpdate, TopicResponse
from app.models.course import Topic
from app.models.user import User

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("/", response_model=List[TopicResponse])
def list_topics(
    unit_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(Topic).filter(Topic.is_active == True)
    if unit_id:
        query = query.filter(Topic.unit_id == unit_id)
    return query.order_by(Topic.order).all()


@router.post("/", response_model=TopicResponse, status_code=201)
def create_topic(
    data: TopicCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    topic = Topic(**data.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.put("/{topic_id}", response_model=TopicResponse)
def update_topic(
    topic_id: int,
    data: TopicUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(topic, field, value)
    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/{topic_id}")
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    db.delete(topic)
    db.commit()
    return {"message": "Topic deleted"}


