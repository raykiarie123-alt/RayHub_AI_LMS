from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.community import CommunityPost, Comment
from app.models.user import User

router = APIRouter(prefix="/community", tags=["Community"])


class PostCreate(BaseModel):
    title: str
    content: str
    post_type: Optional[str] = "discussion"
    tags: Optional[List[str]] = None
    cpa_level: Optional[str] = None
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None
    mentions: Optional[List[str]] = None  # list of @usernames mentioned


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None
    mentions: Optional[List[str]] = None


def _user_info(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "cpa_level": user.cpa_level or user.student_level or "Foundation",
        "student_level": user.student_level or "foundation",
    }


@router.post("/posts", status_code=201)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = CommunityPost(
        author_id=current_user.id,
        title=data.title,
        content=data.content,
        post_type=data.post_type,
        tags=data.tags,
        unit_id=data.unit_id,
        topic_id=data.topic_id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": current_user.full_name,
        "author_info": _user_info(current_user),
        "post_type": post.post_type,
        "likes_count": post.likes_count,
        "comments_count": 0,
        "created_at": post.created_at,
    }


@router.get("/posts")
def list_posts(
    skip: int = 0,
    limit: int = 30,
    post_type: Optional[str] = None,
    cpa_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(CommunityPost).filter(CommunityPost.is_active == True)
    if post_type:
        query = query.filter(CommunityPost.post_type == post_type)
    posts = query.order_by(
        CommunityPost.is_pinned.desc(),
        CommunityPost.created_at.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for p in posts:
        author = p.author
        author_cpa_level = None
        if author:
            author_cpa_level = author.cpa_level or author.student_level or "Foundation"
        # Filter by cpa_level if provided
        if cpa_level and author and (author.student_level or "foundation").lower() != cpa_level.lower():
            continue
        result.append({
            "id": p.id,
            "title": p.title,
            "content": p.content[:300] + "..." if len(p.content) > 300 else p.content,
            "author": author.full_name if author else "Unknown",
            "author_username": author.username if author else None,
            "author_cpa_level": author_cpa_level,
            "author_student_level": author.student_level if author else None,
            "post_type": p.post_type,
            "likes_count": p.likes_count,
            "comments_count": len(p.comments),
            "is_pinned": p.is_pinned,
            "tags": p.tags or [],
            "created_at": p.created_at,
        })
    return result


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(CommunityPost).filter(
        CommunityPost.id == post_id,
        CommunityPost.is_active == True
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = []
    for c in sorted(post.comments, key=lambda x: x.created_at):
        if not c.is_active:
            continue
        comment_author = c.author
        comments.append({
            "id": c.id,
            "content": c.content,
            "author": comment_author.full_name if comment_author else "Unknown",
            "author_username": comment_author.username if comment_author else None,
            "author_cpa_level": comment_author.cpa_level if comment_author else None,
            "author_student_level": comment_author.student_level if comment_author else None,
            "likes_count": c.likes_count,
            "parent_id": c.parent_id,
            "created_at": c.created_at,
        })

    author = post.author
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": author.full_name if author else "Unknown",
        "author_username": author.username if author else None,
        "author_cpa_level": author.cpa_level if author else None,
        "author_student_level": author.student_level if author else None,
        "post_type": post.post_type,
        "tags": post.tags or [],
        "likes_count": post.likes_count,
        "is_pinned": post.is_pinned,
        "comments": comments,
        "created_at": post.created_at,
    }


@router.post("/posts/{post_id}/comments", status_code=201)
def add_comment(
    post_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=data.content,
        parent_id=data.parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "content": comment.content,
        "author": current_user.full_name,
        "author_username": current_user.username,
        "author_cpa_level": current_user.cpa_level,
        "author_student_level": current_user.student_level,
        "created_at": comment.created_at,
    }


@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.likes_count += 1
    db.commit()
    return {"likes_count": post.likes_count}


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id and current_user.role not in ("admin", "tutor"):
        raise HTTPException(status_code=403, detail="Not authorized")
    post.is_active = False
    db.commit()
    return {"message": "Post deleted"}


@router.get("/users/search")
def search_users(
    q: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search users by username or name for @mentions."""
    if len(q) < 2:
        return []
    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) | (User.full_name.ilike(f"%{q}%")),
        User.is_active == True,
    ).limit(10).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "cpa_level": u.cpa_level or u.student_level or "Foundation",
            "student_level": u.student_level or "foundation",
        }
        for u in users
    ]
