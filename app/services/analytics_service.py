from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import QuizAttempt, TopicMastery, Quiz

def calculate_topic_mastery(db: Session, Student_id: int):
    results = (
        db.query(
            Quiz.topic_id,
            func.avg(QuizAttempt.score).label("average_score"),
            func.count(QuizAttempt.id).label("attempts")
        )
        .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
        .filter(QuizAttempt.user_id == Student_id)
        .group_by(Quiz.topic_id)
        .all()
    )

    mastery_list = []
    for topic_id, avg_score, attempts in results:


        #determine mastery level based on average score
        if avg_score < 50:
            mastery_level = "beginner"
        elif avg_score < 80:
            mastery_level = "intermediate"
        else:
            mastery_level = "advanced"


        #check if record exists
        record = db.query(TopicMastery).filter(
            TopicMastery.student_id == Student_id,
            TopicMastery.topic_id == topic_id
        ).first()
        if record:
            record.average_score = avg_score
            record.attempts = attempts
            record.mastery_level = mastery_level
        else:
            new_record = TopicMastery(
                student_id = Student_id,
                topic_id=topic_id,
                average_score=avg_score,
                attempts=attempts,
                mastery_level=mastery_level
            )
            db.add(new_record)

        mastery_list.append(new_record)
    db.commit()

    return mastery_list
           
