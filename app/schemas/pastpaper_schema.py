from pydantic import BaseModel

class PastPaperCreate(BaseModel):
    title: str
    course_id: int
    content: str

class PastPaperSubmissionCreate(BaseModel):
    past_paper_id: int
    answers_text: str
