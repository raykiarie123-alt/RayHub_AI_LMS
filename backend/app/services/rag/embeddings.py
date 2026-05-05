from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings

_model: SentenceTransformer = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    """Embed a list of texts and return numpy array of embeddings."""
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string."""
    model = get_embedding_model()
    embedding = model.encode([query], convert_to_numpy=True, show_progress_bar=False)
    return embedding[0]


def get_embedding_dimension() -> int:
    """Return the embedding dimension for the current model."""
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()