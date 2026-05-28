from sqlalchemy.orm import Session
from typing import List
from app.models.resource import Resource, ResourceChunk
from app.services.rag.chunking import chunk_by_paragraphs
from app.services.rag.embeddings import embed_texts
from app.services.rag.vector_store import FAISSVectorStore


def ingest_resource(
    db: Session,
    vector_store: FAISSVectorStore,
    resource: Resource
) -> int:
    """
    Ingest a resource into the vector store.
    Chunks the text, creates embeddings, stores in FAISS and DB.
    Returns number of chunks created.
    """
    if not resource.content_text:
        return 0

    # Chunk the text
    chunks = chunk_by_paragraphs(resource.content_text)
    if not chunks:
        return 0

    # Create embeddings
    embeddings = embed_texts(chunks)

    # Build metadata list
    meta_list = [
        {
            "resource_id": resource.id,
            "resource_title": resource.title,
            "chunk_text": chunk,
            "chunk_id": None  # Will be set after DB insert
        }
        for chunk in chunks
    ]

    # Store in FAISS and get chunk count
    # NOTE: current FAISSVectorStore implementation supports add_chunks(), not add_embeddings().
    faiss_ids = vector_store.add_chunks(chunks)


    # Store chunks in DB
    db_chunks = []
    for i, chunk in enumerate(chunks):

        db_chunk = ResourceChunk(
            resource_id=resource.id,
            chunk_index=i,
            content=chunk,
            embedding_id=None,

            token_count=len(chunk.split())
        )
        db.add(db_chunk)
        db_chunks.append(db_chunk)

    # Update metadata with DB chunk IDs
    db.flush()
    for i, (db_chunk, meta) in enumerate(zip(db_chunks, meta_list)):
        meta["chunk_id"] = db_chunk.id

    # Mark resource as indexed
    resource.is_indexed = True
    db.commit()

    return len(chunks)


def delete_resource_from_store(
    db: Session,
    vector_store: FAISSVectorStore,
    resource_id: int
):
    """Remove all chunks for a resource from vector store and DB."""
    # Current FAISSVectorStore implementation does not support per-resource deletion.
    # We fall back to clearing the whole in-memory index.
    vector_store.clear()

    db.query(ResourceChunk).filter(ResourceChunk.resource_id == resource_id).delete()
    db.commit()


