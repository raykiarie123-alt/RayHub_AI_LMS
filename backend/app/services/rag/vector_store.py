import faiss
import numpy as np

from app.services.rag.embeddings import embed_texts, embed_query


class FAISSVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.stored_chunks = []

    def add_chunks(self, chunks: list[str]):
        if not chunks:
            return 0

        vectors = embed_texts(chunks)
        vectors = np.array(vectors).astype("float32")

        self.index.add(vectors)
        self.stored_chunks.extend(chunks)

        return len(chunks)

    def search_chunks(self, query: str, top_k: int = 5):
        if self.index.ntotal == 0:
            return []

        query_vector = embed_query(query)
        query_vector = np.array(query_vector).astype("float32")

        distances, indices = self.index.search(query_vector, top_k)

        results = []

        for idx in indices[0]:
            if idx != -1 and idx < len(self.stored_chunks):
                results.append(self.stored_chunks[idx])

        return results

    def clear(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.stored_chunks = []


vector_store = FAISSVectorStore()


def add_chunks(chunks: list[str]):
    return vector_store.add_chunks(chunks)


def search_chunks(query: str, top_k: int = 5):
    return vector_store.search_chunks(query, top_k)


def clear_vector_store():
    vector_store.clear()