from app.services.rag.vector_store import FAISSVectorStore

vector_store = None


def init_vector_store():
    global vector_store

    if vector_store is None:
        vector_store = FAISSVectorStore()

    return vector_store


def get_vector_store():
    global vector_store

    if vector_store is None:
        vector_store = FAISSVectorStore()

    return vector_store