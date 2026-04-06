from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.schemas.document import DocumentResponse
from app.services.documents.upload_service import upload_document
from app.database import SessionLocal

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload", response_model=DocumentResponse)
def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Replace user_id with authenticated user later
    return upload_document(db=db, file=file, user_id=1)