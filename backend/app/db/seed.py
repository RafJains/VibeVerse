import sys

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import hash_password, verify_password
from app.models.collection import Collection, CollectionItem
from app.models.community import Community, CommunityMember, CommunityRule
from app.models.entity import (
    Entity,
    EntityCredit,
    EntityMedia,
    EntityRelation,
    EntityTag,
    EntityType,
)
from app.models.review import Review, ReviewTag
from app.models.user import Profile, User


def password_matches(password: str, hashed_password: str | None) -> bool:
    if not hashed_password:
        return False
    try:
        return verify_password(password, hashed_password)
    except (TypeError, ValueError):
        return False


def get_or_create_user(
    db: Session,
    *,
    email: str,
    username: str,
    password: str,
    role: str = "normal_user",
) -> User:
    user = db.query(User).filter(User.username == username).one_or_none()
    if user is not None:
        user.email = email
        user.role = role
        user.is_active = True
        if not password_matches(password, user.hashed_password):
            user.hashed_password = hash_password(password)
        if user.profile is None:
            db.add(Profile(user_id=user.id, display_name=user.username))
        return user

    user = db.query(User).filter(User.email == email).one_or_none()
    if user is not None:
        user.username = username
        user.role = role
        user.is_active = True
        if not password_matches(password, user.hashed_password):
            user.hashed_password = hash_password(password)
        if user.profile is None:
            db.add(Profile(user_id=user.id, display_name=user.username))
        return user

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.flush()
    db.add(Profile(user_id=user.id, display_name=user.username))
    return user


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


def add_review_tag_if_missing(db: Session, review: Review, tag: str) -> None:
    exists = (
        db.query(ReviewTag)
        .filter(ReviewTag.review_id == review.id, ReviewTag.tag == tag)
        .one_or_none()
    )
    if exists is None:
        db.add(ReviewTag(review_id=review.id, tag=tag))


def add_review_if_missing(
    db: Session,
    *,
    entity: Entity,
    user: User,
    rating: float,
    title: str,
    body: str,
    tags: list[str],
    spoiler: bool = False,
    visibility: str = "public",
) -> Review:
    review = (
        db.query(Review)
        .filter(Review.entity_id == entity.id, Review.user_id == user.id)
        .one_or_none()
    )
    if review is None:
        review = Review(
            entity_id=entity.id,
            user_id=user.id,
            rating=rating,
            title=title,
            body=body,
            spoiler=spoiler,
            visibility=visibility,
            is_deleted=False,
        )
        db.add(review)
        db.flush()

    for tag in tags:
        add_review_tag_if_missing(db, review, tag)

    return review


def get_or_create_collection(
    db: Session,
    *,
    user: User,
    collection_type: str,
    name: str,
    description: str | None = None,
    visibility: str = "private",
) -> Collection:
    collection = (
        db.query(Collection)
        .filter(
            Collection.user_id == user.id,
            Collection.collection_type == collection_type,
            Collection.name == name,
        )
        .one_or_none()
    )
    if collection is not None:
        return collection

    collection = Collection(
        user_id=user.id,
        name=name,
        description=description,
        collection_type=collection_type,
        visibility=visibility,
    )
    db.add(collection)
    db.flush()
    return collection


def add_collection_item_if_missing(
    db: Session,
    *,
    collection: Collection,
    entity: Entity,
    note: str | None = None,
    order_index: int = 0,
) -> CollectionItem:
    item = (
        db.query(CollectionItem)
        .filter(
            CollectionItem.collection_id == collection.id,
            CollectionItem.entity_id == entity.id,
        )
        .one_or_none()
    )
    if item is not None:
        return item

    item = CollectionItem(
        collection_id=collection.id,
        entity_id=entity.id,
        note=note,
        order_index=order_index,
    )
    db.add(item)
    db.flush()
    return item


def get_or_create_community(
    db: Session,
    *,
    name: str,
    slug: str,
    community_type: str,
    owner: User,
    entity: Entity | None = None,
    description: str | None = None,
) -> Community:
    community = db.query(Community).filter(Community.slug == slug).one_or_none()
    if community is not None:
        community.name = name
        community.community_type = community_type
        community.owner_user_id = owner.id
        community.entity_id = entity.id if entity is not None else None
        community.description = description
        community.status = "approved"
        return community

    community = Community(
        name=name,
        slug=slug,
        community_type=community_type,
        owner_user_id=owner.id,
        entity_id=entity.id if entity is not None else None,
        description=description,
        status="approved",
        member_count=0,
    )
    db.add(community)
    db.flush()
    return community


def add_community_member_if_missing(
    db: Session,
    *,
    community: Community,
    user: User,
    role: str = "member",
    status: str = "active",
) -> CommunityMember:
    member = (
        db.query(CommunityMember)
        .filter(
            CommunityMember.community_id == community.id,
            CommunityMember.user_id == user.id,
        )
        .one_or_none()
    )
    if member is not None:
        member.role = role
        member.status = status
        return member

    member = CommunityMember(
        community_id=community.id,
        user_id=user.id,
        role=role,
        status=status,
    )
    db.add(member)
    db.flush()
    return member


