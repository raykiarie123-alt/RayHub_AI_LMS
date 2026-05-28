from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resource import Resource
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/resources", tags=["Resources"])

LEVEL_ACCESS = {
    "foundation": ["foundation"],
    "intermediate": ["foundation", "intermediate"],
    "advanced": ["foundation", "intermediate", "advanced"],
}


@router.get("/")
def get_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # current_user may be a SQLAlchemy User OR a decoded/token payload dict
    student_level = getattr(current_user, "student_level", None)
    if student_level is None and isinstance(current_user, dict):
        student_level = current_user.get("student_level")


        


    allowed_levels = LEVEL_ACCESS.get(
        student_level or "foundation",
        ["foundation"],
    )

    resources = (
        db.query(Resource)
        .filter(Resource.level.in_(allowed_levels))
        .order_by(Resource.id.desc())
        .all()
    )

    return resources


@router.post("/upload")

async def upload_resource(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    resource_type: str = Form("pdf"),
    level: str = Form("foundation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student_level = getattr(current_user, "student_level", None)
    if student_level is None and isinstance(current_user, dict):
        student_level = current_user.get("student_level")

    allowed_levels = LEVEL_ACCESS.get(

        student_level or "foundation",
        ["foundation"],
    )

    if level not in allowed_levels:
        raise HTTPException(
            status_code=403,
            detail="You cannot upload resources to a higher level",
        )

    resource = Resource(
        title=title,
        description=description,
        resource_type=resource_type,
        level=level,
        uploader_name=current_user.full_name,
    )

    db.add(resource)
    db.commit()
    db.refresh(resource)

    return {
        "message": "Resource uploaded successfully",
        "resource": resource,
    }
