from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.course import Unit, Course
from app.models.user import User
from app.schemas.course_schema import UnitCreate, UnitUpdate, UnitResponse


router = APIRouter(prefix="/units", tags=["Units"])


@router.get("/", response_model=List[UnitResponse])
def list_units(
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Unit).filter(Unit.is_active == True)

    if course_id:
        query = query.filter(Unit.course_id == course_id)

    return query.order_by(Unit.order).offset(skip).limit(limit).all()


@router.post("/", response_model=UnitResponse, status_code=201)
def create_unit(
    data: UnitCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    course = db.query(Course).filter(Course.id == data.course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    unit = Unit(**data.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)

    return unit


@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    return unit


@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: int,
    data: UnitUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(unit, field, value)

    db.commit()
    db.refresh(unit)

    return unit


@router.delete("/{unit_id}")
def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    unit.is_active = False
    db.commit()

    return {"message": "Unit deleted"}