from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.entity import Entity, EntityCredit, EntityMedia, EntityRelation, EntityTag, EntityType
from app.schemas.entity import EntityCreate, EntityUpdate


def _clean_tags(tags: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        normalized = tag.strip().lower()
        if normalized and normalized not in seen:
            cleaned.append(normalized)
            seen.add(normalized)
    return cleaned


def _replace_entity_tags(db: Session, entity: Entity, tags: list[str]) -> None:
    db.query(EntityTag).filter(EntityTag.entity_id == entity.id).delete(synchronize_session=False)
    for tag in _clean_tags(tags):
        db.add(EntityTag(entity_id=entity.id, tag=tag))


def list_entities(
    db: Session,
    entity_type: EntityType | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Entity]:
    query = db.query(Entity)

    if entity_type is not None:
        query = query.filter(Entity.entity_type == entity_type)

    if search:
        query = query.filter(Entity.name.ilike(f"%{search.strip()}%"))

    return (
        query.order_by(Entity.popularity_score.desc(), Entity.name.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_entity_or_404(db: Session, entity_id: int) -> Entity:
    entity = db.get(Entity, entity_id)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )
    return entity


def create_entity(db: Session, payload: EntityCreate) -> Entity:
    data = payload.model_dump()
    tags = data.pop("tags", [])

    entity = Entity(**data)
    db.add(entity)
    db.flush()
    _replace_entity_tags(db, entity, tags)

    db.commit()
    db.refresh(entity)
    return entity


def update_entity(db: Session, entity_id: int, payload: EntityUpdate) -> Entity:
    entity = get_entity_or_404(db, entity_id)
    data = payload.model_dump(exclude_unset=True)
    tags = data.pop("tags", None)

    for field, value in data.items():
        setattr(entity, field, value)

    if tags is not None:
        _replace_entity_tags(db, entity, tags)

    db.commit()
    db.refresh(entity)
    return entity


def delete_entity(db: Session, entity_id: int) -> None:
    entity = get_entity_or_404(db, entity_id)
    db.delete(entity)
    db.commit()


def get_entity_media(db: Session, entity_id: int) -> list[EntityMedia]:
    get_entity_or_404(db, entity_id)
    return (
        db.query(EntityMedia)
        .filter(EntityMedia.entity_id == entity_id)
        .order_by(EntityMedia.created_at.asc())
        .all()
    )


def get_entity_credits(db: Session, entity_id: int) -> list[EntityCredit]:
    get_entity_or_404(db, entity_id)
    return (
        db.query(EntityCredit)
        .filter(EntityCredit.entity_id == entity_id)
        .order_by(EntityCredit.order_index.asc(), EntityCredit.id.asc())
        .all()
    )


def get_related_entities(db: Session, entity_id: int) -> list[EntityRelation]:
    get_entity_or_404(db, entity_id)
    return (
        db.query(EntityRelation)
        .filter(
            or_(
                EntityRelation.source_entity_id == entity_id,
                EntityRelation.target_entity_id == entity_id,
            )
        )
        .order_by(EntityRelation.created_at.asc())
        .all()
    )
