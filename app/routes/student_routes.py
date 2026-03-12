from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import QuizAttempt, Question, StudentAnswer, Quiz, Topic

router = APIRouter(prefix="/students", tags=["Students Analytics"])

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
