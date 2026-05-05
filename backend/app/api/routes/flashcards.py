from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.flashcard import Flashcard
from app.models.user import User
from app.schemas.quiz_schema import FlashcardGenerateRequest, FlashcardResponse, FlashcardBase, FlashcardReviewRequest
from app.services.ai.flashcard_generator import generate_flashcards

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


@router.post("/generate", response_model=List[FlashcardResponse], status_code=201)
async def generate_flashcards_endpoint(
    data: FlashcardGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI flashcards for a topic or resource."""
    cards = await generate_flashcards(
        db=db,
        creator_id=current_user.id,
        topic_id=data.topic_id,
        unit_id=data.unit_id,
        resource_id=data.resource_id,
        num_cards=data.number_of_cards or 10
    )
    return cards


@router.get("/", response_model=List[FlashcardResponse])
def list_flashcards(
    topic_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List flashcards."""
    query = db.query(Flashcard).filter(
        (Flashcard.creator_id == current_user.id) | (Flashcard.is_public == True)
    )
    if topic_id:
        query = query.filter(Flashcard.topic_id == topic_id)
    if unit_id:
        query = query.filter(Flashcard.unit_id == unit_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{flashcard_id}", response_model=FlashcardResponse)
def get_flashcard(
    flashcard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return card


@router.put("/{flashcard_id}", response_model=FlashcardResponse)
def update_flashcard(
    flashcard_id: int,
    data: FlashcardBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.creator_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(card, field, value)
    db.commit()
    db.refresh(card)
    return card


@router.delete("/{flashcard_id}")
def delete_flashcard(
    flashcard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.creator_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    db.delete(card)
    db.commit()
    return {"message": "Flashcard deleted"}


@router.post("/review")
def review_flashcard(
    data: FlashcardReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a flashcard review with spaced repetition."""
    card = db.query(Flashcard).filter(Flashcard.id == data.flashcard_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # Simple SM-2 spaced repetition
    quality = max(0, min(5, data.quality))
    card.review_count += 1

    if quality >= 3:
        if card.review_count == 1:
            card.interval_days = 1
        elif card.review_count == 2:
            card.interval_days = 6
        else:
            card.interval_days = int(card.interval_days * card.ease_factor)
        card.ease_factor = max(1.3, card.ease_factor + 0.1 - (5 - quality) * 0.08)
    else:
        card.interval_days = 1
        card.ease_factor = max(1.3, card.ease_factor - 0.2)

    card.next_review_date = datetime.utcnow() + timedelta(days=card.interval_days)
    db.commit()

    from app.services.gamification_service import add_xp
    add_xp(db, current_user.id, 5, "Reviewed a flashcard", "flashcard", card.id)

    return {"message": "Review recorded", "next_review_days": card.interval_days}


