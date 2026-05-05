from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.progress import Progress
from app.models.user import User
from app.schemas.progress_schema import ProgressUpdateRequest, ProgressResponse, WeakAreaResponse, RecommendationResponse
from app.services.progress_service import mark_topic_complete, add_study_time, get_weak_areas
from app.services.gamification_service import add_xp, update_streak, check_and_award_badges

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/me", response_model=List[ProgressResponse])
def get_my_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all progress records for the current user."""
    return db.query(Progress).filter(Progress.user_id == current_user.id).all()


@router.get("/course/{course_id}", response_model=List[ProgressResponse])
def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for a specific course."""
    return db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.course_id == course_id
    ).all()


@router.get("/unit/{unit_id}", response_model=List[ProgressResponse])
def get_unit_progress(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for a specific unit."""
    return db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.unit_id == unit_id
    ).all()


@router.post("/update")
def update_progress(
    data: ProgressUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update study progress."""
    if data.study_time_minutes and data.study_time_minutes > 0:
        add_study_time(db, current_user.id, data.topic_id, data.study_time_minutes)

    if data.is_completed and data.topic_id:
        mark_topic_complete(db, current_user.id, data.topic_id)
        add_xp(db, current_user.id, 10, "Completed a topic", "topic", data.topic_id)

    # Update streak
    update_streak(db, current_user.id)
    check_and_award_badges(db, current_user.id)

    return {"message": "Progress updated"}


@router.get("/weak-areas")
def get_weak_areas_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the user's weak areas based on quiz performance."""
    return get_weak_areas(db, current_user.id)


@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized study recommendations."""
    from app.services.ai.recommendation_engine import get_recommendations
    recommendations = await get_recommendations(db, current_user)
    return recommendations


@router.get("/summary")
def get_progress_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a summary of the user's overall progress."""
    all_progress = db.query(Progress).filter(Progress.user_id == current_user.id).all()
    completed = [p for p in all_progress if p.is_completed]
    total_study_time = sum(p.study_time_minutes for p in all_progress)
    avg_score = 0
    scored = [p for p in all_progress if p.quiz_attempts_count > 0]
    if scored:
        avg_score = sum(p.average_quiz_score for p in scored) / len(scored)

    from app.models.gamification import GamificationProfile, Streak
    profile = db.query(GamificationProfile).filter(
        GamificationProfile.user_id == current_user.id
    ).first()
    streak = db.query(Streak).filter(Streak.user_id == current_user.id).first()

    return {
        "topics_completed": len(completed),
        "total_topics_tracked": len(all_progress),
        "total_study_time_minutes": total_study_time,
        "average_quiz_score": round(avg_score, 1),
        "total_xp": profile.total_xp if profile else 0,
        "level": profile.level if profile else 1,
        "rank": profile.rank if profile else "Beginner",
        "current_streak": streak.current_streak if streak else 0,
        "longest_streak": streak.longest_streak if streak else 0
    }