def add_community_rule_if_missing(
    db: Session,
    *,
    community: Community,
    title: str,
    description: str | None = None,
    order_index: int = 0,
) -> None:
    exists = (
        db.query(CommunityRule)
        .filter(CommunityRule.community_id == community.id, CommunityRule.title == title)
        .one_or_none()
    )
    if exists is None:
        db.add(
            CommunityRule(
                community_id=community.id,
                title=title,
                description=description,
                order_index=order_index,
            )
        )


def sync_community_member_count(db: Session, community: Community) -> None:
    community.member_count = (
        db.query(CommunityMember)
        .filter(
            CommunityMember.community_id == community.id,
            CommunityMember.status == "active",
        )
        .count()
    )


def seed_entities() -> None:
    db = SessionLocal()
    try:
        demo_user = get_or_create_user(
            db,
            email="demo@vibeverse.local",
            username="demo_user",
            password="demo12345",
        )
        critic_user = get_or_create_user(
            db,
            email="critic@vibeverse.local",
            username="critic_user",
            password="critic12345",
            role="verified_user",
        )

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

        add_review_if_missing(
            db,
            entity=inception,
            user=critic_user,
            rating=4.5,
            title="A layered blockbuster",
            body="A precise, memorable sci-fi thriller with strong momentum and visual clarity.",
            tags=["sci-fi", "mind-bending"],
        )
        add_review_if_missing(
            db,
            entity=demon_slayer,
            user=demo_user,
            rating=4.0,
            title="High-energy anime",
            body="A visually striking series with emotional stakes and standout action sequences.",
            tags=["anime", "action"],
            spoiler=False,
        )
        add_review_if_missing(
            db,
            entity=blinding_lights,
            user=demo_user,
            rating=5.0,
            title="Instant synth-pop classic",
            body="A polished track with a sharp hook and strong replay value.",
            tags=["synth-pop", "replayable"],
        )

        demo_watchlist = get_or_create_collection(
            db,
            user=demo_user,
            collection_type="watchlist",
            name="Watchlist",
            description="Demo user's saved watchlist.",
        )
        demo_favourites = get_or_create_collection(
            db,
            user=demo_user,
            collection_type="favourites",
            name="Favourites",
            description="Demo user's favourite entities.",
        )
        mind_bending = get_or_create_collection(
            db,
            user=critic_user,
            collection_type="custom_collection",
            name="Mind-bending cinema",
            description="Films with layered stories and reality-bending ideas.",
            visibility="public",
        )

        add_collection_item_if_missing(
            db,
            collection=demo_watchlist,
            entity=inception,
            order_index=1,
        )
        add_collection_item_if_missing(
            db,
            collection=demo_watchlist,
            entity=demon_slayer,
            order_index=2,
        )
        add_collection_item_if_missing(
            db,
            collection=demo_favourites,
            entity=blinding_lights,
            order_index=1,
        )
        add_collection_item_if_missing(
            db,
            collection=mind_bending,
            entity=inception,
            note="A strong fit for high-concept film discovery.",
            order_index=1,
        )

        inception_fans = get_or_create_community(
            db,
            name="Inception Fans",
            slug="inception-fans",
            community_type="fan",
            owner=demo_user,
            entity=inception,
            description="A fan community for theories and discussion around Inception.",
        )
        demon_slayer_corps = get_or_create_community(
            db,
            name="Demon Slayer Corps",
            slug="demon-slayer-corps",
            community_type="fan",
            owner=critic_user,
            entity=demon_slayer,
            description="A fan community for Demon Slayer arcs, characters, and animation.",
        )
        weeknd_listeners = get_or_create_community(
            db,
            name="Weeknd Listeners",
            slug="weeknd-listeners",
            community_type="fan",
            owner=critic_user,
            entity=after_hours,
            description="A listener community for The Weeknd tracks, albums, and eras.",
        )

        add_community_member_if_missing(db, community=inception_fans, user=demo_user, role="owner")
        add_community_member_if_missing(
            db,
            community=inception_fans,
            user=critic_user,
            role="moderator",
        )
        add_community_member_if_missing(
            db,
            community=demon_slayer_corps,
            user=critic_user,
            role="owner",
        )
        add_community_member_if_missing(
            db,
            community=demon_slayer_corps,
            user=demo_user,
            role="member",
        )
        add_community_member_if_missing(db, community=weeknd_listeners, user=critic_user, role="owner")
        add_community_member_if_missing(db, community=weeknd_listeners, user=demo_user, role="member")

        add_community_rule_if_missing(
            db,
            community=inception_fans,
            title="Mark major spoilers",
            description="Use spoiler warnings for theory posts and ending discussion.",
            order_index=1,
        )
        add_community_rule_if_missing(
            db,
            community=demon_slayer_corps,
            title="Respect episode spoilers",
            description="Keep newer episode and manga spoilers clearly marked.",
            order_index=1,
        )
        add_community_rule_if_missing(
            db,
            community=weeknd_listeners,
            title="Keep release discussions civil",
            description="Discuss albums, tracks, and eras without personal attacks.",
            order_index=1,
        )

        sync_community_member_count(db, inception_fans)
        sync_community_member_count(db, demon_slayer_corps)
        sync_community_member_count(db, weeknd_listeners)

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
