import json
from typing import Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.services.ai.llm_service import call_llm_json
from app.services.ai.prompt_templates import STUDY_PLAN_SYSTEM_PROMPT, STUDY_PLAN_PROMPT
from app.models.study_plan import StudyPlan, StudyPlanTask
from app.models.user import User


async def generate_study_plan(
    db: Session,
    user: User,
    exam_date: Optional[str],
    available_hours_per_day: float,
    selected_units: list,
    weak_topics: list,
    learning_style: str,
    title: Optional[str]
) -> StudyPlan:
    """Generate an AI-powered personalized study plan."""

    prompt = STUDY_PLAN_PROMPT.format(
        exam_date=exam_date or "Not specified",
        hours_per_day=available_hours_per_day,
        selected_units=", ".join(selected_units) if selected_units else "All units",
        weak_topics=", ".join(weak_topics) if weak_topics else "None specified",
        learning_style=learning_style or "balanced",
        cpa_level=user.cpa_level or "Intermediate"
    )

    raw_json = await call_llm_json(
        system_prompt=STUDY_PLAN_SYSTEM_PROMPT,
        user_message=prompt
    )

    data = json.loads(raw_json)

    # Parse exam date
    parsed_exam_date = None
    if exam_date:
        try:
            parsed_exam_date = date.fromisoformat(exam_date)
        except ValueError:
            pass

    plan = StudyPlan(
        user_id=user.id,
        title=title or data.get("title", "My CPA Study Plan"),
        description=data.get("description", ""),
        exam_date=parsed_exam_date,
        available_hours_per_day=available_hours_per_day,
        selected_units=selected_units,
        weak_topics=weak_topics,
        learning_style=learning_style,
        ai_generated_plan=data
    )
    db.add(plan)
    db.flush()

    # Create tasks from weekly plan
    today = date.today()
    for week_data in data.get("weekly_plan", []):
        week_num = week_data.get("week", 1)
        for task_data in week_data.get("tasks", []):
            day_num = task_data.get("day", 1)
            scheduled = today + timedelta(weeks=week_num - 1, days=day_num - 1)
            task = StudyPlanTask(
                study_plan_id=plan.id,
                title=task_data.get("title", "Study Task"),
                description=task_data.get("description", ""),
                task_type=task_data.get("task_type", "topic"),
                week_number=week_num,
                day_number=day_num,
                estimated_hours=task_data.get("estimated_hours", 1.0),
                scheduled_date=scheduled,
                order=(week_num - 1) * 7 + day_num
            )
            db.add(task)

    db.commit()
    db.refresh(plan)
    return plan