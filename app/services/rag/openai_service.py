def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Splits text into overlapping chunks.

    Args:
        text (str): Full document text
        chunk_size (int): Size of each chunk
        overlap (int): Overlap between chunks

    Returns:
        List[str]: List of text chunks
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks