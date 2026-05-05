from typing import List, Dict, Optional
from app.services.ai.llm_service import call_llm
from app.services.rag.retrieval import retrieve_relevant_chunks, build_context_from_chunks
from app.services.rag.vector_store import FAISSVectorStore


async def generate_rag_answer(
    vector_store: FAISSVectorStore,
    question: str,
    resource_id: Optional[int] = None,
    top_k: int = 5
) -> Dict:
    """
    Full RAG pipeline: retrieve relevant chunks, build context, generate answer.
    Returns dict with answer and sources.
    """
    chunks = retrieve_relevant_chunks(vector_store, question, top_k=top_k, resource_id=resource_id)

    if not chunks:
        # Fallback to general LLM without context
        answer = await call_llm(
            system_prompt="You are an expert CPA tutor. Answer the student's question clearly and concisely.",
            user_message=question
        )
        return {
            "answer": answer,
            "sources": [],
            "context_used": ""
        }

    context = build_context_from_chunks(chunks)

    system_prompt = """You are an expert CPA tutor and AI assistant for RayHub AI LMS.
You help CPA students understand complex accounting, audit, tax, and finance concepts.

Use the provided context from the student's study materials to answer their question.
If the answer is in the context, cite the source. If not fully covered, supplement with your knowledge.
Be clear, structured, and educational in your response."""

    user_message = f"""Context from study materials:
{context}

Student's question: {question}

Please provide a clear, comprehensive answer based on the context above."""

    answer = await call_llm(system_prompt=system_prompt, user_message=user_message)

    sources = [
        {
            "resource_title": c["resource_title"],
            "chunk_id": c["chunk_id"],
            "chunk_text": c["chunk_text"][:200] + "..." if len(c["chunk_text"]) > 200 else c["chunk_text"]
        }
        for c in chunks[:3]
    ]

    return {
        "answer": answer,
        "sources": sources,
        "context_used": context
    }