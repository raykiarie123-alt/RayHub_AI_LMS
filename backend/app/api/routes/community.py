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
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


@router.post("/posts", status_code=201)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a community post."""
    post = CommunityPost(
        author_id=current_user.id,
        title=data.title,
        content=data.content,
        post_type=data.post_type,
        tags=data.tags,
        unit_id=data.unit_id,
        topic_id=data.topic_id
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": current_user.full_name,
        "post_type": post.post_type,
        "likes_count": post.likes_count,
        "created_at": post.created_at
    }


@router.get("/posts")
def list_posts(
    skip: int = 0,
    limit: int = 20,
    post_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List community posts."""
    query = db.query(CommunityPost).filter(CommunityPost.is_active == True)
    if post_type:
        query = query.filter(CommunityPost.post_type == post_type)
    posts = query.order_by(
        CommunityPost.is_pinned.desc(),
        CommunityPost.created_at.desc()
    ).offset(skip).limit(limit).all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "content": p.content[:300] + "..." if len(p.content) > 300 else p.content,
            "author": p.author.full_name if p.author else "Unknown",
            "post_type": p.post_type,
            "likes_count": p.likes_count,
            "comments_count": len(p.comments),
            "is_pinned": p.is_pinned,
            "created_at": p.created_at
        }
        for p in posts
    ]


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single post with comments."""
    post = db.query(CommunityPost).filter(
        CommunityPost.id == post_id,
        CommunityPost.is_active == True
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = [
        {
            "id": c.id,
            "content": c.content,
            "author": c.author.full_name if c.author else "Unknown",
            "likes_count": c.likes_count,
            "parent_id": c.parent_id,
            "created_at": c.created_at
        }
        for c in post.comments if c.is_active
    ]

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": post.author.full_name if post.author else "Unknown",
        "post_type": post.post_type,
        "tags": post.tags,
        "likes_count": post.likes_count,
        "is_pinned": post.is_pinned,
        "comments": comments,
        "created_at": post.created_at
    }


@router.post("/posts/{post_id}/comments", status_code=201)
def add_comment(
    post_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a comment to a post."""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=data.content,
        parent_id=data.parent_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "content": comment.content,
        "author": current_user.full_name,
        "created_at": comment.created_at
    }


@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Like a post."""
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
    """Delete a post."""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id and current_user.role not in ("admin", "tutor"):
        raise HTTPException(status_code=403, detail="Not authorized")
    post.is_active = False
    db.commit()
    return {"message": "Post deleted"}