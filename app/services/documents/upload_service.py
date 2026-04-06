from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.document import Document
from app.utils.file_helpers import save_uploaded_file


ALLOWED_FILE_TYPES = {"application/pdf"}


def upload_document(
    db: Session,
    file: UploadFile,
    user_id: int | None = None,
) -> Document:
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    saved_name, saved_path = save_uploaded_file(file)

    document = Document(
        user_id=user_id,
        title=file.filename.rsplit(".", 1)[0],
        file_name=saved_name,
        file_path=saved_path,
        source_type="student_upload",
        content_type=file.content_type,
        upload_status="uploaded",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document