from datetime import datetime, timedelta
from app.models import UserPoints, UserStreak, UserBadge

def award_points(db, user_id, points):
    record = db.query(UserPoints).filter(UserPoints.user_id == user_id).first()
    if not record:
        record = UserPoints(user_id=user_id, points=points)
        db.add(record)
    else:
        record.points += points
    db.commit() 
    return record.points

def update_streak(db, user_id):
    record = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
    today = datetime.today().date()

    if not record:
        record = UserStreak(user_id=user_id, current_streak=1, last_active_date=today)
        db.add(record)
    else:
        if record.last_active_date == today - timedelta(days=1):
            record.current_streak += 1
        elif record.last_active_date < today - timedelta(days=1):
            record.current_streak = 1
        record.last_active_date = today

    db.commit()
    return record.current_streak