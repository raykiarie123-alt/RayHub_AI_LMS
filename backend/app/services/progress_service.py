from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.models.progress import Progress
from app.models.user import User


def update_quiz_progress(db: Session, user_id: int, topic_id: int, score: float):
    """Update progress record after a quiz attempt."""
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.topic_id == topic_id
    ).first()

    if not progress:
        progress = Progress(user_id=user_id, topic_id=topic_id)
        db.add(progress)
        db.flush()

    progress.quiz_attempts_count += 1
    progress.best_quiz_score = max(progress.best_quiz_score, score)

    # Recalculate average
    total = (progress.average_quiz_score * (progress.quiz_attempts_count - 1)) + score
    progress.average_quiz_score = total / progress.quiz_attempts_count

    progress.last_studied_at = datetime.utcnow()
    db.commit()


def mark_topic_complete(db: Session, user_id: int, topic_id: int):
    """Mark a topic as completed."""
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.topic_id == topic_id
    ).first()

    if not progress:
        progress = Progress(user_id=user_id, topic_id=topic_id)
        db.add(progress)

    progress.is_completed = True
    progress.completion_percentage = 100.0
    progress.completed_at = datetime.utcnow()
    progress.last_studied_at = datetime.utcnow()
    db.commit()


def add_study_time(db: Session, user_id: int, topic_id: Optional[int], minutes: int):
    """Add study time to a progress record."""
    if not topic_id:
        return
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.topic_id == topic_id
    ).first()

    if not progress:
        progress = Progress(user_id=user_id, topic_id=topic_id)
        db.add(progress)

    progress.study_time_minutes += minutes
    progress.last_studied_at = datetime.utcnow()
    db.commit()


def get_weak_areas(db: Session, user_id: int):
    """Get topics where the user is performing poorly."""
    records = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.quiz_attempts_count > 0,
        Progress.average_quiz_score < 70
    ).all()

    weak_areas = []
    for p in records:
        if p.topic_id:
            from app.models.course import Topic, Unit
            topic = db.query(Topic).filter(Topic.id == p.topic_id).first()
            if topic:
                unit = db.query(Unit).filter(Unit.id == topic.unit_id).first()
                weak_areas.append({
                    "topic_id": p.topic_id,
                    "topic_title": topic.title,
                    "unit_title": unit.title if unit else "Unknown",
                    "average_score": p.average_quiz_score,
                    "attempts": p.quiz_attempts_count
                })
    return weak_areas