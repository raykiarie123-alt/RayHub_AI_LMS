from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import UserStreak, UserBadge


def update_streak(db: Session, user_id: int):
    record = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
    today = datetime.utcnow().date()

    if not record:
        record = UserStreak(
            user_id=user_id,
            streak_count=1,
            last_active_date=today
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.streak_count

    last_date = record.last_active_date

    if last_date == today:
        return record.streak_count

    if last_date == today - timedelta(days=1):
        record.streak_count += 1
    else:
        record.streak_count = 1

    record.last_active_date = today
    db.commit()
    db.refresh(record)

    return record.streak_count

