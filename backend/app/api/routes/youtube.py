from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.vector_store_instance import get_vector_store
from app.models.resource import Resource
from app.models.user import User
from app.schemas.resource_schema import YouTubeIngestRequest, ResourceResponse
from app.services.youtube.transcript_service import get_youtube_transcript, get_video_title_from_url
from app.services.youtube.youtube_summary_service import summarize_youtube_video
from app.services.rag.ingestion import ingest_resource
from app.services.resource_service import get_resources, get_resource_by_id, delete_resource

router = APIRouter(prefix="/youtube", tags=["YouTube Resources"])


@router.post("/ingest", response_model=ResourceResponse, status_code=201)
async def ingest_youtube(
    data: YouTubeIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ingest a YouTube video by extracting its transcript."""
    try:
        transcript = get_youtube_transcript(data.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    title = data.title or get_video_title_from_url(data.url)

    resource = Resource(
        title=title,
        resource_type="youtube",
        url=data.url,
        content_text=transcript,
        uploader_id=current_user.id,
        course_id=data.course_id,
        unit_id=data.unit_id,
        topic_id=data.topic_id,
        is_indexed=False
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)

    # Index for RAG
    vs = get_vector_store()
    ingest_resource(db, vs, resource)

    return resource


@router.post("/summarize")
async def summarize_youtube(
    data: YouTubeIngestRequest,
    current_user: User = Depends(get_current_user)
):
    """Summarize a YouTube video without saving it."""
    try:
        summary = await summarize_youtube_video(data.url, data.title)
        return {"summary": summary, "url": data.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/resources", response_model=List[ResourceResponse])
def list_youtube_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_resources(db, current_user, resource_type="youtube")


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_youtube_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_resource_by_id(db, resource_id)


@router.delete("/{resource_id}")
def delete_youtube_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vs = get_vector_store()
    from app.services.rag.ingestion import delete_resource_from_store
    delete_resource_from_store(db, vs, resource_id)
    delete_resource(db, resource_id, current_user)
    return {"message": "YouTube resource deleted"}