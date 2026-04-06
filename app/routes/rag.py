from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag.rag_service import generate_answer

router = APIRouter(prefix="/rag", tags=["RAG"])


class QueryRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: QueryRequest):
    answer = generate_answer(request.question)
    return {"answer": answer}