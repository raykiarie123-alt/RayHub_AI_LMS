from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.resource import Resource
from app.models.user import User
from app.schemas.resource_schema import ResourceResponse, ResourceUpdate
from app.services.resource_service import get_resources, get_resource_by_id

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/", response_model=List[ResourceResponse])
def list_resources(
    course_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resources = get_resources(
        db,
        current_user,
        course_id=course_id,
        unit_id=unit_id,
        topic_id=topic_id,
        resource_type=resource_type,
        skip=skip,
        limit=limit
    )

    result = []

    for r in resources:
        item = ResourceResponse.model_validate(r)

        item.uploader_name = (
            r.uploader.full_name
            if r.uploader else "Unknown"
        )

        item.course_name = (
            r.course.name
            if r.course else None
        )

        result.append(item)

    return result
@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a resource by ID."""
    return get_resource_by_id(db, resource_id)


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a resource."""
    resource = get_resource_by_id(db, resource_id)
    if resource.uploader_id != current_user.id and current_user.role not in ("admin", "tutor"):
        raise HTTPException(status_code=403, detail="Not authorized")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.post("/{resource_id}/summarize")
async def summarize_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate an AI summary for a resource."""
    resource = get_resource_by_id(db, resource_id)
    if not resource.content_text:
        raise HTTPException(status_code=400, detail="Resource has no text content to summarize")

    from app.services.ai.llm_service import call_llm
    from app.services.ai.prompt_templates import SUMMARIZE_SYSTEM_PROMPT, SUMMARIZE_PROMPT

    content = resource.content_text[:8000]
    prompt = SUMMARIZE_PROMPT.format(topic=resource.title, content=content)
    summary = await call_llm(system_prompt=SUMMARIZE_SYSTEM_PROMPT, user_message=prompt)

    resource.summary = summary
    db.commit()

    return {"summary": summary, "resource_id": resource_id}
