from datetime import date, timedelta
from app.models.models import TopicMastery, Topic, StudentProfile


def generate_study_plan(db, student_id):

    # 1. Get student profile
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == student_id
    ).first()

    if not profile:
        return {"error": "Profile not found"}

    study_hours = profile.study_hours_per_day

    # 2. Get weak topics first
    weak_topics = db.query(TopicMastery).filter(
        TopicMastery.student_id == student_id,
        TopicMastery.mastery_level == "Weak"
    ).all()

    medium_topics = db.query(TopicMastery).filter(
        TopicMastery.student_id == student_id,
        TopicMastery.mastery_level == "Medium"
    ).all()

    # 3. Combine priority list
    priority_topics = weak_topics + medium_topics

    # 4. Generate plan for next 7 days
    today = date.today()
    plan = []

    topic_index = 0

    for i in range(7):
        day = today + timedelta(days=i)

        daily_tasks = []

        # assign topics based on study hours
        for _ in range(study_hours):

            if topic_index < len(priority_topics):

                topic_id = priority_topics[topic_index].topic_id

                topic = db.query(Topic).filter(Topic.id == topic_id).first()

                daily_tasks.append({
                    "topic": topic.title,
                    "activity": "Study + Quiz"
                })

                topic_index += 1

        plan.append({
            "date": str(day),
            "tasks": daily_tasks
        })

    return plan
