from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.vector_store_instance import get_vector_store
from app.models.resource import Resource
from app.models.user import User
from app.schemas.resource_schema import ResourceResponse
from app.services.documents.upload_service import save_uploaded_file, delete_file
from app.services.documents.parser_service import extract_text_from_file
from app.services.rag.ingestion import ingest_resource, delete_resource_from_store
from app.services.resource_service import get_resources, get_resource_by_id, delete_resource

router = APIRouter(prefix="/documents", tags=["Documents"])


def _ingest_background(db_url: str, resource_id: int):
    """Background task to ingest a resource into the vector store."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if resource:
            vs = get_vector_store()
            ingest_resource(db, vs, resource)
    finally:
        db.close()


@router.post("/upload", response_model=ResourceResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    course_id: Optional[int] = Form(None),
    unit_id: Optional[int] = Form(None),
    topic_id: Optional[int] = Form(None),
    resource_type: Optional[str] = Form("pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF or text document and index it for RAG."""

    file_path = await save_uploaded_file(file)

    try:
        content_text = extract_text_from_file(file_path)
    except Exception as e:
        delete_file(file_path)
        raise HTTPException(status_code=400, detail=str(e))

    # Auto-map to Course/Unit/Topic when IDs are not provided by the upload UI.
    if course_id is None and unit_id is None and topic_id is None:
        try:
            from app.models.course import Course, Unit, Topic, Level

            student_level = getattr(current_user, "student_level", None) or "foundation"
            level = db.query(Level).filter(Level.name.ilike(student_level)).first()
            if not level:
                level = db.query(Level).filter(Level.name.ilike("foundation")).first()

            course = (
                db.query(Course)
                .filter(Course.level_id == (level.id if level else None), Course.is_active == True)
                .order_by(Course.id.asc())
                .first()
            )

            if course:
                unit = (
                    db.query(Unit)
                    .filter(Unit.course_id == course.id, Unit.title == "Uploaded Resources", Unit.is_active == True)
                    .first()
                )

                if not unit:
                    unit = Unit(
                        title="Uploaded Resources",
                        description="Uploaded Resources",
                        course_id=course.id,
                        order=1,
                        is_active=True,
                    )
                    db.add(unit)
                    db.flush()

                topic = (
                    db.query(Topic)
                    .filter(Topic.unit_id == unit.id, Topic.title == title, Topic.is_active == True)
                    .first()
                )

                if not topic:
                    topic = Topic(
                        title=title,
                        description=title,
                        unit_id=unit.id,
                        order=1,
                        estimated_hours=2,
                        is_active=True,
                    )
                    db.add(topic)
                    db.flush()

                course_id = course.id
                unit_id = unit.id
                topic_id = topic.id
        except Exception:
            # Keep provided/None IDs; the upload can still work without mapping.
            pass

    resource = Resource(
        title=title,
        description=description,
        resource_type=resource_type,
        file_path=file_path,
        content_text=content_text,
        uploader_id=current_user.id,
        course_id=course_id,
        unit_id=unit_id,
        topic_id=topic_id,
        is_indexed=False,
    )

    db.add(resource)
    db.commit()
    db.refresh(resource)

    # Index in background (but currently executed immediately).
    vs = get_vector_store()
    ingest_resource(db, vs, resource)

    # Award XP
    from app.services.gamification_service import add_xp

    add_xp(db, current_user.id, 10, "Uploaded a resource", "resource", resource.id)

    return resource


@router.get("/", response_model=List[ResourceResponse])
def list_documents(
    course_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents."""

    return get_resources(
        db,
        current_user,
        course_id=course_id,
        unit_id=unit_id,
        topic_id=topic_id,
        resource_type=None,
    )


@router.get("/{document_id}", response_model=ResourceResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a document by ID."""

    return get_resource_by_id(db, document_id)


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document and remove from vector store."""

    resource = get_resource_by_id(db, document_id)
    vs = get_vector_store()
    delete_resource_from_store(db, vs, document_id)
    if resource.file_path:
        delete_file(resource.file_path)
    delete_resource(db, document_id, current_user)
    return {"message": "Document deleted"}

