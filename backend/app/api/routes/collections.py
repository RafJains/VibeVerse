from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.collection import (
    CollectionCreate,
    CollectionItemCreate,
    CollectionItemRead,
    CollectionItemUpdate,
    CollectionListItem,
    CollectionRead,
    CollectionUpdate,
)
from app.services import collection_service


router = APIRouter(tags=["collections"])


@router.post("/collections", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
def create_collection(payload: CollectionCreate, db: Session = Depends(get_db)) -> CollectionRead:
    return collection_service.create_collection(db=db, payload=payload)


@router.get("/collections/user/{user_id}", response_model=list[CollectionListItem])
def list_collections_for_user(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[CollectionListItem]:
    return collection_service.list_collections_for_user(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )


@router.get("/collections/{collection_id}", response_model=CollectionRead)
def get_collection(collection_id: int, db: Session = Depends(get_db)) -> CollectionRead:
    return collection_service.get_collection_or_404(db=db, collection_id=collection_id)


@router.patch("/collections/{collection_id}", response_model=CollectionRead)
def update_collection(
    collection_id: int,
    payload: CollectionUpdate,
    db: Session = Depends(get_db),
) -> CollectionRead:
    return collection_service.update_collection(
        db=db,
        collection_id=collection_id,
        payload=payload,
    )


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(collection_id: int, db: Session = Depends(get_db)) -> None:
    collection_service.delete_collection(db=db, collection_id=collection_id)


@router.post(
    "/collections/{collection_id}/items",
    response_model=CollectionItemRead,
    status_code=status.HTTP_201_CREATED,
)
def add_entity_to_collection(
    collection_id: int,
    payload: CollectionItemCreate,
    db: Session = Depends(get_db),
) -> CollectionItemRead:
    return collection_service.add_entity_to_collection(
        db=db,
        collection_id=collection_id,
        payload=payload,
    )


@router.get("/collections/{collection_id}/items", response_model=list[CollectionItemRead])
def list_collection_items(
    collection_id: int,
    db: Session = Depends(get_db),
) -> list[CollectionItemRead]:
    return collection_service.list_collection_items(db=db, collection_id=collection_id)


@router.patch("/collections/{collection_id}/items/{item_id}", response_model=CollectionItemRead)
def update_collection_item(
    collection_id: int,
    item_id: int,
    payload: CollectionItemUpdate,
    db: Session = Depends(get_db),
) -> CollectionItemRead:
    return collection_service.update_collection_item(
        db=db,
        collection_id=collection_id,
        item_id=item_id,
        payload=payload,
    )


@router.delete("/collections/{collection_id}/items/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_entity_from_collection(
    collection_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
) -> None:
    collection_service.remove_entity_from_collection(
        db=db,
        collection_id=collection_id,
        entity_id=entity_id,
    )


@router.post("/users/{user_id}/watchlist/{entity_id}", response_model=CollectionItemRead)
def save_to_watchlist(
    user_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
) -> CollectionItemRead:
    collection = collection_service.get_or_create_default_collection(
        db=db,
        user_id=user_id,
        collection_type="watchlist",
    )
    return collection_service.add_entity_to_collection(
        db=db,
        collection_id=collection.id,
        payload=CollectionItemCreate(entity_id=entity_id),
        allow_existing=True,
    )


@router.delete("/users/{user_id}/watchlist/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    user_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
) -> None:
    collection = collection_service.get_or_create_default_collection(
        db=db,
        user_id=user_id,
        collection_type="watchlist",
    )
    collection_service.remove_entity_from_collection(
        db=db,
        collection_id=collection.id,
        entity_id=entity_id,
    )


@router.post("/users/{user_id}/favourites/{entity_id}", response_model=CollectionItemRead)
def save_to_favourites(
    user_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
) -> CollectionItemRead:
    collection = collection_service.get_or_create_default_collection(
        db=db,
        user_id=user_id,
        collection_type="favourites",
    )
    return collection_service.add_entity_to_collection(
        db=db,
        collection_id=collection.id,
        payload=CollectionItemCreate(entity_id=entity_id),
        allow_existing=True,
    )


@router.delete("/users/{user_id}/favourites/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_favourites(
    user_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
) -> None:
    collection = collection_service.get_or_create_default_collection(
        db=db,
        user_id=user_id,
        collection_type="favourites",
    )
    collection_service.remove_entity_from_collection(
        db=db,
        collection_id=collection.id,
        entity_id=entity_id,
    )
