from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from app.models.resource import Resource
from app.models.user import User
from app.schemas.resource_schema import ResourceCreate


def get_resources(
    db: Session,
    user: User,
    course_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Resource]:
    query = db.query(Resource)
    if user.role == "student":
        query = query.filter(Resource.is_approved == True)
    if course_id:
        query = query.filter(Resource.course_id == course_id)
    if unit_id:
        query = query.filter(Resource.unit_id == unit_id)
    if topic_id:
        query = query.filter(Resource.topic_id == topic_id)
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    return query.order_by(Resource.created_at.desc()).offset(skip).limit(limit).all()


def get_resource_by_id(db: Session, resource_id: int) -> Resource:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


def delete_resource(db: Session, resource_id: int, user: User):
    resource = get_resource_by_id(db, resource_id)
    if resource.uploader_id != user.id and user.role not in ("admin", "tutor"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this resource")
    db.delete(resource)
    db.commit()