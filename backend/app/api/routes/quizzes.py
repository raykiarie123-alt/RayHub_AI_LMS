from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.quiz import Quiz, Question, QuizAttempt, Answer
from app.models.user import User
from app.schemas.quiz_schema import (
    QuizGenerateRequest, QuizResponse, QuizSubmitRequest, QuizAttemptResponse
)
from app.services.ai.quiz_generator import generate_quiz

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post("/generate", response_model=QuizResponse, status_code=201)
async def generate_quiz_endpoint(
    data: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate an AI-powered quiz."""
    quiz = await generate_quiz(
        db=db,
        topic_id=data.topic_id,
        unit_id=data.unit_id,
        resource_id=data.resource_id,
        difficulty=data.difficulty or "intermediate",
        num_questions=data.number_of_questions or 10,
        question_type=data.question_type or "mcq",
        title=data.title,
        creator_id=current_user.id
    )
    return quiz


@router.get("/", response_model=List[QuizResponse])
def list_quizzes(
    topic_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List available quizzes."""
    query = db.query(Quiz).filter(Quiz.is_active == True)
    if topic_id:
        query = query.filter(Quiz.topic_id == topic_id)
    if unit_id:
        query = query.filter(Quiz.unit_id == unit_id)
    return query.offset(skip).limit(limit).all()


@router.get("/me/history", response_model=List[QuizAttemptResponse])
def get_my_quiz_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's quiz attempt history."""
    return db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.started_at.desc()).limit(50).all()


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a quiz with its questions."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/{quiz_id}/submit", response_model=QuizAttemptResponse)
def submit_quiz(
    quiz_id: int,
    data: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit quiz answers and get results."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = {q.id: q for q in quiz.questions}
    total_marks = len(questions)
    score = 0

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        total_marks=total_marks,
        time_taken_seconds=data.time_taken_seconds,
        is_completed=True,
        completed_at=datetime.utcnow()
    )
    db.add(attempt)
    db.flush()

    for ans_data in data.answers:
        q_id = ans_data.get("question_id")
        user_ans = ans_data.get("answer", "")
        question = questions.get(q_id)
        if not question:
            continue

        is_correct = user_ans.strip().lower() == question.correct_answer.strip().lower()
        marks = question.marks if is_correct else 0
        score += marks

        answer = Answer(
            attempt_id=attempt.id,
            question_id=q_id,
            user_answer=user_ans,
            is_correct=is_correct,
            marks_awarded=marks
        )
        db.add(answer)

    percentage = (score / total_marks * 100) if total_marks > 0 else 0
    attempt.score = score
    attempt.percentage = percentage

    db.commit()
    db.refresh(attempt)

    # Award XP
    from app.services.gamification_service import add_xp, check_and_award_badges
    add_xp(db, current_user.id, 20, "Completed a quiz", "quiz", quiz_id)
    if percentage >= 80:
        add_xp(db, current_user.id, 30, "Scored above 80%", "quiz", quiz_id)
    check_and_award_badges(db, current_user.id)

    # Update progress
    from app.services.progress_service import update_quiz_progress
    if quiz.topic_id:
        update_quiz_progress(db, current_user.id, quiz.topic_id, percentage)

    return attempt


@router.get("/{quiz_id}/results")
def get_quiz_results(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed results for the user's latest quiz attempt."""
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.started_at.desc()).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="No attempt found")

    answers_detail = []
    for answer in attempt.answers:
        q = answer.question
        answers_detail.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "options": q.options,
            "user_answer": answer.user_answer,
            "correct_answer": q.correct_answer,
            "is_correct": answer.is_correct,
            "explanation": q.explanation,
            "marks_awarded": answer.marks_awarded
        })

    return {
        "attempt_id": attempt.id,
        "score": attempt.score,
        "total_marks": attempt.total_marks,
        "percentage": attempt.percentage,
        "answers": answers_detail
    }