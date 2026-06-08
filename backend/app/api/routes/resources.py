import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resource import Resource
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/resources", tags=["Resources"])

LEVEL_ACCESS = {
    "foundation": ["foundation"],
    "intermediate": ["foundation", "intermediate"],
    "advanced": ["foundation", "intermediate", "advanced"],
    "post-qualification": ["foundation", "intermediate", "advanced", "post-qualification"],
}

UPLOAD_DIR = "./uploads/resources"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _extract_text(file_path: str, resource_type: str) -> str:
    """Best-effort text extraction from uploaded files."""
    try:
        if file_path.lower().endswith(".pdf"):
            from app.services.rag.pdf_parser import extract_text_from_pdf
            return extract_text_from_pdf(file_path)
        if file_path.lower().endswith(".txt"):
            with open(file_path, "r", errors="ignore") as f:
                return f.read()
    except Exception:
        pass
    return ""


@router.get("/")
def get_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student_level = getattr(current_user, "student_level", None) or "foundation"
    allowed_levels = LEVEL_ACCESS.get(student_level, ["foundation"])

    resources = (
        db.query(Resource)
        .filter(Resource.level.in_(allowed_levels))
        .order_by(Resource.id.desc())
        .all()
    )

    result = []
    for r in resources:
        uploader_name = None
        if r.uploader_id:
            uploader = db.query(User).filter(User.id == r.uploader_id).first()
            uploader_name = uploader.full_name if uploader else None
        result.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "resource_type": r.resource_type,
            "level": r.level,
            "url": r.url,
            "file_path": r.file_path,
            "is_indexed": r.is_indexed,
            "is_approved": r.is_approved,
            "uploader_id": r.uploader_id,
            "uploader_name": uploader_name,
            "created_at": r.created_at,
        })
    return result


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
    student_level = getattr(current_user, "student_level", None) or "foundation"
    allowed_levels = LEVEL_ACCESS.get(student_level, ["foundation"])

    if level not in allowed_levels:
        raise HTTPException(
            status_code=403,
            detail="You cannot upload resources to a level higher than your current level",
        )

    # Save file
    safe_name = file.filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{safe_name}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text for AI/RAG use
    content_text = _extract_text(file_path, resource_type)

    # Add to FAISS vector store
    if content_text:
        try:
            from app.services.rag.chunker import chunk_text
            from app.services.rag.vector_store import add_chunks
            chunks = chunk_text(content_text)
            add_chunks(chunks)
        except Exception:
            pass

    resource = Resource(
        title=title,
        description=description or f"{title} - {level} level resource",
        resource_type=resource_type,
        level=level,
        file_path=file_path,
        content_text=content_text or None,
        uploader_id=current_user.id,
        is_indexed=bool(content_text),
    )

    db.add(resource)
    db.commit()
    db.refresh(resource)

    # Award XP for uploading
    try:
        from app.services.gamification_service import add_xp
        add_xp(db, current_user.id, 10, "Uploaded a resource", "resource", resource.id)
    except Exception:
        pass

    return {
        "message": "Resource uploaded successfully",
        "resource": {
            "id": resource.id,
            "title": resource.title,
            "level": resource.level,
            "resource_type": resource.resource_type,
            "is_indexed": resource.is_indexed,
        },
    }


@router.delete("/{resource_id}")
def delete_resource_endpoint(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    if resource.uploader_id != current_user.id and current_user.role not in ("admin", "tutor"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this resource")
    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted"}
