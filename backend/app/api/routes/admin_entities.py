from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.entity import EntityCreate, EntityRead, EntityUpdate
from app.services import entity_service


router = APIRouter(prefix="/admin/entities", tags=["admin entities"])


@router.post("", response_model=EntityRead, status_code=status.HTTP_201_CREATED)
def create_entity(payload: EntityCreate, db: Session = Depends(get_db)) -> EntityRead:
    return entity_service.create_entity(db=db, payload=payload)


@router.patch("/{entity_id}", response_model=EntityRead)
def update_entity(
    entity_id: int,
    payload: EntityUpdate,
    db: Session = Depends(get_db),
) -> EntityRead:
    return entity_service.update_entity(db=db, entity_id=entity_id, payload=payload)


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(entity_id: int, db: Session = Depends(get_db)) -> None:
    entity_service.delete_entity(db=db, entity_id=entity_id)
