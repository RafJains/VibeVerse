import re

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.community import (
    Community,
    CommunityMember,
    CommunityMergeRequest,
    CommunityReport,
    CommunityRule,
)
from app.models.entity import Entity
from app.models.user import User
from app.schemas.community import (
    CommunityCreate,
    CommunityMergeRequestCreate,
    CommunityReportCreate,
    CommunityRuleCreate,
    CommunityRuleUpdate,
    CommunityUpdate,
)


ADMIN_ROLES = {"admin", "super_admin"}
OFFICIAL_CREATOR_ROLES = {"verified_user", "admin", "super_admin"}
MULTI_COMMUNITY_ROLES = {"verified_user", "admin", "super_admin"}


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "community"


def _ensure_entity_exists(db: Session, entity_id: int) -> None:
    if db.get(Entity, entity_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )


def _generate_unique_slug(db: Session, name: str, exclude_community_id: int | None = None) -> str:
    base_slug = _slugify(name)
    slug = base_slug
    suffix = 2

    while True:
        query = db.query(Community).filter(Community.slug == slug)
        if exclude_community_id is not None:
            query = query.filter(Community.id != exclude_community_id)
        if query.one_or_none() is None:
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1


def _ensure_unique_name(db: Session, name: str, exclude_community_id: int | None = None) -> None:
    query = db.query(Community).filter(func.lower(Community.name) == name.lower())
    if exclude_community_id is not None:
        query = query.filter(Community.id != exclude_community_id)
    if query.one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A community with this name already exists",
        )


def _ensure_create_allowed(db: Session, payload: CommunityCreate, current_user: User) -> None:
    if current_user.role == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guest users cannot create communities",
        )

    if payload.community_type == "official" and current_user.role not in OFFICIAL_CREATOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified users and admins can create official communities",
        )

    if payload.community_type == "platform" and current_user.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create platform communities",
        )

    if payload.community_type == "fan" and current_user.role not in MULTI_COMMUNITY_ROLES:
        existing_fan_community = (
            db.query(Community)
            .filter(
                Community.owner_user_id == current_user.id,
                Community.community_type == "fan",
                Community.status != "hidden",
            )
            .one_or_none()
        )
        if existing_fan_community is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already owns a fan community",
            )


def _sync_member_count(db: Session, community: Community) -> None:
    active_count = (
        db.query(func.count(CommunityMember.id))
        .filter(
            CommunityMember.community_id == community.id,
            CommunityMember.status == "active",
        )
        .scalar()
    )
    community.member_count = int(active_count or 0)


def _is_admin(user: User) -> bool:
    return user.role in ADMIN_ROLES


def _ensure_owner_or_admin(community: Community, current_user: User) -> None:
    if community.owner_user_id == current_user.id or _is_admin(current_user):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to manage this community",
    )


def _is_community_moderator(db: Session, community: Community, current_user: User) -> bool:
    if community.owner_user_id == current_user.id or _is_admin(current_user):
        return True

    member = (
        db.query(CommunityMember)
        .filter(
            CommunityMember.community_id == community.id,
            CommunityMember.user_id == current_user.id,
            CommunityMember.status == "active",
            CommunityMember.role.in_(["owner", "moderator"]),
        )
        .one_or_none()
    )
    return member is not None


def _ensure_can_manage_rules(db: Session, community: Community, current_user: User) -> None:
    if _is_community_moderator(db, community, current_user):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to manage community rules",
    )


def create_community(db: Session, payload: CommunityCreate, current_user: User) -> Community:
    name = payload.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Community name is required",
        )

    if payload.entity_id is not None:
        _ensure_entity_exists(db, payload.entity_id)

    _ensure_create_allowed(db, payload, current_user)
    _ensure_unique_name(db, name)

    community = Community(
        name=name,
        slug=_generate_unique_slug(db, name),
        description=payload.description,
        community_type=payload.community_type,
        entity_id=payload.entity_id,
        owner_user_id=current_user.id,
        status="approved",
        image_url=payload.image_url,
        banner_url=payload.banner_url,
        member_count=1,
    )

    try:
        db.add(community)
        db.flush()
        db.add(
            CommunityMember(
                community_id=community.id,
                user_id=current_user.id,
                role="owner",
                status="active",
            )
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Community name or slug already exists",
        ) from exc

    db.refresh(community)
    return community


def list_communities(
    db: Session,
    entity_id: int | None = None,
    community_type: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Community]:
    query = db.query(Community).filter(Community.status == "approved")

    if entity_id is not None:
        _ensure_entity_exists(db, entity_id)
        query = query.filter(Community.entity_id == entity_id)

    if community_type:
        query = query.filter(Community.community_type == community_type)

    if search and search.strip():
        pattern = f"%{search.strip()}%"
        query = query.filter(Community.name.ilike(pattern))

    return (
        query.order_by(Community.member_count.desc(), Community.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_community_or_404(db: Session, community_id: int) -> Community:
    community = db.get(Community, community_id)
    if community is None or community.status == "hidden":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )
    return community


def get_community_by_slug_or_404(db: Session, slug: str) -> Community:
    community = db.query(Community).filter(Community.slug == slug).one_or_none()
    if community is None or community.status == "hidden":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )
    return community


