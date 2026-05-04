"""
Temporary vector store instance.
We will connect the real FAISS vector store later.
"""

_vector_store = None


def get_vector_store():
    global _vector_store
    return _vector_store


def init_vector_store():
    global _vector_store
    _vector_store = None
    return _vector_store