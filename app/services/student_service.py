from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import QuizAttempt


def get_student_dashboard(db: Session, user_id: int):

    total_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).count()

    avg_score = db.query(func.avg(QuizAttempt.score)).filter(
        QuizAttempt.user_id == user_id
    ).scalar()

    return {
        "total_quizzes": total_quizzes,
        "average_score": avg_score
    }