def update_community(
    db: Session,
    community_id: int,
    payload: CommunityUpdate,
    current_user: User,
) -> Community:
    community = get_community_or_404(db, community_id)
    _ensure_owner_or_admin(community, current_user)

    data = payload.model_dump(exclude_unset=True)

    if "entity_id" in data and data["entity_id"] is not None:
        _ensure_entity_exists(db, data["entity_id"])

    if "name" in data and data["name"] is not None:
        name = data["name"].strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Community name is required",
            )
        _ensure_unique_name(db, name, exclude_community_id=community.id)
        data["name"] = name
        data["slug"] = _generate_unique_slug(db, name, exclude_community_id=community.id)

    for field, value in data.items():
        setattr(community, field, value)

    db.commit()
    db.refresh(community)
    return community


def delete_or_hide_community(db: Session, community_id: int, current_user: User) -> None:
    community = get_community_or_404(db, community_id)
    _ensure_owner_or_admin(community, current_user)
    community.status = "hidden"
    db.commit()


def join_community(db: Session, community_id: int, current_user: User) -> CommunityMember:
    community = get_community_or_404(db, community_id)
    if community.status in {"hidden", "rejected"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This community cannot be joined",
        )

    member = (
        db.query(CommunityMember)
        .filter(
            CommunityMember.community_id == community.id,
            CommunityMember.user_id == current_user.id,
        )
        .one_or_none()
    )

    if member is not None:
        if member.status == "banned":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This user is banned from the community",
            )
        member.status = "active"
        if member.role not in {"owner", "moderator"}:
            member.role = "member"
    else:
        member = CommunityMember(
            community_id=community.id,
            user_id=current_user.id,
            role="member",
            status="active",
        )
        db.add(member)

    _sync_member_count(db, community)
    db.commit()
    db.refresh(member)
    return member


def leave_community(db: Session, community_id: int, current_user: User) -> CommunityMember:
    community = get_community_or_404(db, community_id)
    member = (
        db.query(CommunityMember)
        .filter(
            CommunityMember.community_id == community.id,
            CommunityMember.user_id == current_user.id,
        )
        .one_or_none()
    )
    if member is None or member.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active community membership not found",
        )
    if member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Community owner cannot leave their own community",
        )

    member.status = "left"
    _sync_member_count(db, community)
    db.commit()
    db.refresh(member)
    return member


def list_members(db: Session, community_id: int) -> list[CommunityMember]:
    community = get_community_or_404(db, community_id)
    return (
        db.query(CommunityMember)
        .filter(CommunityMember.community_id == community.id, CommunityMember.status == "active")
        .order_by(CommunityMember.role.asc(), CommunityMember.joined_at.asc())
        .all()
    )


def add_rule(
    db: Session,
    community_id: int,
    payload: CommunityRuleCreate,
    current_user: User,
) -> CommunityRule:
    community = get_community_or_404(db, community_id)
    _ensure_can_manage_rules(db, community, current_user)
    rule = CommunityRule(
        community_id=community.id,
        title=payload.title.strip(),
        description=payload.description,
        order_index=payload.order_index,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(
    db: Session,
    community_id: int,
    rule_id: int,
    payload: CommunityRuleUpdate,
    current_user: User,
) -> CommunityRule:
    community = get_community_or_404(db, community_id)
    _ensure_can_manage_rules(db, community, current_user)
    rule = (
        db.query(CommunityRule)
        .filter(CommunityRule.community_id == community.id, CommunityRule.id == rule_id)
        .one_or_none()
    )
    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community rule not found",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "title" and value is not None:
            value = value.strip()
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, community_id: int, rule_id: int, current_user: User) -> None:
    community = get_community_or_404(db, community_id)
    _ensure_can_manage_rules(db, community, current_user)
    rule = (
        db.query(CommunityRule)
        .filter(CommunityRule.community_id == community.id, CommunityRule.id == rule_id)
        .one_or_none()
    )
    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community rule not found",
        )

    db.delete(rule)
    db.commit()


def report_community(
    db: Session,
    community_id: int,
    payload: CommunityReportCreate,
    current_user: User,
) -> CommunityReport:
    community = get_community_or_404(db, community_id)
    report = CommunityReport(
        community_id=community.id,
        reporter_user_id=current_user.id,
        reason=payload.reason,
        details=payload.details,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def request_community_merge(
    db: Session,
    payload: CommunityMergeRequestCreate,
    current_user: User,
) -> CommunityMergeRequest:
    if payload.source_community_id == payload.target_community_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Source and target communities must be different",
        )

    source = get_community_or_404(db, payload.source_community_id)
    target = get_community_or_404(db, payload.target_community_id)

    existing_request = (
        db.query(CommunityMergeRequest)
        .filter(
            CommunityMergeRequest.source_community_id == source.id,
            CommunityMergeRequest.target_community_id == target.id,
            CommunityMergeRequest.status == "pending",
        )
        .one_or_none()
    )
    if existing_request is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending merge request already exists for these communities",
        )

    merge_request = CommunityMergeRequest(
        source_community_id=source.id,
        target_community_id=target.id,
        requested_by_user_id=current_user.id,
        reason=payload.reason,
        status="pending",
    )
    db.add(merge_request)
    db.commit()
    db.refresh(merge_request)
    return merge_request


def list_entity_communities(db: Session, entity_id: int) -> list[Community]:
    return list_communities(db=db, entity_id=entity_id, limit=100, offset=0)
