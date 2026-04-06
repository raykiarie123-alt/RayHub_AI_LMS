from app.services.documents.parser_service import extract_text_from_pdf
from app.services.rag.chunking import chunk_text
from app.services.rag.embeddings import embed_chunks
from app.services.rag.vector_store import vector_store


def ingest_document(file_path: str):
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        return []

    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)

    vector_store.add_embeddings(embeddings, chunks)
    return chunks