import re

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.community import Community, CommunityMember
from app.models.post import (
    CommunityBlockedWord,
    CommunityPost,
    PostModerationAction,
    PostReport,
)
from app.models.user import User
from app.schemas.post import (
    CommunityBlockedWordCreate,
    CommunityPostCreate,
    CommunityPostUpdate,
    PostReportCreate,
)


ADMIN_ROLES = {"admin", "super_admin"}
MODERATOR_ROLES = {"owner", "moderator"}


def _is_admin(user: User) -> bool:
    return user.role in ADMIN_ROLES


def _get_community_or_404(db: Session, community_id: int) -> Community:
    community = db.get(Community, community_id)
    if community is None or community.status == "hidden":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )
    return community


def _ensure_approved_community(community: Community) -> None:
    if community.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Posts can only be created inside approved communities",
        )


def _get_active_membership(
    db: Session,
    community_id: int,
    user_id: int,
) -> CommunityMember | None:
    return (
        db.query(CommunityMember)
        .filter(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == user_id,
            CommunityMember.status == "active",
        )
        .one_or_none()
    )


def _ensure_active_member(db: Session, community: Community, current_user: User) -> CommunityMember:
    membership = _get_active_membership(db, community.id, current_user.id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an active community member to post",
        )
    return membership


def _is_community_moderator(db: Session, community: Community, current_user: User) -> bool:
    if _is_admin(current_user) or community.owner_user_id == current_user.id:
        return True

    membership = _get_active_membership(db, community.id, current_user.id)
    return membership is not None and membership.role in MODERATOR_ROLES


def _ensure_can_moderate_community(
    db: Session,
    community: Community,
    current_user: User,
) -> None:
    if _is_community_moderator(db, community, current_user):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to moderate this community",
    )


def _ensure_can_moderate(db: Session, post: CommunityPost, current_user: User) -> None:
    _ensure_can_moderate_community(db, post.community, current_user)


def _ensure_can_update(post: CommunityPost, current_user: User) -> None:
    if post.author_user_id == current_user.id or _is_admin(current_user):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to modify this post",
    )


def _ensure_can_remove(db: Session, post: CommunityPost, current_user: User) -> None:
    if post.author_user_id == current_user.id or _is_community_moderator(
        db,
        post.community,
        current_user,
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to remove this post",
    )


def _get_existing_post(db: Session, post_id: int) -> CommunityPost | None:
    return db.get(CommunityPost, post_id)


def get_post_or_404(db: Session, post_id: int) -> CommunityPost:
    post = _get_existing_post(db, post_id)
    if post is None or post.status == "removed" or post.community.status == "hidden":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


def _clean_moderation_reason(reason: str | None) -> str | None:
    if reason is None:
        return None
    stripped = reason.strip()
    return stripped or None


def _ensure_no_blocked_words(
    db: Session,
    community_id: int,
    title: str | None,
    body: str | None,
) -> None:
    combined_text = " ".join(part for part in (title, body) if part).lower()
    if not combined_text:
        return

    blocked_words = (
        db.query(CommunityBlockedWord)
        .filter(CommunityBlockedWord.community_id == community_id)
        .all()
    )
    for blocked_word in blocked_words:
        pattern = rf"(?<!\w){re.escape(blocked_word.word.lower())}(?!\w)"
        if re.search(pattern, combined_text):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post contains a blocked word for this community",
            )


def _create_moderation_action(
    db: Session,
    post: CommunityPost,
    action_type: str,
    reason: str | None,
    current_user: User,
) -> PostModerationAction:
    action = PostModerationAction(
        post_id=post.id,
        moderator_user_id=current_user.id,
        action_type=action_type,
        reason=_clean_moderation_reason(reason),
    )
    db.add(action)
    return action


