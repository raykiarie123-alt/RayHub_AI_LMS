from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.vector_store_instance import get_vector_store

from app.models.rag_chat import RAGChat
from app.models.user import User

from app.schemas.rag_schema import (
    RAGAskRequest,
    RAGAskResponse,
    RAGChatResponse
)

from app.services.rag.answer_generator import generate_rag_answer

router = APIRouter(
    prefix="/rag",
    tags=["RAG AI Tutor"]
)

CPA_KEYWORDS = [
    "cpa", "kasneb", "accounting", "accountant", "audit", "auditing",
    "assurance", "tax", "taxation", "vat", "income tax", "corporate tax",
    "finance", "financial", "ifrs", "ias", "financial reporting",
    "bookkeeping", "double entry", "trial balance", "ledger",
    "management accounting", "cost accounting", "budget", "budgeting",
    "variance", "company law", "business law", "governance", "ethics",
    "public finance", "economics", "leadership", "management",
    "strategy", "risk", "internal control", "fraud", "information systems",
    "it audit", "forensic audit", "exam", "revision", "study plan"
]


def is_cpa_related(question: str) -> bool:
    q = question.lower()
    return any(keyword in q for keyword in CPA_KEYWORDS)


@router.post("/ask", response_model=RAGAskResponse)
async def ask_ai(
    data: RAGAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ask the AI tutor a question.
    Searches across indexed learning resources.
    """

    if not is_cpa_related(data.question):
        return RAGAskResponse(
            answer=(
                "I can only help with CPA-related learning questions. "
                "Please ask a question related to accounting, auditing, "
                "taxation, finance, law, governance, business studies, "
                "or CPA exam preparation."
            ),
            sources=[],
            question=data.question
        )

    vs = get_vector_store()

    # Prevent crashes if vector store is not initialized
    if vs is None:
        return RAGAskResponse(
            answer=(
                "AI Tutor is not ready yet because the vector "
                "store has not been initialized. "
                "Please upload and index learning resources first."
            ),
            sources=[],
            question=data.question
        )

    # Generate AI answer
    result = await generate_rag_answer(
        vector_store=vs,
        question=data.question,
        resource_id=data.resource_id,
        top_k=data.top_k or 5
    )

    # Save chat history
    chat = RAGChat(
        user_id=current_user.id,
        resource_id=data.resource_id,
        topic_id=data.topic_id,
        question=data.question,
        answer=result["answer"],
        sources=result["sources"],
        context_used=result.get("context_used", "")[:2000]
    )

    db.add(chat)
    db.commit()

    return RAGAskResponse(
        answer=result["answer"],
        sources=result["sources"],
        question=data.question
    )


@router.post("/ask-resource", response_model=RAGAskResponse)
async def ask_about_resource(
    data: RAGAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ask a question about a specific resource."""

    if not data.resource_id:
        raise HTTPException(
            status_code=400,
            detail="resource_id is required"
        )

    return await ask_ai(data, db, current_user)


@router.post("/ask-topic", response_model=RAGAskResponse)
async def ask_about_topic(
    data: RAGAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ask a question about a specific topic."""

    if not data.topic_id:
        raise HTTPException(
            status_code=400,
            detail="topic_id is required"
        )

    return await ask_ai(data, db, current_user)


@router.get("/history", response_model=List[RAGChatResponse])
def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's AI tutor chat history."""

    chats = (
        db.query(RAGChat)
        .filter(RAGChat.user_id == current_user.id)
        .order_by(RAGChat.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return chats


@router.delete("/history/{chat_id}")
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a chat history entry."""

    chat = (
        db.query(RAGChat)
        .filter(
            RAGChat.id == chat_id,
            RAGChat.user_id == current_user.id
        )
        .first()
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted"}