from fastapi import APIRouter
from app.services.ai_router import generate_ai_response

router = APIRouter()

@router.post("/chat")
def chat(message: str):
    response = generate_ai_response(message)
    return {"response": response}