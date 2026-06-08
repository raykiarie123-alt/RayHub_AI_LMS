from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.course_schema import CourseCreate, CourseUpdate, CourseResponse, LevelCreate, LevelResponse
from app.models.course import Course, Level
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])
levels_router = APIRouter(prefix="/levels", tags=["Levels"])


# ─── Levels ───────────────────────────────────────────────────────────────────

@levels_router.get("/", response_model=List[LevelResponse])
def list_levels(db: Session = Depends(get_db)):
    return db.query(Level).order_by(Level.order).all()


@levels_router.post("/", response_model=LevelResponse, status_code=201)
def create_level(
    data: LevelCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    level = Level(**data.model_dump())
    db.add(level)
    db.commit()
    db.refresh(level)
    return level


@levels_router.get("/{level_id}", response_model=LevelResponse)
def get_level(level_id: int, db: Session = Depends(get_db)):
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    return level


# ─── Courses ──────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[CourseResponse])
def list_courses(
    skip: int = 0,
    limit: int = 50,
    level_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(Course).filter(Course.is_active == True)
    if level_id:
        query = query.filter(Course.level_id == level_id)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=CourseResponse, status_code=201)
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    course = Course(**data.model_dump(), created_by=admin.id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"message": "Course deleted"}


@router.get("/{course_id}/resources")
def get_course_resources(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all resources associated with a course (by course_id or matching level)."""
    from app.models.resource import Resource

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Resources explicitly linked to this course
    direct = db.query(Resource).filter(Resource.course_id == course_id).all()

    # Resources linked by level (uploaded by students at this level)
    level = db.query(Level).filter(Level.id == course.level_id).first()
    level_name = (level.name if level else "Foundation").lower().replace("-", "").replace(" ", "")
    # Map level names to the level column in resources
    level_map = {
        "foundation": "foundation",
        "intermediate": "intermediate",
        "advanced": "advanced",
        "postqualification": "post-qualification",
    }
    resource_level = level_map.get(level_name, "foundation")

    level_resources = (
        db.query(Resource)
        .filter(Resource.level == resource_level, Resource.course_id.is_(None))
        .order_by(Resource.created_at.desc())
        .limit(30)
        .all()
    )

    all_resources = {r.id: r for r in direct + level_resources}.values()

    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "resource_type": r.resource_type,
            "level": r.level,
            "url": r.url,
            "file_path": r.file_path,
            "is_indexed": r.is_indexed,
            "uploader_id": r.uploader_id,
            "created_at": r.created_at,
        }
        for r in all_resources
    ]