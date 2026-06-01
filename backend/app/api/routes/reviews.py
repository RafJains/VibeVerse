from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.review import (
    EntityRatingSummary,
    ReviewCreate,
    ReviewListItem,
    ReviewRead,
    ReviewReportCreate,
    ReviewReportRead,
    ReviewUpdate,
)
from app.services import review_service


router = APIRouter(tags=["reviews"])


@router.post("/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)) -> ReviewRead:
    return review_service.create_review(db=db, payload=payload)


@router.get("/reviews/entity/{entity_id}", response_model=list[ReviewListItem])
def list_reviews_for_entity(
    entity_id: int,
    include_spoilers: bool = Query(default=True),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ReviewListItem]:
    return review_service.list_reviews_for_entity(
        db=db,
        entity_id=entity_id,
        include_spoilers=include_spoilers,
        limit=limit,
        offset=offset,
    )


@router.get("/entities/{entity_id}/reviews", response_model=list[ReviewListItem])
def list_entity_reviews(
    entity_id: int,
    include_spoilers: bool = Query(default=True),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ReviewListItem]:
    return review_service.list_reviews_for_entity(
        db=db,
        entity_id=entity_id,
        include_spoilers=include_spoilers,
        limit=limit,
        offset=offset,
    )


@router.get("/reviews/user/{user_id}", response_model=list[ReviewListItem])
def list_reviews_for_user(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ReviewListItem]:
    return review_service.list_reviews_for_user(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )


@router.get("/reviews/{review_id}", response_model=ReviewRead)
def get_review(review_id: int, db: Session = Depends(get_db)) -> ReviewRead:
    return review_service.get_review_or_404(db=db, review_id=review_id)


@router.patch("/reviews/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
) -> ReviewRead:
    return review_service.update_review(db=db, review_id=review_id, payload=payload)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db)) -> None:
    review_service.delete_review(db=db, review_id=review_id)


@router.post("/reviews/{review_id}/report", response_model=ReviewReportRead, status_code=status.HTTP_201_CREATED)
def report_review(
    review_id: int,
    payload: ReviewReportCreate,
    db: Session = Depends(get_db),
) -> ReviewReportRead:
    return review_service.report_review(db=db, review_id=review_id, payload=payload)


@router.get("/entities/{entity_id}/rating-summary", response_model=EntityRatingSummary)
def get_entity_rating_summary(
    entity_id: int,
    db: Session = Depends(get_db),
) -> EntityRatingSummary:
    return review_service.get_entity_rating_summary(db=db, entity_id=entity_id)
