from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.study_plan import StudyPlan, StudyPlanTask
from app.models.user import User
from app.schemas.study_plan_schema import (
    StudyPlanGenerateRequest, StudyPlanResponse, CompleteTaskRequest
)
from app.services.ai.study_plan_generator import generate_study_plan

router = APIRouter(prefix="/study-plans", tags=["Study Plans"])


@router.post("/generate", response_model=StudyPlanResponse, status_code=201)
async def generate_plan(
    data: StudyPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a personalized AI study plan."""
    plan = await generate_study_plan(
        db=db,
        user=current_user,
        exam_date=data.exam_date,
        available_hours_per_day=data.available_hours_per_day or 3.0,
        selected_units=data.selected_units or [],
        weak_topics=data.weak_topics or [],
        learning_style=data.learning_style or "balanced",
        title=data.title
    )

    # Award XP for creating a study plan
    from app.services.gamification_service import add_xp, check_and_award_badges
    add_xp(db, current_user.id, 10, "Created a study plan", "study_plan", plan.id)
    check_and_award_badges(db, current_user.id)

    return plan


@router.get("/me", response_model=List[StudyPlanResponse])
def get_my_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all study plans for the current user."""
    return db.query(StudyPlan).filter(
        StudyPlan.user_id == current_user.id
    ).order_by(StudyPlan.created_at.desc()).all()


@router.get("/{plan_id}", response_model=StudyPlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan


@router.put("/{plan_id}", response_model=StudyPlanResponse)
def update_plan(
    plan_id: int,
    data: StudyPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Study plan deleted"}


@router.post("/{plan_id}/complete-task")
def complete_task(
    plan_id: int,
    data: CompleteTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a study plan task as completed."""
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")

    task = db.query(StudyPlanTask).filter(
        StudyPlanTask.id == data.task_id,
        StudyPlanTask.study_plan_id == plan_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = True
    task.completed_at = datetime.utcnow()

    # Update plan completion percentage
    total_tasks = len(plan.tasks)
    completed_tasks = sum(1 for t in plan.tasks if t.is_completed)
    plan.completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    db.commit()

    # Award XP
    from app.services.gamification_service import add_xp
    add_xp(db, current_user.id, 10, f"Completed study task: {task.title}", "task", task.id)

    return {"message": "Task completed", "completion_percentage": plan.completion_percentage}