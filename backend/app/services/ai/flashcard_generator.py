import json
from typing import Optional
from sqlalchemy.orm import Session
from app.services.ai.llm_service import call_llm_json
from app.services.ai.prompt_templates import FLASHCARD_SYSTEM_PROMPT, FLASHCARD_PROMPT
from app.models.flashcard import Flashcard
from app.models.course import Topic, Unit
from app.models.resource import Resource


async def generate_flashcards(
    db: Session,
    creator_id: int,
    topic_id: Optional[int],
    unit_id: Optional[int],
    resource_id: Optional[int],
    num_cards: int
) -> list:
    """Generate AI flashcards and save to database."""

    # Get topic/unit name
    topic_name = "CPA Accounting"
    if topic_id:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if topic:
            topic_name = topic.title
    elif unit_id:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if unit:
            topic_name = unit.title

    # Get context
    context = ""
    if resource_id:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if resource and resource.content_text:
            context = f"\nBase flashcards on this material:\n{resource.content_text[:3000]}"
    elif topic_id:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if topic and topic.content:
            context = f"\nBase flashcards on this content:\n{topic.content[:2000]}"

    prompt = FLASHCARD_PROMPT.format(
        num_cards=num_cards,
        topic=topic_name,
        context=context
    )

    raw_json = await call_llm_json(
        system_prompt=FLASHCARD_SYSTEM_PROMPT,
        user_message=prompt
    )

    data = json.loads(raw_json)
    flashcards = []

    for card_data in data.get("flashcards", []):
        card = Flashcard(
            creator_id=creator_id,
            topic_id=topic_id,
            unit_id=unit_id,
            resource_id=resource_id,
            front=card_data.get("front", ""),
            back=card_data.get("back", ""),
            is_ai_generated=True,
            is_public=True
        )
        db.add(card)
        flashcards.append(card)

    db.commit()
    for card in flashcards:
        db.refresh(card)

    return flashcards