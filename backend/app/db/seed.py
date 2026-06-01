import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.entity import (
    Entity,
    EntityCredit,
    EntityMedia,
    EntityRelation,
    EntityTag,
    EntityType,
)


def get_or_create_entity(
    db: Session,
    *,
    name: str,
    entity_type: EntityType,
    description: str,
    image_url: str | None = None,
    banner_url: str | None = None,
    popularity_score: float = 0.0,
) -> Entity:
    entity = (
        db.query(Entity)
        .filter(Entity.name == name, Entity.entity_type == entity_type)
        .one_or_none()
    )
    if entity is not None:
        return entity

    entity = Entity(
        name=name,
        entity_type=entity_type,
        description=description,
        image_url=image_url,
        banner_url=banner_url,
        status="published",
        popularity_score=popularity_score,
    )
    db.add(entity)
    db.flush()
    return entity


def add_tag_if_missing(db: Session, entity: Entity, tag: str) -> None:
    exists = (
        db.query(EntityTag)
        .filter(EntityTag.entity_id == entity.id, EntityTag.tag == tag)
        .one_or_none()
    )
    if exists is None:
        db.add(EntityTag(entity_id=entity.id, tag=tag))


def add_media_if_missing(
    db: Session,
    entity: Entity,
    *,
    media_type: str,
    title: str,
    url: str,
    source_name: str,
) -> None:
    exists = (
        db.query(EntityMedia)
        .filter(EntityMedia.entity_id == entity.id, EntityMedia.url == url)
        .one_or_none()
    )
    if exists is None:
        db.add(
            EntityMedia(
                entity_id=entity.id,
                media_type=media_type,
                title=title,
                url=url,
                source_name=source_name,
            )
        )


def add_credit_if_missing(
    db: Session,
    entity: Entity,
    person: Entity,
    *,
    role: str,
    character_name: str | None = None,
    order_index: int = 0,
) -> None:
    exists = (
        db.query(EntityCredit)
        .filter(
            EntityCredit.entity_id == entity.id,
            EntityCredit.person_entity_id == person.id,
            EntityCredit.role == role,
        )
        .one_or_none()
    )
    if exists is None:
        db.add(
            EntityCredit(
                entity_id=entity.id,
                person_entity_id=person.id,
                role=role,
                character_name=character_name,
                order_index=order_index,
            )
        )


def add_relation_if_missing(
    db: Session,
    source: Entity,
    target: Entity,
    *,
    relation_type: str,
) -> None:
    exists = (
        db.query(EntityRelation)
        .filter(
            EntityRelation.source_entity_id == source.id,
            EntityRelation.target_entity_id == target.id,
            EntityRelation.relation_type == relation_type,
        )
        .one_or_none()
    )
    if exists is None:
        db.add(
            EntityRelation(
                source_entity_id=source.id,
                target_entity_id=target.id,
                relation_type=relation_type,
            )
        )


def seed_entities() -> None:
    db = SessionLocal()
    try:
        inception = get_or_create_entity(
            db,
            name="Inception",
            entity_type=EntityType.FILM,
            description="A sci-fi heist film about dream infiltration and layered realities.",
            popularity_score=95.0,
        )
        demon_slayer = get_or_create_entity(
            db,
            name="Demon Slayer",
            entity_type=EntityType.SERIES,
            description="An anime series following Tanjiro Kamado's fight against demons.",
            popularity_score=92.0,
        )
        blinding_lights = get_or_create_entity(
            db,
            name="Blinding Lights",
            entity_type=EntityType.SONG,
            description="A synth-pop song by The Weeknd from the After Hours era.",
            popularity_score=94.0,
        )
        after_hours = get_or_create_entity(
            db,
            name="After Hours",
            entity_type=EntityType.ALBUM,
            description="A studio album by The Weeknd featuring a dark synth-pop sound.",
            popularity_score=90.0,
        )
        christopher_nolan = get_or_create_entity(
            db,
            name="Christopher Nolan",
            entity_type=EntityType.PERSON,
            description="A filmmaker known for large-scale, high-concept films.",
            popularity_score=93.0,
        )

        add_tag_if_missing(db, inception, "sci-fi")
        add_tag_if_missing(db, demon_slayer, "anime")
        add_tag_if_missing(db, blinding_lights, "synth-pop")
        add_tag_if_missing(db, after_hours, "pop")
        add_tag_if_missing(db, christopher_nolan, "director")

        add_media_if_missing(
            db,
            inception,
            media_type="trailer",
            title="Inception Official Trailer",
            url="https://www.youtube.com/watch?v=YoHD9XEInc0",
            source_name="youtube",
        )
        add_media_if_missing(
            db,
            blinding_lights,
            media_type="music_video",
            title="Blinding Lights Official Video",
            url="https://www.youtube.com/watch?v=4NRXx6U8ABQ",
            source_name="youtube",
        )

        add_credit_if_missing(db, inception, christopher_nolan, role="director", order_index=1)
        add_relation_if_missing(
            db,
            after_hours,
            blinding_lights,
            relation_type="includes_song",
        )

        db.commit()
        print("Seed data inserted successfully.")
    except SQLAlchemyError as exc:
        db.rollback()
        print(f"Seed failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_entities()
