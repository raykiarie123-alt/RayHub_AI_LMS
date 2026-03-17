from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import QuizAttempt
from app.models.models import StudentProfile


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

def create_profile(db: Session, user_id: int, profile_data):
    profile = StudentProfile(
        user_id=user_id,
        study_hours_per_day=profile_data.study_hours_per_day,
        preferred_learning_style=profile_data.preferred_learning_style,
        target_exam_date=profile_data.target_exam_date,
        daily_reminder_time=profile_data.daily_reminder_time
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def get_profile(db: Session, user_id: int):
    return db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()   
 
def update_profile(db: Session, user_id: int, data):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        return None
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile
