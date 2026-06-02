from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.community import (
    CommunityCreate,
    CommunityListItem,
    CommunityMemberRead,
    CommunityMergeRequestCreate,
    CommunityMergeRequestRead,
    CommunityRead,
    CommunityReportCreate,
    CommunityReportRead,
    CommunityRuleCreate,
    CommunityRuleRead,
    CommunityRuleUpdate,
    CommunityUpdate,
)
from app.services import community_service
from app.services.auth_service import get_current_user


router = APIRouter(tags=["communities"])


@router.get("/communities", response_model=list[CommunityListItem])
def list_communities(
    entity_id: int | None = None,
    community_type: str | None = Query(default=None, pattern="^(fan|official|platform)$"),
    search: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[CommunityListItem]:
    return community_service.list_communities(
        db=db,
        entity_id=entity_id,
        community_type=community_type,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/communities/slug/{slug}", response_model=CommunityRead)
def get_community_by_slug(slug: str, db: Session = Depends(get_db)) -> CommunityRead:
    return community_service.get_community_by_slug_or_404(db=db, slug=slug)


@router.post(
    "/communities/merge-requests",
    response_model=CommunityMergeRequestRead,
    status_code=status.HTTP_201_CREATED,
)
def request_community_merge(
    payload: CommunityMergeRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityMergeRequestRead:
    return community_service.request_community_merge(
        db=db,
        payload=payload,
        current_user=current_user,
    )


@router.get("/communities/{community_id}", response_model=CommunityRead)
def get_community(community_id: int, db: Session = Depends(get_db)) -> CommunityRead:
    return community_service.get_community_or_404(db=db, community_id=community_id)


@router.get("/entities/{entity_id}/communities", response_model=list[CommunityListItem])
def list_entity_communities(
    entity_id: int,
    db: Session = Depends(get_db),
) -> list[CommunityListItem]:
    return community_service.list_entity_communities(db=db, entity_id=entity_id)


@router.get("/communities/{community_id}/members", response_model=list[CommunityMemberRead])
def list_members(
    community_id: int,
    db: Session = Depends(get_db),
) -> list[CommunityMemberRead]:
    return community_service.list_members(db=db, community_id=community_id)


@router.post("/communities", response_model=CommunityRead, status_code=status.HTTP_201_CREATED)
def create_community(
    payload: CommunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityRead:
    return community_service.create_community(db=db, payload=payload, current_user=current_user)


@router.patch("/communities/{community_id}", response_model=CommunityRead)
def update_community(
    community_id: int,
    payload: CommunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityRead:
    return community_service.update_community(
        db=db,
        community_id=community_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete("/communities/{community_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_or_hide_community(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    community_service.delete_or_hide_community(
        db=db,
        community_id=community_id,
        current_user=current_user,
    )


@router.post("/communities/{community_id}/join", response_model=CommunityMemberRead)
def join_community(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityMemberRead:
    return community_service.join_community(
        db=db,
        community_id=community_id,
        current_user=current_user,
    )


@router.post("/communities/{community_id}/leave", response_model=CommunityMemberRead)
def leave_community(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityMemberRead:
    return community_service.leave_community(
        db=db,
        community_id=community_id,
        current_user=current_user,
    )


@router.post(
    "/communities/{community_id}/rules",
    response_model=CommunityRuleRead,
    status_code=status.HTTP_201_CREATED,
)
def add_rule(
    community_id: int,
    payload: CommunityRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityRuleRead:
    return community_service.add_rule(
        db=db,
        community_id=community_id,
        payload=payload,
        current_user=current_user,
    )


@router.patch("/communities/{community_id}/rules/{rule_id}", response_model=CommunityRuleRead)
def update_rule(
    community_id: int,
    rule_id: int,
    payload: CommunityRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityRuleRead:
    return community_service.update_rule(
        db=db,
        community_id=community_id,
        rule_id=rule_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/communities/{community_id}/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rule(
    community_id: int,
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    community_service.delete_rule(
        db=db,
        community_id=community_id,
        rule_id=rule_id,
        current_user=current_user,
    )


@router.post(
    "/communities/{community_id}/report",
    response_model=CommunityReportRead,
    status_code=status.HTTP_201_CREATED,
)
def report_community(
    community_id: int,
    payload: CommunityReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityReportRead:
    return community_service.report_community(
        db=db,
        community_id=community_id,
        payload=payload,
        current_user=current_user,
    )

