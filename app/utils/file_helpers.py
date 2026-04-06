import os
import shutil
from uuid import uuid4
from fastapi import UploadFile


UPLOAD_DIR = "uploads"


def ensure_upload_dir() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_uploaded_file(file: UploadFile) -> tuple[str, str]:
    ensure_upload_dir()

    extension = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return unique_name, file_path