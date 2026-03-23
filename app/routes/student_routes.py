from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import QuizAttempt, Question, StudentAnswer, Quiz, Topic

from app.schemas.student_schema import StudentProfileCreate, StudentProfileResponse, StudentProfileUpdate
from app.services.student_service import create_profile, get_profile, update_profile
from app.services.student_service import get_student_dashboard
from app.schemas.student_schema import StudentDashboard

router = APIRouter(prefix="/students", tags=["Students"])

from app.services.analytics_service import calculate_topic_mastery
from typing import List
from app.schemas.student_schema import TopicMasteryResponse 

@router.get("/dashboard")
def get_student_dashboard(db: Session = Depends(get_db)):

    user_id = 1 #temporary until JWT integration

    toral_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
        ).count()
    
    average_score = db.query(func.avg(QuizAttempt.score)).filter(
        QuizAttempt.user_id == user_id
        ).scalar() 
    
    return{
        "total_quizzes_attempted": toral_quizzes,
        "average_score": average_score
    }

@router.get("/quiz-history")
def quiz_history(db: Session = Depends(get_db)):
    user_id = 1

    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).all()

    results = []
    for attempt in attempts:
        results.append({
            "quiz_id": attempt.quiz_id,
            "score": attempt.score,
        })

    return results

@router.get("/progress")
def student_progress(db: Session = Depends(get_db)):

    user_id = 1

    total_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).count()

    total_correct = db.query(StudentAnswer).filter(
        StudentAnswer.is_correct == True
    ).count()

    total_answers = db.query(StudentAnswer).count()

    accuracy = 0

    if total_answers > 0:
        accuracy = (total_correct / total_answers) * 100

    return {
        "quiz_attempts": total_attempts,
        "accuracy_percentage": accuracy
    }

@router.get("/weak-topics")
def weak_topics(db: Session = Depends(get_db)):

    weak = db.query(
        Topic.title,
        func.avg(StudentAnswer.is_correct.cast())
    ).join(
        Quiz, Quiz.topic_id == Topic.id
    ).join(
        Question, Question.quiz_id == Quiz.id
    ).join(
        StudentAnswer, StudentAnswer.question_id == Question.id
    ).group_by(Topic.title).all()

    results = []

    for topic, avg_score in weak:
        results.append({
            "topic": topic,
            "performance": avg_score
        })

    return results

#Create Profile
@router.post("/profile", response_model=StudentProfileResponse)
def create_student_profile(profile_data: StudentProfileCreate, db: Session = Depends(get_db)):
    user_id = 1  # temporary until JWT integration

    profile = get_profile(db, user_id)
    if profile:
            raise HTTPException(status_code=400, detail="Profile already exists")
    return create_profile(db, user_id)

#Get Profile
@router.get("/profile", response_model=StudentProfileResponse)
def get_student_profile(db: Session = Depends(get_db)):
    user_id = 1  # temporary until JWT integration
    profile = get_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

#Update Profile
@router.put("/profile", response_model=StudentProfileResponse)  
def update_student_profile(profile_data: StudentProfileUpdate, db: Session = Depends(get_db)):
    user_id = 1  # temporary until JWT integration
    profile = update_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.get("/topic-mastery", response_model=List[TopicMasteryResponse])
def topic_mastery(db: Session = Depends(get_db)):
    user_id = 1
    mastery = calculate_topic_mastery(db, user_id)
    return [
        {
            "topic_id": record.topic_id,
            "average_score": record.average_score,
            "attempts": record.attempts,
            "mastery_level": record.mastery_level
        }
        for record in mastery
    ]
    return mastery

@router.get("/dashboard", response_model=StudentDashboard)
def student_dashboard(db: Session = Depends(get_db)):
    user_id = 1
    return get_student_dashboard(db, user_id)

