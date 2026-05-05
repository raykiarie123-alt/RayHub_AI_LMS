import json
from typing import List, Dict
from sqlalchemy.orm import Session
from app.services.ai.llm_service import call_llm_json
from app.services.ai.prompt_templates import RECOMMENDATION_PROMPT
from app.models.user import User
from app.models.progress import Progress
from app.models.gamification import Streak


async def get_recommendations(db: Session, user: User) -> List[Dict]:
    """Generate personalized study recommendations for a user."""

    # Gather user data
    progress_records = db.query(Progress).filter(
        Progress.user_id == user.id,
        Progress.average_quiz_score < 70
    ).limit(5).all()

    weak_areas = []
    for p in progress_records:
        if p.topic_id:
            from app.models.course import Topic
            topic = db.query(Topic).filter(Topic.id == p.topic_id).first()
            if topic:
                weak_areas.append(f"{topic.title} (avg score: {p.average_quiz_score:.0f}%)")

    completed_topics = db.query(Progress).filter(
        Progress.user_id == user.id,
        Progress.is_completed == True
    ).count()

    streak = db.query(Streak).filter(Streak.user_id == user.id).first()
    streak_days = streak.current_streak if streak else 0

    prompt = RECOMMENDATION_PROMPT.format(
        cpa_level=user.cpa_level or "Intermediate",
        weak_areas=", ".join(weak_areas) if weak_areas else "None identified yet",
        completed_topics=f"{completed_topics} topics completed",
        quiz_performance="Based on recent quiz attempts",
        streak=streak_days
    )

    try:
        raw_json = await call_llm_json(
            system_prompt="You are an expert CPA study coach. Return valid JSON only.",
            user_message=prompt
        )
        data = json.loads(raw_json)
        return data.get("recommendations", [])
    except Exception:
        return [
            {"type": "topic", "title": "Review weak areas", "reason": "Focus on topics with low scores", "priority": "high"},
            {"type": "quiz", "title": "Practice quiz", "reason": "Regular practice improves retention", "priority": "medium"}
        ]


