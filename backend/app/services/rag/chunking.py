from typing import List
from app.utils.constants import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks for embedding.
    Uses word-boundary splitting to avoid cutting words mid-way.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(words):
            break
        start += chunk_size - overlap

    return chunks


def chunk_by_paragraphs(text: str, max_chunk_size: int = CHUNK_SIZE) -> List[str]:
    """
    Split text by paragraphs first, then by size if needed.
    Produces more semantically coherent chunks.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        words_in_para = len(para.split())
        words_in_current = len(current_chunk.split()) if current_chunk else 0

        if words_in_current + words_in_para <= max_chunk_size:
            current_chunk = (current_chunk + "\n\n" + para).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if words_in_para > max_chunk_size:
                # Split large paragraph
                sub_chunks = chunk_text(para, max_chunk_size)
                chunks.extend(sub_chunks[:-1])
                current_chunk = sub_chunks[-1] if sub_chunks else ""
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks