import re
import uuid
import os
from datetime import datetime
from typing import Optional

# General utility functions for the RayHub AI LMS application. This module includes functions for generating UUIDs, slugifying text, sanitizing filenames, formatting datetimes, calculating percentages, and truncating text. These helper functions are used throughout the application to perform common tasks in a consistent manner.
def generate_uuid() -> str:
    return str(uuid.uuid4())

#slugify text, converts text into a URL-friendly format by lowercasing, removing special characters, replacing spaces with hyphens, and trimming leading/trailing hyphens   
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

#sanitize a filename for safe storage by removing directory paths and special characters, ensuring that the filename is safe to use on the filesystem. This function is used when handling file uploads to prevent security issues related to file paths and names.
def safe_filename(filename: str) -> str:
    """Sanitize a filename for safe storage."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\s\-.]', '', filename)
    return filename

#converts datetime to string in ISO format, if the datetime is None, it returns None. This function is used to ensure that datetime values are consistently formatted when returned in API responses or stored in the database.
def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.isoformat()


def calculate_percentage(score: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((score / total) * 100, 2)


def truncate_text(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."