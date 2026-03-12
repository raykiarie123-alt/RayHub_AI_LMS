from pydantic import BaseModel
from typing import List


class QuizCreate(BaseModel):
    topic_id: int
    title: str


class QuestionCreate(BaseModel):
    quiz_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str


class AnswerSubmission(BaseModel):
    question_id: int
    selected_option: str


class QuizSubmission(BaseModel):
    quiz_id: int
    answers: List[AnswerSubmission]
