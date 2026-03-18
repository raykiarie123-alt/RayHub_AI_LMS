from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_service import generate_study_plan
from typing import List
from app.schemas.ai_schema import StudyPlanDay



router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/study-plan")
def get_study_plan(db: Session = Depends(get_db)):
    user_id = 1

    return generate_study_plan(db, user_id)
