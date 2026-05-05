from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import Optional
from app.models.gamification import GamificationProfile, Badge, UserBadge, XPLog, Streak
from app.models.user import User
from app.utils.constants import BADGES, XP_COMPLETE_TOPIC, XP_COMPLETE_QUIZ


def add_xp(
    db: Session,
    user_id: int,
    xp_amount: int,
    reason: str,
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None
):
    """Add XP to a user's profile and log it."""
    profile = db.query(GamificationProfile).filter(
        GamificationProfile.user_id == user_id
    ).first()
    if not profile:
        profile = GamificationProfile(user_id=user_id)
        db.add(profile)
        db.flush()

    profile.total_xp += xp_amount

    # Update level (every 100 XP = 1 level)
    profile.level = max(1, profile.total_xp // 100 + 1)

    # Update rank
    if profile.total_xp >= 5000:
        profile.rank = "CPA Master"
    elif profile.total_xp >= 2000:
        profile.rank = "Advanced Scholar"
    elif profile.total_xp >= 1000:
        profile.rank = "Intermediate Learner"
    elif profile.total_xp >= 500:
        profile.rank = "Active Student"
    else:
        profile.rank = "Beginner"

    # Log XP
    log = XPLog(
        user_id=user_id,
        xp_amount=xp_amount,
        reason=reason,
        reference_type=reference_type,
        reference_id=reference_id
    )
    db.add(log)
    db.commit()


def update_streak(db: Session, user_id: int):
    """Update the user's study streak."""
    streak = db.query(Streak).filter(Streak.user_id == user_id).first()
    if not streak:
        streak = Streak(user_id=user_id)
        db.add(streak)
        db.flush()

    today = date.today()
    if streak.last_study_date:
        last_date = streak.last_study_date.date() if hasattr(streak.last_study_date, 'date') else streak.last_study_date
        if last_date == today:
            return  # Already studied today
        elif last_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
    else:
        streak.current_streak = 1

    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.last_study_date = datetime.utcnow()
    db.commit()

    # Award streak XP
    add_xp(db, user_id, 15, f"Maintained {streak.current_streak}-day streak", "streak")


def check_and_award_badges(db: Session, user_id: int):
    """Check if user qualifies for any new badges and award them."""
    existing_badge_keys = {
        ub.badge.key
        for ub in db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    }

    from app.models.quiz import QuizAttempt
    from app.models.resource import Resource

    # Check first quiz badge
    if "first_quiz" not in existing_badge_keys:
        attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).count()
        if attempts >= 1:
            _award_badge(db, user_id, "first_quiz")

    # Check streak badges
    streak = db.query(Streak).filter(Streak.user_id == user_id).first()
    if streak:
        if "streak_3" not in existing_badge_keys and streak.current_streak >= 3:
            _award_badge(db, user_id, "streak_3")
        if "streak_7" not in existing_badge_keys and streak.current_streak >= 7:
            _award_badge(db, user_id, "streak_7")
        if "streak_30" not in existing_badge_keys and streak.current_streak >= 30:
            _award_badge(db, user_id, "streak_30")

    # Check top scorer badge
    if "top_scorer" not in existing_badge_keys:
        perfect = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.percentage >= 100
        ).first()
        if perfect:
            _award_badge(db, user_id, "top_scorer")

    # Check resource uploader badge
    if "resource_uploader" not in existing_badge_keys:
        uploads = db.query(Resource).filter(Resource.uploader_id == user_id).count()
        if uploads >= 5:
            _award_badge(db, user_id, "resource_uploader")

    # Check study plan creator badge
    if "study_plan_creator" not in existing_badge_keys:
        from app.models.study_plan import StudyPlan
        plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).count()
        if plans >= 1:
            _award_badge(db, user_id, "study_plan_creator")


def _award_badge(db: Session, user_id: int, badge_key: str):
    """Award a badge to a user."""
    badge = db.query(Badge).filter(Badge.key == badge_key).first()
    if not badge:
        badge_def = BADGES.get(badge_key, {})
        badge = Badge(
            key=badge_key,
            name=badge_def.get("name", badge_key),
            description=badge_def.get("description", ""),
            icon=badge_def.get("icon", ""),
            xp_reward=50
        )
        db.add(badge)
        db.flush()

    user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
    db.add(user_badge)
    db.commit()

    # Award XP for badge
    add_xp(db, user_id, badge.xp_reward, f"Earned badge: {badge.name}", "badge", badge.id)