import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.services.ai.llm_service import call_llm_json
from app.services.ai.prompt_templates import (
    QUIZ_SYSTEM_PROMPT, QUIZ_MCQ_PROMPT, QUIZ_SHORT_ANSWER_PROMPT, QUIZ_CASE_PROMPT
)
from app.models.quiz import Quiz, Question
from app.models.course import Topic, Unit
from app.models.resource import Resource


def _get_context(db: Session, topic_id: Optional[int], unit_id: Optional[int], resource_id: Optional[int]) -> str:
    """Build context string for quiz generation."""
    parts = []
    if topic_id:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if topic and topic.content:
            parts.append(f"Topic content: {topic.content[:2000]}")
    if resource_id:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if resource and resource.content_text:
            parts.append(f"Study material: {resource.content_text[:3000]}")
    return "\n\n".join(parts)


def _get_topic_name(db: Session, topic_id: Optional[int], unit_id: Optional[int]) -> str:
    if topic_id:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if topic:
            return topic.title
    if unit_id:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if unit:
            return unit.title
    return "CPA Accounting"


async def generate_quiz(
    db: Session,
    topic_id: Optional[int],
    unit_id: Optional[int],
    resource_id: Optional[int],
    difficulty: str,
    num_questions: int,
    question_type: str,
    title: Optional[str],
    creator_id: int
) -> Quiz:
    """Generate a quiz using AI and save to database."""
    topic_name = _get_topic_name(db, topic_id, unit_id)
    context = _get_context(db, topic_id, unit_id, resource_id)
    context_str = f"\nAdditional context:\n{context}" if context else ""

    # Select prompt template
    if question_type == "short_answer":
        prompt = QUIZ_SHORT_ANSWER_PROMPT.format(
            num_questions=num_questions, topic=topic_name,
            difficulty=difficulty, context=context_str
        )
    elif question_type == "case_study":
        prompt = QUIZ_CASE_PROMPT.format(
            num_questions=num_questions, topic=topic_name,
            difficulty=difficulty, context=context_str
        )
    else:
        prompt = QUIZ_MCQ_PROMPT.format(
            num_questions=num_questions, topic=topic_name,
            difficulty=difficulty, context=context_str
        )

    raw_json = await call_llm_json(
        system_prompt=QUIZ_SYSTEM_PROMPT,
        user_message=prompt
    )

    data = json.loads(raw_json)
    quiz_title = title or data.get("title", f"Quiz on {topic_name}")

    # Create quiz
    quiz = Quiz(
        title=quiz_title,
        topic_id=topic_id,
        unit_id=unit_id,
        difficulty=difficulty,
        question_type=question_type,
        is_ai_generated=True,
        created_by=creator_id,
        resource_id=resource_id
    )
    db.add(quiz)
    db.flush()

    # Create questions
    for i, q in enumerate(data.get("questions", [])):
        question = Question(
            quiz_id=quiz.id,
            question_text=q.get("question_text", ""),
            question_type=q.get("question_type", question_type),
            options=q.get("options"),
            correct_answer=q.get("correct_answer", ""),
            explanation=q.get("explanation", ""),
            marks=1,
            order=i
        )
        db.add(question)

    db.commit()
    db.refresh(quiz)
    return quiz


