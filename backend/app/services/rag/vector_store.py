import os
import json
import numpy as np
import faiss
from typing import List, Tuple, Optional, Dict
from app.core.config import settings
from app.services.rag.embeddings import get_embedding_dimension


class FAISSVectorStore:
    """
    FAISS-based vector store for storing and retrieving document embeddings.
    Maintains a metadata mapping alongside the FAISS index.
    """

    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        self.meta_path = settings.FAISS_INDEX_PATH + "_meta.json"
        self.dimension = get_embedding_dimension()
        self.index: Optional[faiss.IndexFlatL2] = None
        self.metadata: List[Dict] = []  # List of {resource_id, chunk_id, chunk_text}
        self._load_or_create()

    def _load_or_create(self):
        """Load existing index or create a new one."""
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "r") as f:
                    self.metadata = json.load(f)
                return
            except Exception:
                pass
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []

    def _save(self):
        """Persist the index and metadata to disk."""
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else ".", exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w") as f:
            json.dump(self.metadata, f)

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        meta_list: List[Dict]
    ) -> List[int]:
        """
        Add embeddings and their metadata to the store.
        Returns list of FAISS internal IDs (indices).
        """
        if len(embeddings) == 0:
            return []
        embeddings = embeddings.astype(np.float32)
        start_id = len(self.metadata)
        self.index.add(embeddings)
        self.metadata.extend(meta_list)
        self._save()
        return list(range(start_id, start_id + len(meta_list)))

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        resource_id: Optional[int] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Search for the most similar chunks.
        Optionally filter by resource_id.
        Returns list of (metadata, distance) tuples.
        """
        if self.index.ntotal == 0:
            return []

        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        # Fetch more results if filtering
        fetch_k = min(top_k * 10 if resource_id else top_k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, fetch_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            if resource_id and meta.get("resource_id") != resource_id:
                continue
            results.append((meta, float(dist)))
            if len(results) >= top_k:
                break

        return results

    def delete_by_resource(self, resource_id: int):
        """
        Remove all vectors for a given resource.
        FAISS flat index doesn't support deletion natively — rebuild without those entries.
        """
        from app.services.rag.embeddings import embed_texts
        remaining_meta = [m for m in self.metadata if m.get("resource_id") != resource_id]
        if len(remaining_meta) == len(self.metadata):
            return  # Nothing to delete

        # Rebuild index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []

        if remaining_meta:
            texts = [m["chunk_text"] for m in remaining_meta]
            embeddings = embed_texts(texts).astype(np.float32)
            self.index.add(embeddings)
            self.metadata = remaining_meta

        self._save()

    def get_total_vectors(self) -> int:
        return self.index.ntotal if self.index else 0