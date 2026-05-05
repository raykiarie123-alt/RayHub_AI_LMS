from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class QuizGenerateRequest(BaseModel):
    topic_id: Optional[int] = None
    unit_id: Optional[int] = None
    resource_id: Optional[int] = None
    difficulty: Optional[str] = "intermediate"
    number_of_questions: Optional[int] = 10
    question_type: Optional[str] = "mcq"
    title: Optional[str] = None


class QuestionBase(BaseModel):
    question_text: str
    question_type: str = "mcq"
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    marks: Optional[int] = 1


class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    order: int

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    topic_id: Optional[int] = None
    unit_id: Optional[int] = None
    difficulty: Optional[str] = "intermediate"
    question_type: Optional[str] = "mcq"
    time_limit_minutes: Optional[int] = None


class QuizResponse(QuizBase):
    id: int
    is_ai_generated: bool
    is_active: bool
    questions: Optional[List[QuestionResponse]] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuizSubmitRequest(BaseModel):
    answers: List[dict]  # [{"question_id": 1, "answer": "A"}]
    time_taken_seconds: Optional[int] = None


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    score: float
    total_marks: int
    percentage: float
    is_completed: bool
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FlashcardGenerateRequest(BaseModel):
    topic_id: Optional[int] = None
    unit_id: Optional[int] = None
    resource_id: Optional[int] = None
    number_of_cards: Optional[int] = 10


class FlashcardBase(BaseModel):
    front: str
    back: str
    topic_id: Optional[int] = None
    unit_id: Optional[int] = None
    is_public: Optional[bool] = True


class FlashcardResponse(FlashcardBase):
    id: int
    is_ai_generated: bool
    review_count: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FlashcardReviewRequest(BaseModel):
    flashcard_id: int
    quality: int  # 0-5 rating for spaced repetition
    