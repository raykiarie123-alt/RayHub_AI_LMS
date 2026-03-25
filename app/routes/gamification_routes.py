from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserStreaks

router = APIRouter(prefix="/gamification", tags=["Gamification"])
@router.get("/streak")
def get_user_streak(db: Session = Depends(get_db)):
    user_id = 1 #temporary until JWT integration

    streak = db.query(UserStreaks).filter(UserStreaks.user_id == user_id).first()
    if not streak:
        return {"streak_count": 0}

    return {"streak_count": streak.streak_count if streak else 0}