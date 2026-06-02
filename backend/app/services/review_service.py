from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.models.review import Review, ReviewEditHistory, ReviewReport, ReviewTag
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewReportCreate, ReviewUpdate


ADMIN_ROLES = {"admin", "super_admin"}


def _clean_tags(tags: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        normalized = tag.strip().lower()
        if normalized and normalized not in seen:
            cleaned.append(normalized)
            seen.add(normalized)
    return cleaned


def _replace_review_tags(db: Session, review: Review, tags: list[str]) -> None:
    db.query(ReviewTag).filter(ReviewTag.review_id == review.id).delete(synchronize_session=False)
    for tag in _clean_tags(tags):
        db.add(ReviewTag(review_id=review.id, tag=tag))


def _ensure_entity_exists(db: Session, entity_id: int) -> None:
    if db.get(Entity, entity_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )


def _ensure_user_exists(db: Session, user_id: int) -> None:
    if db.get(User, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


def _can_manage_review(review: Review, user: User) -> bool:
    return review.user_id == user.id or user.role in ADMIN_ROLES


def _ensure_can_manage_review(review: Review, user: User) -> None:
    if not _can_manage_review(review, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this review",
        )


def create_review(db: Session, payload: ReviewCreate, user_id: int) -> Review:
    _ensure_entity_exists(db, payload.entity_id)
    _ensure_user_exists(db, user_id)

    existing_review = (
        db.query(Review)
        .filter(Review.entity_id == payload.entity_id, Review.user_id == user_id)
        .one_or_none()
    )
    if existing_review is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User has already reviewed this entity",
        )

    data = payload.model_dump()
    tags = data.pop("tags", [])
    review = Review(**data, user_id=user_id)

    try:
        db.add(review)
        db.flush()
        _replace_review_tags(db, review, tags)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User has already reviewed this entity",
        ) from exc

    db.refresh(review)
    return review


def list_reviews_for_entity(
    db: Session,
    entity_id: int,
    include_spoilers: bool = True,
    limit: int = 20,
    offset: int = 0,
) -> list[Review]:
    _ensure_entity_exists(db, entity_id)
    query = db.query(Review).filter(Review.entity_id == entity_id, Review.is_deleted.is_(False))

    if not include_spoilers:
        query = query.filter(Review.spoiler.is_(False))

    return query.order_by(Review.created_at.desc()).offset(offset).limit(limit).all()


def list_reviews_for_user(
    db: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
) -> list[Review]:
    _ensure_user_exists(db, user_id)
    return (
        db.query(Review)
        .filter(Review.user_id == user_id, Review.is_deleted.is_(False))
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_review_or_404(db: Session, review_id: int) -> Review:
    review = db.get(Review, review_id)
    if review is None or review.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    return review


def update_review(db: Session, review_id: int, payload: ReviewUpdate, current_user: User) -> Review:
    review = get_review_or_404(db, review_id)
    _ensure_can_manage_review(review, current_user)
    data = payload.model_dump(exclude_unset=True)
    tags = data.pop("tags", None)

    if data or tags is not None:
        db.add(
            ReviewEditHistory(
                review_id=review.id,
                previous_rating=review.rating,
                previous_title=review.title,
                previous_body=review.body,
                previous_spoiler=review.spoiler,
                previous_visibility=review.visibility,
                previous_attachment_url=review.attachment_url,
            )
        )

    for field, value in data.items():
        setattr(review, field, value)

    if tags is not None:
        _replace_review_tags(db, review, tags)

    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int, current_user: User) -> None:
    review = get_review_or_404(db, review_id)
    _ensure_can_manage_review(review, current_user)
    review.is_deleted = True
    db.commit()


def report_review(db: Session, review_id: int, payload: ReviewReportCreate, reporter_user_id: int) -> ReviewReport:
    review = get_review_or_404(db, review_id)
    _ensure_user_exists(db, reporter_user_id)

    report = ReviewReport(
        review_id=review.id,
        reporter_user_id=reporter_user_id,
        reason=payload.reason,
        details=payload.details,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_entity_rating_summary(db: Session, entity_id: int) -> dict[str, int | float | None]:
    _ensure_entity_exists(db, entity_id)

    average_rating, rating_count = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(Review.entity_id == entity_id, Review.is_deleted.is_(False))
        .one()
    )
    count = int(rating_count or 0)

    return {
        "entity_id": entity_id,
        "average_rating": round(float(average_rating), 2) if average_rating is not None else None,
        "review_count": count,
        "rating_count": count,
    }
