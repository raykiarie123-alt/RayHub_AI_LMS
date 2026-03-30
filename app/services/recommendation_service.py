from app.models.models import TopicMastery, QuizAttempt
from datetime import datetime, timedelta


def generate_recommendations(db, student_id):

    recommendations = []
    #1. Get topic mastery data
    mastery_data = db.query(TopicMastery).filter(
        TopicMastery.student_id == student_id
    ).all()

    #2. weak topics
    weak_topics = [m for m in mastery_data if m.mastery_level == "Weak"]    
    if weak_topics:
        recommendations.append("Focus on weak topics: " + ", ".join([str(m.topic_id) for m in weak_topics]))

    #3. medium topics
    medium_topics = [m for m in mastery_data if m.mastery_level == "Medium"]
    if medium_topics:
        recommendations.append("Review medium topics: " + ", ".join([str(m.topic_id) for m in medium_topics]))  

    #4. Strong topics
    strong_topics = [m for m in mastery_data if m.mastery_level == "Strong  "]
    if strong_topics:    
        recommendations.append("Maintain strong topics: " + ", ".join([str(m.topic_id) for m in strong_topics]))
    
    #5. Check Quiz Attempts
    recent_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == student_id
    ).count()

    if recent_attempts == 0:
        recommendations.append({
            "message": "You haven't attempted any quiz. Start with a quiz.",
            "priority": "High"
        })

    return recommendations
    

def generate_reminders(db, student_id, study_plan):

    reminders = []

    today = datetime.today().date()

    for day in study_plan:

        plan_date = datetime.strptime(day["date"], "%Y-%m-%d").date()

        if plan_date == today:

            for task in day["tasks"]:

                reminders.append({
                    "message": f"You planned to study {task['topic']} today. Don't forget your quiz.",
                    "time": "18:00"
                })

    return reminders
    

def inactivity_reminder(last_activity):
        if not last_activity:
            return {
                "message": "We noticed you haven't been active. Try to attempt a quiz or review some topics.",
                "priority": "Medium"
            }
        else:
            days_inactive = (datetime.today() - last_activity).days
            if days_inactive >= 7:
                return {
                    "message": f"You've been inactive for {days_inactive} days. Let's get back on track!",
                    "priority": "Medium"
                }
        return None
    

