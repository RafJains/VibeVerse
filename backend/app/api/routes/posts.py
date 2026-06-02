from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.post import (
    CommunityBlockedWordCreate,
    CommunityBlockedWordRead,
    CommunityPostCreate,
    CommunityPostListItem,
    CommunityPostRead,
    CommunityPostUpdate,
    PostModerationActionRead,
    PostReportCreate,
    PostReportRead,
)
from app.services import post_service
from app.services.auth_service import get_current_user


router = APIRouter(tags=["posts"])


@router.post(
    "/communities/{community_id}/posts",
    response_model=CommunityPostRead,
    status_code=status.HTTP_201_CREATED,
)
def create_community_post(
    community_id: int,
    payload: CommunityPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityPostRead:
    return post_service.create_post(
        db=db,
        community_id=community_id,
        payload=payload,
        current_user=current_user,
    )


@router.get("/communities/{community_id}/posts", response_model=list[CommunityPostListItem])
def list_community_posts(
    community_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[CommunityPostListItem]:
    return post_service.list_posts_for_community(
        db=db,
        community_id=community_id,
        include_hidden=False,
        limit=limit,
        offset=offset,
    )


@router.get("/posts/{post_id}", response_model=CommunityPostRead)
def get_post(post_id: int, db: Session = Depends(get_db)) -> CommunityPostRead:
    return post_service.get_post_or_404(db=db, post_id=post_id)


@router.patch("/posts/{post_id}", response_model=CommunityPostRead)
def update_post(
    post_id: int,
    payload: CommunityPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityPostRead:
    return post_service.update_post(
        db=db,
        post_id=post_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    post_service.delete_or_remove_post(db=db, post_id=post_id, current_user=current_user)


@router.post(
    "/posts/{post_id}/report",
    response_model=PostReportRead,
    status_code=status.HTTP_201_CREATED,
)
def report_post(
    post_id: int,
    payload: PostReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostReportRead:
    return post_service.report_post(
        db=db,
        post_id=post_id,
        payload=payload,
        current_user=current_user,
    )


@router.post("/posts/{post_id}/hide", response_model=PostModerationActionRead)
def hide_post(
    post_id: int,
    reason: str | None = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostModerationActionRead:
    return post_service.hide_post(
        db=db,
        post_id=post_id,
        reason=reason,
        current_user=current_user,
    )


@router.post("/posts/{post_id}/unhide", response_model=PostModerationActionRead)
def unhide_post(
    post_id: int,
    reason: str | None = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostModerationActionRead:
    return post_service.unhide_post(
        db=db,
        post_id=post_id,
        reason=reason,
        current_user=current_user,
    )


@router.post(
    "/communities/{community_id}/blocked-words",
    response_model=CommunityBlockedWordRead,
    status_code=status.HTTP_201_CREATED,
)
def add_blocked_word(
    community_id: int,
    payload: CommunityBlockedWordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityBlockedWordRead:
    return post_service.add_blocked_word(
        db=db,
        community_id=community_id,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/communities/{community_id}/blocked-words",
    response_model=list[CommunityBlockedWordRead],
)
def list_blocked_words(
    community_id: int,
    db: Session = Depends(get_db),
) -> list[CommunityBlockedWordRead]:
    return post_service.list_blocked_words(db=db, community_id=community_id)


@router.delete(
    "/communities/{community_id}/blocked-words/{blocked_word_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_blocked_word(
    community_id: int,
    blocked_word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    post_service.delete_blocked_word(
        db=db,
        community_id=community_id,
        blocked_word_id=blocked_word_id,
        current_user=current_user,
    )
