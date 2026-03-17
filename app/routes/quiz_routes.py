from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Quiz, Question, QuizAttempt, StudentAnswer
from app.schemas.quiz_schema import QuizCreate, QuestionCreate, QuizSubmission
from app.services.quiz_service import submit_quiz

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

    score = 0
    
    quiz_attempt = QuizAttempt(
        quiz_id=submission.quiz_id,
        user_id=1,  # Replace with actual user ID from auth
        score=0  # Initial score, will be calculated below
    )
    db.add(quiz_attempt)
    db.commit()
    db.refresh(quiz_attempt)

    total_questions = len(submission.answers)
    correct_answers = 0

    for answer in submission.answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if question and question.correct_answer == answer.selected_option:
            correct_answers += 1

        student_answer = StudentAnswer(
            quiz_attempt_id=quiz_attempt.id,
            question_id=answer.question_id,
            selected_option=answer.selected_option
        )
        db.add(student_answer)

    quiz_attempt.score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    db.commit()
    db.refresh(quiz_attempt)

    return {"score": quiz_attempt.score}    

