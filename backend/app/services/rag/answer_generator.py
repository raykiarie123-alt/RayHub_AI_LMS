from typing import Dict, Optional
from app.services.ai.llm_service import call_llm
from app.services.rag.retrieval import retrieve_relevant_chunks, build_context_from_chunks
from app.services.rag.vector_store import FAISSVectorStore


CPA_SYSTEM_PROMPT = """
You are RayHub AI Tutor, an AI assistant for KASNEB CPA students.

You must only answer questions related to:
- CPA studies
- accounting
- auditing
- taxation
- financial reporting
- management accounting
- finance
- business law
- company law
- economics
- governance
- ethics
- leadership and management
- information systems audit
- public finance
- KASNEB CPA exam preparation

If the user asks anything outside CPA or professional business studies, politely refuse and say:
"I can only help with CPA-related learning questions. Please ask a question related to accounting, auditing, taxation, finance, law, governance, or CPA exam preparation."

Response style:
- Be clear and student-friendly.
- Use short paragraphs.
- Use bullets or numbered steps where helpful.
- Give CPA/KASNEB-style examples.
- Avoid unnecessary long explanations.
- If context from uploaded study material is provided, ground your answer in that context.
- Do not make up sources.
- End every valid CPA answer with a section titled "Suggested follow-up questions" and list exactly 3 related questions.
"""


async def generate_rag_answer(
    vector_store: FAISSVectorStore,
    question: str,
    resource_id: Optional[int] = None,
    top_k: int = 5
) -> Dict:
    chunks = retrieve_relevant_chunks(
        vector_store,
        question,
        top_k=top_k,
        resource_id=resource_id
    )

    if not chunks:
        answer = await call_llm(
            system_prompt=CPA_SYSTEM_PROMPT,
            user_message=(
                f"Student's question: {question}\n\n"
                "No uploaded document context was found. "
                "Answer only if the question is CPA-related."
            )
        )

        return {
            "answer": answer,
            "sources": [],
            "context_used": ""
        }

    context = build_context_from_chunks(chunks)

    user_message = f"""
Context from uploaded CPA study materials:
{context}

Student's question:
{question}

Provide a clear CPA student-friendly answer based mainly on the context above.
If the context is not enough, say what is missing instead of inventing details.
"""

    answer = await call_llm(
        system_prompt=CPA_SYSTEM_PROMPT,
        user_message=user_message
    )

    sources = [
        {
            "resource_title": c.get("resource_title", "Uploaded resource"),
            "chunk_id": c.get("chunk_id"),
            "chunk_text": (
                c.get("chunk_text", "")[:250] + "..."
                if len(c.get("chunk_text", "")) > 250
                else c.get("chunk_text", "")
            )
        }
        for c in chunks[:3]
    ]

    return {
        "answer": answer,
        "sources": sources,
        "context_used": context
    }