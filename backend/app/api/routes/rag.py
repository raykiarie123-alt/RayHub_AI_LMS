from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai
from datetime import datetime
from typing import Optional
import os
import shutil

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.rag_chat import RAGChat
from app.services.rag.pdf_parser import extract_text_from_pdf
from app.services.rag.chunker import chunk_text
from app.services.rag.vector_store import add_chunks, search_chunks

load_dotenv()

router = APIRouter(prefix="/rag", tags=["AI Tutor"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

UPLOAD_DIR = "uploads/rag"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class AskRequest(BaseModel):
    question: str
    resource_id: Optional[int] = None
    top_k: int = 5


@router.post("/upload")
async def upload_rag_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text_from_pdf(file_path)
        if not text:
            raise HTTPException(status_code=400, detail="No readable text found in this PDF.")

        chunks = chunk_text(text)
        total_chunks = add_chunks(chunks)

        return {
            "message": "PDF uploaded, processed, and indexed successfully.",
            "filename": file.filename,
            "chunks_indexed": total_chunks,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF upload failed: {str(e)}")


@router.post("/ask")
def ask_ai_tutor(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if not client:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key missing. Add GEMINI_API_KEY to your .env file.",
            )

        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        relevant_chunks = search_chunks(request.question, top_k=request.top_k)
        context = "\n\n".join(relevant_chunks)

        prompt = f"""
You are RayHub AI Tutor, a CPA/KASNEB learning assistant.

Use the provided study context where relevant.
If the context is useful, base your answer on it.
If the context is empty or not enough, answer using your general CPA knowledge and say that no uploaded material was found for that exact question.

Study Context:
{context}

Student Question:
{request.question}

Answer using this exact format:

## Short Answer
Give a direct answer in 2-3 lines.

## Step-by-Step Explanation
Use clear bullet points or numbered steps.

## CPA Example
Give a simple CPA/KASNEB-related example.

## Exam Tip
Give one short exam-focused tip.

Rules:
- Keep answers clear and structured.
- Avoid very long paragraphs.
- Use markdown headings.
- Use bullet points.
- Do not write one huge block of text.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        answer = response.text or "I could not generate a response."

        # Persist to database
        chat_record = RAGChat(
            user_id=current_user.id,
            resource_id=request.resource_id,
            question=request.question,
            answer=answer,
            sources=relevant_chunks[:2],
            created_at=datetime.utcnow(),
        )
        db.add(chat_record)
        db.commit()
        db.refresh(chat_record)

        return {
            "answer": answer,
            "sources": relevant_chunks[:2],
            "chat_id": chat_record.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Tutor failed: {str(e)}")


@router.get("/history")
def get_rag_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chats = (
        db.query(RAGChat)
        .filter(RAGChat.user_id == current_user.id)
        .order_by(RAGChat.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": c.id,
            "question": c.question,
            "answer": c.answer,
            "sources": c.sources or [],
            "created_at": c.created_at,
        }
        for c in chats
    ]


@router.delete("/history")
def clear_rag_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(RAGChat).filter(RAGChat.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared successfully"}


@router.delete("/history/{chat_id}")
def delete_chat_history_item(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = db.query(RAGChat).filter(
        RAGChat.id == chat_id,
        RAGChat.user_id == current_user.id,
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}
