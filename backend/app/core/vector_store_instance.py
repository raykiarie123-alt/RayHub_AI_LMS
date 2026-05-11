"""
Global FAISS vector store instance for RayHub AI LMS.
Initializes once on application startup and is reused by RAG routes.
"""

from app.services.rag.vector_store import FAISSVectorStore

_vector_store: FAISSVectorStore | None = None


def get_vector_store() -> FAISSVectorStore | None:
    global _vector_store
    return _vector_store


def init_vector_store() -> FAISSVectorStore:
    global _vector_store

    if _vector_store is None:
        _vector_store = FAISSVectorStore()

    return _vector_store