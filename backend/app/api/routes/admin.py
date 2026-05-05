from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.resource import Resource
from app.models.quiz import QuizAttempt
from app.models.progress import Progress
from app.models.gamification import GamificationProfile

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Admin dashboard overview."""
    total_users = db.query(User).filter(User.role == "student").count()
    active_users = db.query(User).filter(User.role == "student", User.is_active == True).count()
    total_resources = db.query(Resource).count()
    total_quizzes_taken = db.query(QuizAttempt).filter(QuizAttempt.is_completed == True).count()
    total_topics_completed = db.query(Progress).filter(Progress.is_completed == True).count()

    return {
        "total_students": total_users,
        "active_students": active_users,
        "total_resources": total_resources,
        "total_quizzes_taken": total_quizzes_taken,
        "total_topics_completed": total_topics_completed
    }


@router.get("/users")
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """List all users with their stats."""
    users = db.query(User).offset(skip).limit(limit).all()
    result = []
    for user in users:
        profile = db.query(GamificationProfile).filter(
            GamificationProfile.user_id == user.id
        ).first()
        result.append({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "cpa_level": user.cpa_level,
            "is_active": user.is_active,
            "total_xp": profile.total_xp if profile else 0,
            "level": profile.level if profile else 1,
            "created_at": user.created_at
        })
    return result


@router.get("/resources")
def list_all_resources(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """List all resources for admin review."""
    resources = db.query(Resource).order_by(Resource.created_at.desc()).limit(100).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "resource_type": r.resource_type,
            "is_indexed": r.is_indexed,
            "is_approved": r.is_approved,
            "uploader_id": r.uploader_id,
            "created_at": r.created_at
        }
        for r in resources
    ]


@router.post("/resources/approve")
def approve_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Approve a resource for student access."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Resource not found")
    resource.is_approved = True
    db.commit()
    return {"message": "Resource approved"}


@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get platform analytics."""
    from app.models.quiz import Quiz
    from app.models.course import Topic, Unit

    total_quizzes = db.query(Quiz).count()
    avg_score_result = db.query(QuizAttempt).filter(
        QuizAttempt.is_completed == True
    ).all()
    avg_score = 0
    if avg_score_result:
        avg_score = sum(a.percentage for a in avg_score_result) / len(avg_score_result)

    weak_areas = db.query(Progress).filter(
        Progress.average_quiz_score < 60,
        Progress.quiz_attempts_count > 0
    ).count()

    return {
        "total_quizzes": total_quizzes,
        "quiz_completion_rate": len(avg_score_result),
        "average_quiz_score": round(avg_score, 1),
        "students_with_weak_areas": weak_areas,
        "total_resources": db.query(Resource).count(),
        "indexed_resources": db.query(Resource).filter(Resource.is_indexed == True).count()
    }


@router.get("/student-engagement")
def get_student_engagement(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get student engagement metrics."""
    from app.models.gamification import Streak
    active_streaks = db.query(Streak).filter(Streak.current_streak > 0).count()
    top_students = db.query(GamificationProfile).order_by(
        GamificationProfile.total_xp.desc()
    ).limit(10).all()

    return {
        "students_with_active_streaks": active_streaks,
        "top_students": [
            {
                "user_id": p.user_id,
                "total_xp": p.total_xp,
                "level": p.level,
                "rank": p.rank
            }
            for p in top_students
        ]
    }


