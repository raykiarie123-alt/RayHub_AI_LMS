from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import QuizAttempt
from app.models.models import StudentProfile
from app.services.ai_service import generate_study_plan
from app.services.recommendation_service import generate_recommendations, generate_reminders
from datetime import datetime, timedelta    

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

def get_student_dashboard(db, student_id):

    # 1. Study Plan
    study_plan = generate_study_plan(db, student_id)

    # 2. Recommendations
    recommendations = generate_recommendations(db, student_id)

    # 3. Reminders
    reminders = generate_reminders(db, student_id, study_plan)

    # 4. Add inactivity trigger(optional)
    last_activity = None #fetch last activity timestamp from DB
    if not last_activity:
        reminders.append({
            "date": datetime.today().date(),
            "time": (datetime.now() + timedelta(minutes=30)).time(),
            "message": "We noticed you haven't been active. Consider reviewing your study plan or attempting a quiz."
        })

    return {
        "study_plan": study_plan,
        "recommendations": recommendations,
        "reminders": reminders
    }

