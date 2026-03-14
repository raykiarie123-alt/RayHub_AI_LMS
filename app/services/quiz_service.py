from sqlalchemy.orm import Session
from app.models.models import QuizAttempt, StudentAnswer, Question

def submit_quiz(db: Session, user_id: int, quiz_id: int, answers:dict):
    score = 0
    for question_id, selected_option in answers.items():
        question = db.query(Question).filter(
            Question.id == question_id
        ).first()

        is_correct = selected_option == question.correct_option

        if is_correct:
            score +=1

        student_answer = StudentAnswer(
            user_id=user_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct
        )

        db.add(student_answer)

    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        score=score
    )

    db.add(attempt)
    db.commit()

    return score
