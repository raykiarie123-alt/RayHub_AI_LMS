from typing import List, Dict, Optional, Tuple
from app.services.rag.embeddings import embed_query
from app.services.rag.vector_store import FAISSVectorStore
from app.utils.constants import MAX_CHUNKS_PER_RETRIEVAL


def retrieve_relevant_chunks(
    vector_store: FAISSVectorStore,
    query: str,
    top_k: int = MAX_CHUNKS_PER_RETRIEVAL,
    resource_id: Optional[int] = None
) -> List[Dict]:
    """
    Retrieve the most relevant chunks for a given query.
    Returns list of metadata dicts with chunk_text, resource_id, chunk_id.
    """
    query_embedding = embed_query(query)
    results = vector_store.search(query_embedding, top_k=top_k, resource_id=resource_id)

    chunks = []
    for meta, distance in results:
        chunks.append({
            "chunk_id": meta.get("chunk_id"),
            "resource_id": meta.get("resource_id"),
            "resource_title": meta.get("resource_title", "Unknown"),
            "chunk_text": meta.get("chunk_text", ""),
            "distance": distance
        })

    return chunks


def build_context_from_chunks(chunks: List[Dict], max_tokens: int = 3000) -> str:
    """
    Build a context string from retrieved chunks for LLM input.
    Truncates to approximate token limit.
    """
    context_parts = []
    total_chars = 0
    max_chars = max_tokens * 4  # Approximate: 1 token ≈ 4 chars

    for i, chunk in enumerate(chunks):
        text = chunk.get("chunk_text", "")
        source = chunk.get("resource_title", "Unknown Source")
        part = f"[Source: {source}]\n{text}"
        if total_chars + len(part) > max_chars:
            break
        context_parts.append(part)
        total_chars += len(part)

    return "\n\n---\n\n".join(context_parts)


