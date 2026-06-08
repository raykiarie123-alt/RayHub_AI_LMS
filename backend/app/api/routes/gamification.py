from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.gamification import GamificationProfile, Badge, UserBadge, XPLog, Streak
from app.models.user import User
from app.services.gamification_service import add_xp, check_and_award_badges

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/profile")
def get_gamification_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's gamification profile."""
    profile = db.query(GamificationProfile).filter(
        GamificationProfile.user_id == current_user.id
    ).first()
    streak = db.query(Streak).filter(Streak.user_id == current_user.id).first()
    badges = db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()

    return {
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "total_xp": profile.total_xp if profile else 0,
        "level": profile.level if profile else 1,
        "rank": profile.rank if profile else "Beginner",
        "current_streak": streak.current_streak if streak else 0,
        "longest_streak": streak.longest_streak if streak else 0,
        "badges_count": len(badges),
        "badges": [
            {
                "key": ub.badge.key,
                "name": ub.badge.name,
                "icon": ub.badge.icon,
                "earned_at": ub.earned_at
            }
            for ub in badges
        ]
    }


@router.post("/add-xp")
def add_xp_endpoint(
    xp_amount: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually add XP (for testing or admin use)."""
    add_xp(db, current_user.id, xp_amount, reason)
    return {"message": f"Added {xp_amount} XP", "reason": reason}


@router.get("/badges")
def get_all_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available badges and which ones the user has earned."""
    all_badges = db.query(Badge).all()
    earned_keys = {
        ub.badge.key
        for ub in db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    }
    return [
        {
            "key": b.key,
            "name": b.name,
            "description": b.description,
            "icon": b.icon,
            "xp_reward": b.xp_reward,
            "earned": b.key in earned_keys
        }
        for b in all_badges
    ]


@router.get("/streak")
def get_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's streak information."""
    streak = db.query(Streak).filter(Streak.user_id == current_user.id).first()
    return {
        "current_streak": streak.current_streak if streak else 0,
        "longest_streak": streak.longest_streak if streak else 0,
        "last_study_date": streak.last_study_date if streak else None
    }


@router.get("/leaderboard")
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the XP leaderboard."""
    profiles = db.query(GamificationProfile).order_by(
        GamificationProfile.total_xp.desc()
    ).limit(limit).all()

    leaderboard = []
    for rank, profile in enumerate(profiles, 1):
        user = db.query(User).filter(User.id == profile.user_id).first()
        leaderboard.append({
            "rank": rank,
            "user_id": profile.user_id,
            "full_name": user.full_name if user else "Unknown",
            "username": user.username if user else "unknown",
            "cpa_level": user.cpa_level if user else None,
            "student_level": user.student_level if user else "foundation",
            "total_xp": profile.total_xp,
            "level": profile.level,
            "rank_title": profile.rank,
            "is_current_user": profile.user_id == current_user.id,
        })
    return leaderboard


@router.post("/claim-badge")
def claim_badge(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check and claim any earned badges."""
    check_and_award_badges(db, current_user.id)
    return {"message": "Badges checked and awarded"}