def create_post(
    db: Session,
    community_id: int,
    payload: CommunityPostCreate,
    current_user: User,
) -> CommunityPost:
    community = _get_community_or_404(db, community_id)
    _ensure_approved_community(community)
    _ensure_active_member(db, community, current_user)
    _ensure_no_blocked_words(db, community.id, payload.title, payload.body)

    post = CommunityPost(
        community_id=community.id,
        author_user_id=current_user.id,
        post_type=payload.post_type,
        title=payload.title,
        body=payload.body,
        media_url=payload.media_url,
        spoiler=payload.spoiler,
        status="published",
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def list_posts_for_community(
    db: Session,
    community_id: int,
    include_hidden: bool = False,
    limit: int = 20,
    offset: int = 0,
) -> list[CommunityPost]:
    community = _get_community_or_404(db, community_id)
    if community.status != "approved":
        return []

    query = db.query(CommunityPost).filter(CommunityPost.community_id == community.id)
    if include_hidden:
        query = query.filter(CommunityPost.status != "removed")
    else:
        query = query.filter(CommunityPost.status == "published")

    return query.order_by(CommunityPost.created_at.desc()).offset(offset).limit(limit).all()


def update_post(
    db: Session,
    post_id: int,
    payload: CommunityPostUpdate,
    current_user: User,
) -> CommunityPost:
    post = get_post_or_404(db, post_id)
    _ensure_can_update(post, current_user)

    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title cannot be null",
        )

    next_title = data.get("title", post.title)
    next_body = data.get("body", post.body)
    _ensure_no_blocked_words(db, post.community_id, next_title, next_body)

    for field, value in data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


def delete_or_remove_post(db: Session, post_id: int, current_user: User) -> None:
    post = get_post_or_404(db, post_id)
    _ensure_can_remove(db, post, current_user)
    post.status = "removed"
    if post.author_user_id != current_user.id:
        _create_moderation_action(
            db=db,
            post=post,
            action_type="remove",
            reason="Removed by moderator",
            current_user=current_user,
        )
    db.commit()


def report_post(
    db: Session,
    post_id: int,
    payload: PostReportCreate,
    current_user: User,
) -> PostReport:
    post = get_post_or_404(db, post_id)
    report = PostReport(
        post_id=post.id,
        reporter_user_id=current_user.id,
        reason=payload.reason,
        details=payload.details,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def hide_post(
    db: Session,
    post_id: int,
    reason: str | None,
    current_user: User,
) -> PostModerationAction:
    post = get_post_or_404(db, post_id)
    _ensure_can_moderate(db, post, current_user)
    if post.status == "hidden":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Post is already hidden",
        )
    post.status = "hidden"
    action = _create_moderation_action(
        db=db,
        post=post,
        action_type="hide",
        reason=reason,
        current_user=current_user,
    )
    db.commit()
    db.refresh(action)
    return action


def unhide_post(
    db: Session,
    post_id: int,
    reason: str | None,
    current_user: User,
) -> PostModerationAction:
    post = get_post_or_404(db, post_id)
    _ensure_can_moderate(db, post, current_user)
    if post.status == "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Post is already published",
        )
    post.status = "published"
    action = _create_moderation_action(
        db=db,
        post=post,
        action_type="unhide",
        reason=reason,
        current_user=current_user,
    )
    db.commit()
    db.refresh(action)
    return action


def add_blocked_word(
    db: Session,
    community_id: int,
    payload: CommunityBlockedWordCreate,
    current_user: User,
) -> CommunityBlockedWord:
    community = _get_community_or_404(db, community_id)
    _ensure_can_moderate_community(db, community, current_user)

    blocked_word = CommunityBlockedWord(
        community_id=community.id,
        word=payload.word,
        created_by_user_id=current_user.id,
    )
    try:
        db.add(blocked_word)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Blocked word already exists for this community",
        ) from exc

    db.refresh(blocked_word)
    return blocked_word


def list_blocked_words(db: Session, community_id: int) -> list[CommunityBlockedWord]:
    community = _get_community_or_404(db, community_id)
    return (
        db.query(CommunityBlockedWord)
        .filter(CommunityBlockedWord.community_id == community.id)
        .order_by(CommunityBlockedWord.word.asc())
        .all()
    )


def delete_blocked_word(
    db: Session,
    community_id: int,
    blocked_word_id: int,
    current_user: User,
) -> None:
    community = _get_community_or_404(db, community_id)
    _ensure_can_moderate_community(db, community, current_user)
    blocked_word = (
        db.query(CommunityBlockedWord)
        .filter(
            CommunityBlockedWord.community_id == community.id,
            CommunityBlockedWord.id == blocked_word_id,
        )
        .one_or_none()
    )
    if blocked_word is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blocked word not found",
        )

    db.delete(blocked_word)
    db.commit()
