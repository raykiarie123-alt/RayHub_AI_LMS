from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Quiz, Question, QuizAttempt, StudentAnswer
from app.schemas.quiz_schema import QuizCreate, QuestionCreate, QuizSubmission
from app.services.gamification_service import update_streak
from app.services.notification_service import create_notification

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/")
def create_quiz(quiz: QuizCreate, db: Session = Depends(get_db)):
    new_quiz = Quiz(
        topic_id=quiz.topic_id,
        title=quiz.title
    )

    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    return new_quiz


@router.post("/questions")
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    new_question = Question(
        quiz_id=question.quiz_id,
        question_text=question.question_text,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_answer=question.correct_answer
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


@router.post("/attempt")
def attempt_quiz(submission: QuizSubmission, db: Session = Depends(get_db)):
    user_id = 1  # replace later with authenticated user

    # validate quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    correct_answers = 0
    total_questions = len(submission.answers)

    # create attempt first
    quiz_attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=submission.quiz_id,
        score=0
    )
    db.add(quiz_attempt)
    db.commit()
    db.refresh(quiz_attempt)

    # save each answer
    for answer in submission.answers:
        question = db.query(Question).filter(
            Question.id == answer.question_id
        ).first()

        if not question:
            continue

        is_correct = False
        if question.correct_answer == answer.selected_option:
            correct_answers += 1
            is_correct = True

        student_answer = StudentAnswer(
            quiz_attempt_id=quiz_attempt.id,
            question_id=answer.question_id,
            selected_option=answer.selected_option,
            is_correct=is_correct
        )
        db.add(student_answer)

    # calculate percentage score
    quiz_attempt.score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0

    db.commit()
    db.refresh(quiz_attempt)

    # update streak
    streak = update_streak(db, user_id)

    # create notification
    create_notification(
        db,
        user_id,
        f"You scored {quiz_attempt.score}%. Current streak: {streak} days."
    )

    return {
        "score": quiz_attempt.score,
        "current_streak": streak
    }