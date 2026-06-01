from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.collection import Collection, CollectionItem
from app.models.entity import Entity
from app.models.user import User
from app.schemas.collection import (
    CollectionCreate,
    CollectionItemCreate,
    CollectionItemUpdate,
    CollectionUpdate,
)


DEFAULT_COLLECTION_NAMES = {
    "watchlist": "Watchlist",
    "playlist": "Playlist",
    "favourites": "Favourites",
    "gamelist": "Gamelist",
}


def _ensure_user_exists(db: Session, user_id: int) -> None:
    if db.get(User, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


def _ensure_entity_exists(db: Session, entity_id: int) -> None:
    if db.get(Entity, entity_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )


def _default_collection_name(collection_type: str) -> str:
    return DEFAULT_COLLECTION_NAMES.get(collection_type, collection_type.replace("_", " ").title())


def _validate_collection_name(collection_type: str, name: str | None) -> str:
    if collection_type == "custom_collection" and not (name and name.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name is required for custom_collection",
        )
    return name.strip() if name and name.strip() else _default_collection_name(collection_type)


def create_collection(db: Session, payload: CollectionCreate) -> Collection:
    _ensure_user_exists(db, payload.user_id)
    collection = Collection(
        user_id=payload.user_id,
        name=_validate_collection_name(payload.collection_type, payload.name),
        description=payload.description,
        collection_type=payload.collection_type,
        visibility=payload.visibility,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def list_collections_for_user(
    db: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
) -> list[Collection]:
    _ensure_user_exists(db, user_id)
    return (
        db.query(Collection)
        .filter(Collection.user_id == user_id)
        .order_by(Collection.updated_at.desc(), Collection.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_collection_or_404(db: Session, collection_id: int) -> Collection:
    collection = db.get(Collection, collection_id)
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


def update_collection(db: Session, collection_id: int, payload: CollectionUpdate) -> Collection:
    collection = get_collection_or_404(db, collection_id)
    data = payload.model_dump(exclude_unset=True)

    next_type = data.get("collection_type", collection.collection_type)
    next_name = data.get("name", collection.name)
    if "collection_type" in data or "name" in data:
        data["name"] = _validate_collection_name(next_type, next_name)

    for field, value in data.items():
        setattr(collection, field, value)

    db.commit()
    db.refresh(collection)
    return collection


def delete_collection(db: Session, collection_id: int) -> None:
    collection = get_collection_or_404(db, collection_id)
    db.delete(collection)
    db.commit()


def add_entity_to_collection(
    db: Session,
    collection_id: int,
    payload: CollectionItemCreate,
    allow_existing: bool = False,
) -> CollectionItem:
    get_collection_or_404(db, collection_id)
    _ensure_entity_exists(db, payload.entity_id)

    existing_item = (
        db.query(CollectionItem)
        .filter(
            CollectionItem.collection_id == collection_id,
            CollectionItem.entity_id == payload.entity_id,
        )
        .one_or_none()
    )
    if existing_item is not None:
        if allow_existing:
            return existing_item
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entity is already in this collection",
        )

    item = CollectionItem(
        collection_id=collection_id,
        entity_id=payload.entity_id,
        note=payload.note,
        order_index=payload.order_index,
    )

    try:
        db.add(item)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entity is already in this collection",
        ) from exc

    db.refresh(item)
    return item


def update_collection_item(
    db: Session,
    collection_id: int,
    item_id: int,
    payload: CollectionItemUpdate,
) -> CollectionItem:
    get_collection_or_404(db, collection_id)
    item = (
        db.query(CollectionItem)
        .filter(CollectionItem.collection_id == collection_id, CollectionItem.id == item_id)
        .one_or_none()
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection item not found",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def remove_entity_from_collection(db: Session, collection_id: int, entity_id: int) -> None:
    get_collection_or_404(db, collection_id)
    item = (
        db.query(CollectionItem)
        .filter(CollectionItem.collection_id == collection_id, CollectionItem.entity_id == entity_id)
        .one_or_none()
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity is not in this collection",
        )

    db.delete(item)
    db.commit()


def list_collection_items(db: Session, collection_id: int) -> list[CollectionItem]:
    get_collection_or_404(db, collection_id)
    return (
        db.query(CollectionItem)
        .filter(CollectionItem.collection_id == collection_id)
        .order_by(CollectionItem.order_index.asc(), CollectionItem.created_at.asc())
        .all()
    )


def get_or_create_default_collection(
    db: Session,
    user_id: int,
    collection_type: str,
) -> Collection:
    _ensure_user_exists(db, user_id)
    if collection_type == "custom_collection":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="custom_collection requires explicit collection creation",
        )

    collection = (
        db.query(Collection)
        .filter(Collection.user_id == user_id, Collection.collection_type == collection_type)
        .order_by(Collection.id.asc())
        .first()
    )
    if collection is not None:
        return collection

    collection = Collection(
        user_id=user_id,
        name=_default_collection_name(collection_type),
        collection_type=collection_type,
        visibility="private",
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection
