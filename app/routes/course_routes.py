from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Course
from app.schemas.schemas import CourseCreate

router = APIRouter()

@router.post("/courses/", response_model=CourseCreate)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = Course(
        name=course.name, 
        description=course.description
        )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course

@router.get("/courses/")
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return courses

from app.models.models import Level
from app.schemas.schemas import LevelCreate


@router.post("/levels")
def create_level(level: LevelCreate, db: Session = Depends(get_db)):

    new_level = Level(
        name=level.name,
        price=level.price,
        course_id=level.course_id
    )

    db.add(new_level)
    db.commit()
    db.refresh(new_level)

    return new_level

from app.models.models import Unit
from app.schemas.schemas import UnitCreate


@router.post("/units")
def create_unit(unit: UnitCreate, db: Session = Depends(get_db)):

    new_unit = Unit(
        name=unit.name,
        description=unit.description,
        level_id=unit.level_id
    )

    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)

    return new_unit


from app.models.models import Topic
from app.schemas.schemas import TopicCreate


@router.post("/topics")
def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):

    new_topic = Topic(
        title=topic.title,
        content=topic.content,
        video_url=topic.video_url,
        unit_id=topic.unit_id
    )

    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    return new_topic
