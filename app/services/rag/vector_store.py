import faiss
import numpy as np

from app.services.rag.embeddings import embed_texts, embed_query

EMBEDDING_DIMENSION = 384

index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)

stored_chunks = []


def add_chunks(chunks: list[str]) -> int:
    if not chunks:
        return 0

    vectors = embed_texts(chunks)
    vectors = np.array(vectors).astype("float32")

    index.add(vectors)
    stored_chunks.extend(chunks)

    return len(chunks)


def search_chunks(query: str, top_k: int = 5) -> list[str]:
    if index.ntotal == 0:
        return []

    query_vector = embed_query(query)
    query_vector = np.array(query_vector).astype("float32")

    distances, indices = index.search(query_vector, top_k)

    results = []

    for idx in indices[0]:
        if idx != -1 and idx < len(stored_chunks):
            results.append(stored_chunks[idx])

    return results


def clear_vector_store():
    global index, stored_chunks

    index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
    stored_chunks = []

    return True