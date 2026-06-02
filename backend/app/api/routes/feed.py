from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.feed import (
    FeedCardCreate,
    FeedCardEntityRead,
    FeedCardListItem,
    FeedCardRead,
    FeedCardUpdate,
    TrendingScoreRead,
)
from app.services import feed_service
from app.services.auth_service import get_current_user


router = APIRouter(tags=["feed"])
ADMIN_ROLES = {"admin", "super_admin"}


def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role in ADMIN_ROLES:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only admins can manage global feed cards",
    )


@router.get("/feed/global", response_model=list[FeedCardListItem])
def list_global_feed(
    region: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[FeedCardListItem]:
    return feed_service.list_global_feed(
        db=db,
        region=region,
        limit=limit,
        offset=offset,
    )


@router.get("/feed/cards/{feed_card_id}", response_model=FeedCardRead)
def get_public_feed_card(feed_card_id: int, db: Session = Depends(get_db)) -> FeedCardRead:
    return feed_service.get_public_feed_card_or_404(db=db, feed_card_id=feed_card_id)


@router.get("/feed/trending-scores", response_model=list[TrendingScoreRead])
def list_trending_scores(
    score_type: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[TrendingScoreRead]:
    return feed_service.list_trending_scores(
        db=db,
        score_type=score_type,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/admin/feed-cards",
    response_model=FeedCardRead,
    status_code=status.HTTP_201_CREATED,
)
def create_feed_card(
    payload: FeedCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> FeedCardRead:
    return feed_service.create_feed_card(db=db, payload=payload, current_user=current_user)


@router.patch("/admin/feed-cards/{feed_card_id}", response_model=FeedCardRead)
def update_feed_card(
    feed_card_id: int,
    payload: FeedCardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> FeedCardRead:
    return feed_service.update_feed_card(
        db=db,
        feed_card_id=feed_card_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete("/admin/feed-cards/{feed_card_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_feed_card(
    feed_card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> None:
    feed_service.delete_or_archive_feed_card(
        db=db,
        feed_card_id=feed_card_id,
        current_user=current_user,
    )


@router.post("/admin/feed-cards/{feed_card_id}/approve", response_model=FeedCardRead)
def approve_feed_card(
    feed_card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> FeedCardRead:
    return feed_service.approve_feed_card(
        db=db,
        feed_card_id=feed_card_id,
        current_user=current_user,
    )


@router.post("/admin/feed-cards/{feed_card_id}/reject", response_model=FeedCardRead)
def reject_feed_card(
    feed_card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> FeedCardRead:
    return feed_service.reject_feed_card(
        db=db,
        feed_card_id=feed_card_id,
        current_user=current_user,
    )


@router.post("/admin/feed-cards/{feed_card_id}/publish", response_model=FeedCardRead)
def publish_feed_card(
    feed_card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> FeedCardRead:
    return feed_service.publish_feed_card(
        db=db,
        feed_card_id=feed_card_id,
        current_user=current_user,
    )


@router.post(
    "/admin/feed-cards/{feed_card_id}/entities/{entity_id}",
    response_model=FeedCardEntityRead,
    status_code=status.HTTP_201_CREATED,
)
def add_entity_to_feed_card(
    feed_card_id: int,
    entity_id: int,
    order_index: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> FeedCardEntityRead:
    return feed_service.add_entity_to_feed_card(
        db=db,
        feed_card_id=feed_card_id,
        entity_id=entity_id,
        order_index=order_index,
    )


@router.delete(
    "/admin/feed-cards/{feed_card_id}/entities/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_entity_from_feed_card(
    feed_card_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> None:
    feed_service.remove_entity_from_feed_card(
        db=db,
        feed_card_id=feed_card_id,
        entity_id=entity_id,
    )
