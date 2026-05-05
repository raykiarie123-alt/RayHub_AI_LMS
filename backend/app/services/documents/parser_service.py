import os
import PyPDF2
from typing import Optional


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    text_parts = []
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    return "\n\n".join(text_parts)


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text_from_file(file_path: str) -> str:
    """Auto-detect file type and extract text."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".txt", ".md"):
        return extract_text_from_txt(file_path)
    else:
        # Try as text
        try:
            return extract_text_from_txt(file_path)
        except Exception:
            raise ValueError(f"Unsupported file type: {ext}")