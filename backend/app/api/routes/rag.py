from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from datetime import datetime
import os
import shutil

from app.services.rag.pdf_parser import extract_text_from_pdf
from app.services.rag.chunker import chunk_text
from app.services.rag.vector_store import add_chunks, search_chunks

load_dotenv()

router = APIRouter(prefix="/rag", tags=["AI Tutor"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

UPLOAD_DIR = "uploads/rag"
os.makedirs(UPLOAD_DIR, exist_ok=True)

chat_history = []


class AskRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_rag_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed.",
            )

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text_from_pdf(file_path)

        if not text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in this PDF.",
            )

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
        print("PDF Upload Error:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"PDF upload failed: {str(e)}",
        )


@router.post("/ask")
def ask_ai_tutor(request: AskRequest):
    try:
        if not client:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key missing. Add GEMINI_API_KEY to your .env file.",
            )

        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty.",
            )

        relevant_chunks = search_chunks(request.question, top_k=5)

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

        chat_item = {
            "id": len(chat_history) + 1,
            "question": request.question,
            "answer": answer,
            "sources": relevant_chunks[:2],
            "created_at": datetime.utcnow().isoformat(),
        }

        chat_history.append(chat_item)

        return {
            "answer": answer,
            "sources": relevant_chunks[:2],
            "chat_id": chat_item["id"],
        }

    except HTTPException:
        raise

    except Exception as e:
        print("AI Tutor Error:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"AI Tutor failed: {str(e)}",
        )


@router.get("/history")
def get_rag_history():
    return chat_history


@router.delete("/history")
def clear_rag_history():
    chat_history.clear()
    return {
        "message": "Chat history cleared successfully",
    }


@router.delete("/history/{chat_id}")
def delete_chat_history_item(chat_id: int):
    global chat_history

    chat_exists = any(chat["id"] == chat_id for chat in chat_history)

    if not chat_exists:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

    chat_history = [chat for chat in chat_history if chat["id"] != chat_id]

    return {
        "message": "Chat deleted successfully",
    }