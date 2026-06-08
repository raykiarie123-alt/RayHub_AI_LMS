import os
from pathlib import Path


def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF, TXT, MD, or DOCX files.
    Encrypted PDFs that cannot be decrypted are accepted but stored with empty text.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".txt" or ext == ".md":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Could not read DOCX file: {e}")

    elif ext == ".pdf":
        return _extract_pdf_text(file_path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF. Handles encrypted/password-protected PDFs gracefully."""
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ValueError("pypdf is not installed. Run: pip install pypdf")

    try:
        reader = PdfReader(file_path)

        # Handle encrypted PDFs
        if reader.is_encrypted:
            # Try decrypting with an empty password (many PDFs use this)
            try:
                reader.decrypt("")
            except Exception:
                # PyCryptodome not installed or wrong password — store file without text
                # The file is still saved; it just won't be searchable via RAG
                return ""

        text_parts = []
        for page in reader.pages:
            try:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            except Exception:
                continue  # Skip unreadable pages, don't crash

        return "\n".join(text_parts)

    except Exception as e:
        # Never block the upload — return empty text and log the error
        print(f"[parser_service] Warning: could not extract text from {file_path}: {e}")
        return ""