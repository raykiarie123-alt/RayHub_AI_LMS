from app.services.rag.embeddings import get_model
from app.services.rag.vector_store import vector_store
from app.services.rag.openai_service import generate_rag_answer


def retrieve_context(query: str, k: int = 3) -> str:
    query_embedding = get_model().encode(query)
    results = vector_store.search(query_embedding, k=k)
    return "\n\n".join(results)


def generate_answer(query: str) -> str:
    context = retrieve_context(query)
    return generate_rag_answer(query, context)