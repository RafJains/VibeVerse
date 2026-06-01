from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entity import EntityType
from app.schemas.entity import (
    EntityCreditRead,
    EntityListItem,
    EntityMediaRead,
    EntityRead,
    EntityRelationRead,
)
from app.services import entity_service


router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("", response_model=list[EntityListItem])
def list_entities(
    entity_type: EntityType | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[EntityListItem]:
    return entity_service.list_entities(
        db=db,
        entity_type=entity_type,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/{entity_id}", response_model=EntityRead)
def get_entity(entity_id: int, db: Session = Depends(get_db)) -> EntityRead:
    return entity_service.get_entity_or_404(db=db, entity_id=entity_id)


@router.get("/{entity_id}/media", response_model=list[EntityMediaRead])
def get_entity_media(entity_id: int, db: Session = Depends(get_db)) -> list[EntityMediaRead]:
    return entity_service.get_entity_media(db=db, entity_id=entity_id)


@router.get("/{entity_id}/credits", response_model=list[EntityCreditRead])
def get_entity_credits(entity_id: int, db: Session = Depends(get_db)) -> list[EntityCreditRead]:
    return entity_service.get_entity_credits(db=db, entity_id=entity_id)


@router.get("/{entity_id}/related", response_model=list[EntityRelationRead])
def get_related_entities(entity_id: int, db: Session = Depends(get_db)) -> list[EntityRelationRead]:
    return entity_service.get_related_entities(db=db, entity_id=entity_id)
