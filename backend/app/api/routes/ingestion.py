from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.ingestion import (
    IngestionJobRead,
    IngestionResult,
    TMDbIngestionRequest,
    TMDbSearchRequest,
    YouTubeIngestionRequest,
)
from app.services import ingestion_service
from app.services.auth_service import get_current_user


router = APIRouter(prefix="/admin/ingestion", tags=["admin ingestion"])
ADMIN_ROLES = {"admin", "super_admin"}


def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role in ADMIN_ROLES:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only admins can run ingestion jobs",
    )


@router.post("/tmdb", response_model=IngestionResult)
def ingest_tmdb_entity(
    payload: TMDbIngestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> IngestionResult:
    return ingestion_service.ingest_tmdb_entity(
        db=db,
        payload=payload,
        current_user=current_user,
    )


@router.post("/tmdb/search", response_model=IngestionResult)
def search_tmdb(
    payload: TMDbSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> IngestionResult:
    return ingestion_service.search_tmdb(
        db=db,
        payload=payload,
        current_user=current_user,
    )


@router.post("/youtube", response_model=IngestionResult)
def ingest_youtube_media(
    payload: YouTubeIngestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> IngestionResult:
    return ingestion_service.ingest_youtube_media(
        db=db,
        payload=payload,
        current_user=current_user,
    )


@router.get("/jobs", response_model=list[IngestionJobRead])
def list_ingestion_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> list[IngestionJobRead]:
    return ingestion_service.list_ingestion_jobs(db=db, limit=limit, offset=offset)
