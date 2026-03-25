from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.notification_service import get_notifications
router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def get_user_notifications(db: Session = Depends(get_db)):
    user_id = 1 #temporary until JWT integration

    notifications = get_notifications(db, user_id)

    return notifications