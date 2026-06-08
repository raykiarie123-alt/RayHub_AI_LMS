from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.resource import Resource
from app.models.quiz import QuizAttempt
from app.models.progress import Progress
from app.models.gamification import GamificationProfile
from app.models.rag_chat import RAGChat

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    total_users = db.query(User).filter(User.role == "student").count()
    active_users = db.query(User).filter(User.role == "student", User.is_active == True).count()
    total_resources = db.query(Resource).count()
    total_quizzes_taken = db.query(QuizAttempt).filter(QuizAttempt.is_completed == True).count()
    total_topics_completed = db.query(Progress).filter(Progress.is_completed == True).count()
    total_ai_interactions = db.query(RAGChat).count()

    return {
        "total_students": total_users,
        "active_students": active_users,
        "total_resources": total_resources,
        "total_quizzes_taken": total_quizzes_taken,
        "total_topics_completed": total_topics_completed,
        "total_ai_interactions": total_ai_interactions,
    }


@router.get("/users")
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    users = db.query(User).offset(skip).limit(limit).all()
    result = []
    for user in users:
        profile = db.query(GamificationProfile).filter(
            GamificationProfile.user_id == user.id
        ).first()
        ai_count = db.query(RAGChat).filter(RAGChat.user_id == user.id).count()
        quiz_count = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.is_completed == True
        ).count()
        result.append({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "cpa_level": user.cpa_level,
            "student_level": user.student_level,
            "is_active": user.is_active,
            "total_xp": profile.total_xp if profile else 0,
            "level": profile.level if profile else 1,
            "rank": profile.rank if profile else "Beginner",
            "ai_interactions": ai_count,
            "quizzes_completed": quiz_count,
            "created_at": user.created_at,
        })
    return result


@router.get("/resources")
def list_all_resources(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    resources = db.query(Resource).order_by(Resource.created_at.desc()).limit(100).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "resource_type": r.resource_type,
            "level": r.level,
            "is_indexed": r.is_indexed,
            "is_approved": r.is_approved,
            "uploader_id": r.uploader_id,
            "created_at": r.created_at,
        }
        for r in resources
    ]


@router.post("/resources/approve")
def approve_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
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
    from app.models.quiz import Quiz
    from app.models.course import Topic

    total_quizzes = db.query(Quiz).count()
    completed_attempts = db.query(QuizAttempt).filter(QuizAttempt.is_completed == True).all()
    avg_score = 0
    if completed_attempts:
        avg_score = sum(a.percentage for a in completed_attempts) / len(completed_attempts)

    weak_areas = db.query(Progress).filter(
        Progress.average_quiz_score < 60,
        Progress.quiz_attempts_count > 0
    ).count()

    # AI interaction analytics
    total_ai = db.query(RAGChat).count()
    unique_ai_users = db.query(RAGChat.user_id).distinct().count()

    # Top AI users
    from sqlalchemy import func
    top_ai_raw = (
        db.query(RAGChat.user_id, func.count(RAGChat.id).label("count"))
        .group_by(RAGChat.user_id)
        .order_by(func.count(RAGChat.id).desc())
        .limit(5)
        .all()
    )
    top_ai_users = []
    for user_id, count in top_ai_raw:
        user = db.query(User).filter(User.id == user_id).first()
        top_ai_users.append({
            "user_id": user_id,
            "full_name": user.full_name if user else "Unknown",
            "interactions": count,
        })

    return {
        "total_quizzes": total_quizzes,
        "quiz_completion_rate": len(completed_attempts),
        "average_quiz_score": round(avg_score, 1),
        "students_with_weak_areas": weak_areas,
        "total_resources": db.query(Resource).count(),
        "indexed_resources": db.query(Resource).filter(Resource.is_indexed == True).count(),
        "total_ai_interactions": total_ai,
        "unique_ai_users": unique_ai_users,
        "top_ai_users": top_ai_users,
    }


@router.get("/student-engagement")
def get_student_engagement(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
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
                "rank": p.rank,
            }
            for p in top_students
        ],
    }


@router.get("/ai-interactions")
def get_ai_interactions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get recent AI tutor interactions for admin review."""
    chats = (
        db.query(RAGChat)
        .order_by(RAGChat.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for c in chats:
        user = db.query(User).filter(User.id == c.user_id).first()
        result.append({
            "id": c.id,
            "user_id": c.user_id,
            "user_name": user.full_name if user else "Unknown",
            "question": c.question[:200],
            "answer": (c.answer or "")[:300],
            "created_at": c.created_at,
        })
    return result
