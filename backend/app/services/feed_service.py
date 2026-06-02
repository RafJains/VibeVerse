from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.models.feed import FeedCard, FeedCardEntity, TrendingScore
from app.models.user import User
from app.schemas.feed import FeedCardCreate, FeedCardUpdate


ADMIN_ROLES = {"admin", "super_admin"}
PUBLIC_STATUSES = {"approved", "published"}


def _ensure_admin(current_user: User) -> None:
    if current_user.role in ADMIN_ROLES:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only admins can manage global feed cards",
    )


def _ensure_entity_exists(db: Session, entity_id: int) -> Entity:
    entity = db.get(Entity, entity_id)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )
    return entity


def _active_feed_filter(query):
    now = datetime.now(timezone.utc)
    return query.filter(
        FeedCard.status.in_(PUBLIC_STATUSES),
        or_(FeedCard.scheduled_at.is_(None), FeedCard.scheduled_at <= now),
        or_(FeedCard.expires_at.is_(None), FeedCard.expires_at > now),
    )


def _apply_feed_order(query):
    return query.order_by(
        FeedCard.priority.desc(),
        FeedCard.approved_at.desc().nullslast(),
        FeedCard.created_at.desc(),
    )


def list_global_feed(
    db: Session,
    region: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[FeedCard]:
    query = _active_feed_filter(db.query(FeedCard))
    if region:
        query = query.filter(FeedCard.region == region)
    return _apply_feed_order(query).offset(offset).limit(limit).all()


def get_feed_card_or_404(db: Session, feed_card_id: int) -> FeedCard:
    feed_card = db.get(FeedCard, feed_card_id)
    if feed_card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed card not found",
        )
    return feed_card


def get_public_feed_card_or_404(db: Session, feed_card_id: int) -> FeedCard:
    feed_card = (
        _active_feed_filter(db.query(FeedCard).filter(FeedCard.id == feed_card_id))
        .one_or_none()
    )
    if feed_card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed card not found",
        )
    return feed_card


def create_feed_card(db: Session, payload: FeedCardCreate, current_user: User) -> FeedCard:
    _ensure_admin(current_user)
    feed_card = FeedCard(
        title=payload.title,
        subtitle=payload.subtitle,
        body=payload.body,
        card_type=payload.card_type,
        status=payload.status,
        image_url=payload.image_url,
        source_type=payload.source_type,
        source_url=payload.source_url,
        priority=payload.priority,
        region=payload.region,
        created_by_user_id=current_user.id,
        scheduled_at=payload.scheduled_at,
        expires_at=payload.expires_at,
    )
    db.add(feed_card)
    db.flush()

    seen_entity_ids: set[int] = set()
    for order_index, entity_id in enumerate(payload.linked_entity_ids):
        if entity_id in seen_entity_ids:
            continue
        seen_entity_ids.add(entity_id)
        _ensure_entity_exists(db, entity_id)
        db.add(
            FeedCardEntity(
                feed_card_id=feed_card.id,
                entity_id=entity_id,
                order_index=order_index,
            )
        )

    db.commit()
    db.refresh(feed_card)
    return feed_card


def update_feed_card(
    db: Session,
    feed_card_id: int,
    payload: FeedCardUpdate,
    current_user: User,
) -> FeedCard:
    _ensure_admin(current_user)
    feed_card = get_feed_card_or_404(db, feed_card_id)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(feed_card, field, value)

    db.commit()
    db.refresh(feed_card)
    return feed_card


def delete_or_archive_feed_card(db: Session, feed_card_id: int, current_user: User) -> None:
    _ensure_admin(current_user)
    feed_card = get_feed_card_or_404(db, feed_card_id)
    feed_card.status = "archived"
    db.commit()


def approve_feed_card(db: Session, feed_card_id: int, current_user: User) -> FeedCard:
    _ensure_admin(current_user)
    feed_card = get_feed_card_or_404(db, feed_card_id)
    feed_card.status = "approved"
    feed_card.approved_by_user_id = current_user.id
    feed_card.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(feed_card)
    return feed_card


def reject_feed_card(db: Session, feed_card_id: int, current_user: User) -> FeedCard:
    _ensure_admin(current_user)
    feed_card = get_feed_card_or_404(db, feed_card_id)
    feed_card.status = "rejected"
    db.commit()
    db.refresh(feed_card)
    return feed_card


def publish_feed_card(db: Session, feed_card_id: int, current_user: User) -> FeedCard:
    _ensure_admin(current_user)
    feed_card = get_feed_card_or_404(db, feed_card_id)
    if feed_card.approved_by_user_id is None:
        feed_card.approved_by_user_id = current_user.id
        feed_card.approved_at = datetime.now(timezone.utc)
    feed_card.status = "published"
    db.commit()
    db.refresh(feed_card)
    return feed_card


def add_entity_to_feed_card(
    db: Session,
    feed_card_id: int,
    entity_id: int,
    order_index: int = 0,
) -> FeedCardEntity:
    get_feed_card_or_404(db, feed_card_id)
    _ensure_entity_exists(db, entity_id)
    link = FeedCardEntity(
        feed_card_id=feed_card_id,
        entity_id=entity_id,
        order_index=order_index,
    )
    try:
        db.add(link)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entity is already linked to this feed card",
        ) from exc

    db.refresh(link)
    return link


def remove_entity_from_feed_card(db: Session, feed_card_id: int, entity_id: int) -> None:
    get_feed_card_or_404(db, feed_card_id)
    link = (
        db.query(FeedCardEntity)
        .filter(
            FeedCardEntity.feed_card_id == feed_card_id,
            FeedCardEntity.entity_id == entity_id,
        )
        .one_or_none()
    )
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed card entity link not found",
        )
    db.delete(link)
    db.commit()


def list_trending_scores(
    db: Session,
    score_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[TrendingScore]:
    query = db.query(TrendingScore)
    if score_type:
        query = query.filter(TrendingScore.score_type == score_type)
    return (
        query.order_by(TrendingScore.score.desc(), TrendingScore.calculated_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
