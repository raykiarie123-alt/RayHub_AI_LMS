import faiss
import numpy as np


class VectorStore:
    def __init__(self):
        self.index = None
        self.texts = []

    def add_embeddings(self, embeddings, texts):
        embeddings = np.array(embeddings).astype("float32")

        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)

        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)

        self.index.add(embeddings)
        self.texts.extend(texts)

    def search(self, query_embedding, k=3):
        if self.index is None or len(self.texts) == 0:
            return []

        query_embedding = np.array([query_embedding]).astype("float32")
        k = min(k, len(self.texts))
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for i in indices[0]:
            if 0 <= i < len(self.texts):
                results.append(self.texts[i])

        return results


vector_store = VectorStore()