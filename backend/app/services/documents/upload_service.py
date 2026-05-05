import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.utils.helpers import safe_filename

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}
MAX_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


async def save_uploaded_file(file: UploadFile, subfolder: str = "documents") -> str:
    """
    Save an uploaded file to the upload directory.
    Returns the saved file path.
    """
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, unique_name)

    # Save file
    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    return file_path


def delete_file(file_path: str):
    """Delete a file from the filesystem."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


