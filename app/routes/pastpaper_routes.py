from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import PastPaper, PastPaperSubmission
from app.schemas.pastpaper_schema import PastPaperCreate, PastPaperSubmissionCreate

router = APIRouter(prefix="/pastpapers", tags=["Past Papers"])

@router.post("/")
def create_past_paper(past_paper: PastPaperCreate, db: Session = Depends(get_db)):
    new_past_paper = PastPaper(
        title=past_paper.title,
        course_id=past_paper.course_id,
        exam_year = past_paper.exam_year,
    )
    db.add(new_past_paper)
    db.commit()
    db.refresh(new_past_paper)

    return new_past_paper

#student view past papers
@router.get("/")
def get_past_papers(db: Session = Depends(get_db)):
    past_papers = db.query(PastPaper).all()
    return past_papers

#student submit past paper answers
@router.post("/submit")
def submit_past_paper_answers(submission: PastPaperSubmissionCreate, db: Session = Depends(get_db)):
    new_submission = PastPaperSubmission(
        user_id=1,
        past_paper_id=submission.past_paper_id,
        answers_text=submission.answers_text
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return {"message": "Past paper answers submitted successfully"}