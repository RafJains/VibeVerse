from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.integrations import tmdb, youtube
from app.models.entity import (
    Entity,
    EntityMedia,
    EntityTag,
    EntityType,
    ExternalId,
    IngestionJob,
    RawExternalPayload,
)
from app.models.user import User
from app.schemas.ingestion import (
    IngestionResult,
    TMDbIngestionRequest,
    TMDbSearchRequest,
    YouTubeIngestionRequest,
)
from app.services.entity_service import get_entity_or_404


TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p"


def create_ingestion_job(db: Session, source_name: str, job_type: str) -> IngestionJob:
    job = IngestionJob(
        source_name=source_name,
        job_type=job_type,
        status="running",
        message=None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_ingestion_job(
    db: Session,
    job: IngestionJob,
    status: str,
    message: str | None,
) -> IngestionJob:
    job.status = status
    job.message = message
    db.commit()
    db.refresh(job)
    return job


def store_raw_payload(
    db: Session,
    source_name: str,
    source_entity_id: str,
    payload: dict[str, Any],
) -> RawExternalPayload:
    raw_payload = RawExternalPayload(
        source_name=source_name,
        source_entity_id=source_entity_id,
        payload=payload,
    )
    db.add(raw_payload)
    db.flush()
    return raw_payload


def upsert_external_id(
    db: Session,
    entity_id: int,
    source_name: str,
    source_entity_id: str,
    source_url: str | None = None,
) -> ExternalId:
    external_id = (
        db.query(ExternalId)
        .filter(
            ExternalId.source_name == source_name,
            ExternalId.source_entity_id == source_entity_id,
        )
        .order_by(ExternalId.id.asc())
        .first()
    )
    if external_id is not None:
        external_id.entity_id = entity_id
        external_id.source_url = source_url
        return external_id

    external_id = ExternalId(
        entity_id=entity_id,
        source_name=source_name,
        source_entity_id=source_entity_id,
        source_url=source_url,
    )
    db.add(external_id)
    db.flush()
    return external_id


def ingest_tmdb_entity(
    db: Session,
    payload: TMDbIngestionRequest,
    current_user: User,
) -> IngestionResult:
    _ = current_user
    job = create_ingestion_job(db=db, source_name="tmdb", job_type="entity_ingestion")

    try:
        raw_payload = _fetch_tmdb_payload(payload)
        tmdb_source_id = str(payload.tmdb_id)
        store_raw_payload(
            db=db,
            source_name="tmdb",
            source_entity_id=tmdb_source_id,
            payload=raw_payload,
        )

        external_id = _find_external_id(
            db=db,
            source_name="tmdb",
            source_entity_id=tmdb_source_id,
        )
        entity = db.get(Entity, external_id.entity_id) if external_id else None
        created_entity = entity is None

        mapped_entity = _map_tmdb_entity(payload=payload, raw_payload=raw_payload)
        if entity is None:
            entity = Entity(**mapped_entity)
            db.add(entity)
            db.flush()
        else:
            for field, value in mapped_entity.items():
                setattr(entity, field, value)

        _add_tags_if_missing(db=db, entity=entity, tags=_extract_tmdb_tags(raw_payload, payload.tmdb_type))
        _import_tmdb_videos_if_requested(
            db=db,
            entity=entity,
            raw_payload=raw_payload,
            should_import=payload.import_media,
        )
        upsert_external_id(
            db=db,
            entity_id=entity.id,
            source_name="tmdb",
            source_entity_id=tmdb_source_id,
            source_url=_tmdb_source_url(payload.tmdb_type, payload.tmdb_id),
        )

        message = "Created entity from TMDb payload." if created_entity else "Updated entity from TMDb payload."
        update_ingestion_job(db=db, job=job, status="completed", message=message)
        return IngestionResult(
            job_id=job.id,
            status=job.status,
            message=message,
            entity_id=entity.id,
            created_entity=created_entity,
            updated_entity=not created_entity,
        )
    except tmdb.TMDbMissingAPIKeyError as exc:
        update_ingestion_job(db=db, job=job, status="failed", message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except tmdb.TMDbIntegrationError as exc:
        update_ingestion_job(db=db, job=job, status="failed", message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


def search_tmdb(
    db: Session,
    payload: TMDbSearchRequest,
    current_user: User,
) -> IngestionResult:
    _ = current_user
    job = create_ingestion_job(db=db, source_name="tmdb", job_type="search")

    try:
        raw_payload = tmdb.search_multi(payload.query)
        store_raw_payload(
            db=db,
            source_name="tmdb",
            source_entity_id=f"search:{payload.query}",
            payload=raw_payload,
        )
        result_count = len(raw_payload.get("results", []))
        message = f"TMDb search completed and stored {result_count} result(s)."
        update_ingestion_job(db=db, job=job, status="completed", message=message)
        return IngestionResult(job_id=job.id, status=job.status, message=message)
    except tmdb.TMDbMissingAPIKeyError as exc:
        update_ingestion_job(db=db, job=job, status="failed", message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except tmdb.TMDbIntegrationError as exc:
        update_ingestion_job(db=db, job=job, status="failed", message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


def ingest_youtube_media(
    db: Session,
    payload: YouTubeIngestionRequest,
    current_user: User,
) -> IngestionResult:
    _ = current_user
    job = create_ingestion_job(db=db, source_name="youtube", job_type="media_ingestion")

    try:
        entity = get_entity_or_404(db=db, entity_id=payload.entity_id)
        query = payload.query or f"{entity.name} official trailer"
        raw_payload = youtube.search_entity_videos(query=query, max_results=payload.max_results)
        store_raw_payload(
            db=db,
            source_name="youtube",
            source_entity_id=f"entity:{entity.id}",
            payload=raw_payload,
        )
        created_count = _store_youtube_media_items(db=db, entity=entity, raw_payload=raw_payload)
        message = f"YouTube media ingestion completed; added {created_count} new media item(s)."
        update_ingestion_job(db=db, job=job, status="completed", message=message)
        return IngestionResult(
            job_id=job.id,
            status=job.status,
            message=message,
            entity_id=entity.id,
            created_entity=False,
            updated_entity=created_count > 0,
        )
    except youtube.YouTubeMissingAPIKeyError as exc:
        update_ingestion_job(db=db, job=job, status="failed", message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except youtube.YouTubeIntegrationError as exc:
        update_ingestion_job(db=db, job=job, status="failed", message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


def list_ingestion_jobs(db: Session, limit: int = 20, offset: int = 0) -> list[IngestionJob]:
    return (
        db.query(IngestionJob)
        .order_by(IngestionJob.created_at.desc(), IngestionJob.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def _find_external_id(
    db: Session,
    source_name: str,
    source_entity_id: str,
) -> ExternalId | None:
    return (
        db.query(ExternalId)
        .filter(
            ExternalId.source_name == source_name,
            ExternalId.source_entity_id == source_entity_id,
        )
        .order_by(ExternalId.id.asc())
        .first()
    )


def _fetch_tmdb_payload(payload: TMDbIngestionRequest) -> dict[str, Any]:
    if payload.tmdb_type == "movie":
        return tmdb.fetch_movie(payload.tmdb_id)
    if payload.tmdb_type == "tv":
        return tmdb.fetch_tv_series(payload.tmdb_id)
    return tmdb.fetch_person(payload.tmdb_id)


def _map_tmdb_entity(
    payload: TMDbIngestionRequest,
    raw_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "name": _tmdb_name(raw_payload, payload.tmdb_type, payload.tmdb_id),
        "entity_type": _tmdb_entity_type(payload.tmdb_type),
        "description": _tmdb_description(raw_payload),
        "release_date": _tmdb_release_date(raw_payload, payload.tmdb_type),
        "image_url": _tmdb_image_url(_tmdb_image_path(raw_payload, payload.tmdb_type)),
        "banner_url": _tmdb_image_url(raw_payload.get("backdrop_path")),
        "status": "published",
        "popularity_score": float(raw_payload.get("popularity") or 0.0),
        "canonical_entity_id": None,
    }


def _tmdb_entity_type(tmdb_type: str) -> EntityType:
    if tmdb_type == "movie":
        return EntityType.FILM
    if tmdb_type == "tv":
        return EntityType.SERIES
    return EntityType.PERSON


def _tmdb_name(raw_payload: dict[str, Any], tmdb_type: str, tmdb_id: int) -> str:
    if tmdb_type == "movie":
        return (
            raw_payload.get("title")
            or raw_payload.get("original_title")
            or f"TMDb Movie {tmdb_id}"
        )
    return raw_payload.get("name") or raw_payload.get("original_name") or f"TMDb {tmdb_type} {tmdb_id}"


def _tmdb_description(raw_payload: dict[str, Any]) -> str | None:
    description = raw_payload.get("overview") or raw_payload.get("biography")
    if isinstance(description, str):
        return description.strip() or None
    return None


def _tmdb_release_date(raw_payload: dict[str, Any], tmdb_type: str) -> date | None:
    key = "release_date"
    if tmdb_type == "tv":
        key = "first_air_date"
    elif tmdb_type == "person":
        key = "birthday"

    value = raw_payload.get(key)
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _tmdb_image_path(raw_payload: dict[str, Any], tmdb_type: str) -> str | None:
    if tmdb_type == "person":
        return raw_payload.get("profile_path")
    return raw_payload.get("poster_path")


def _tmdb_image_url(path: object, size: str = "w500") -> str | None:
    if not isinstance(path, str) or not path:
        return None
    return f"{TMDB_IMAGE_BASE_URL}/{size}{path}"


def _tmdb_source_url(tmdb_type: str, tmdb_id: int) -> str:
    path = {"movie": "movie", "tv": "tv", "person": "person"}[tmdb_type]
    return f"https://www.themoviedb.org/{path}/{tmdb_id}"


def _extract_tmdb_tags(raw_payload: dict[str, Any], tmdb_type: str) -> list[str]:
    tags: list[str] = []
    for genre in raw_payload.get("genres", []):
        if isinstance(genre, dict) and genre.get("name"):
            tags.append(str(genre["name"]))
    if tmdb_type == "person" and raw_payload.get("known_for_department"):
        tags.append(str(raw_payload["known_for_department"]))
    return tags


def _add_tags_if_missing(db: Session, entity: Entity, tags: list[str]) -> None:
    for tag in tags:
        normalized = tag.strip().lower()
        if not normalized:
            continue
        exists = (
            db.query(EntityTag)
            .filter(EntityTag.entity_id == entity.id, EntityTag.tag == normalized)
            .one_or_none()
        )
        if exists is None:
            db.add(EntityTag(entity_id=entity.id, tag=normalized))


def _import_tmdb_videos_if_requested(
    db: Session,
    entity: Entity,
    raw_payload: dict[str, Any],
    should_import: bool,
) -> None:
    if not should_import:
        return

    for video in raw_payload.get("videos", {}).get("results", []):
        if not isinstance(video, dict) or video.get("site") != "YouTube":
            continue
        video_key = video.get("key")
        if not video_key:
            continue
        url = f"https://www.youtube.com/watch?v={video_key}"
        _add_media_if_missing(
            db=db,
            entity=entity,
            media_type="trailer" if video.get("type") == "Trailer" else "video",
            title=video.get("name"),
            url=url,
            thumbnail_url=f"https://img.youtube.com/vi/{video_key}/hqdefault.jpg",
            source_name="youtube",
        )


def _store_youtube_media_items(
    db: Session,
    entity: Entity,
    raw_payload: dict[str, Any],
) -> int:
    created_count = 0
    for item in raw_payload.get("items", []):
        if not isinstance(item, dict):
            continue
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue
        snippet = item.get("snippet", {})
        title = snippet.get("title") if isinstance(snippet, dict) else None
        thumbnail_url = _youtube_thumbnail_url(snippet)
        url = f"https://www.youtube.com/watch?v={video_id}"
        created = _add_media_if_missing(
            db=db,
            entity=entity,
            media_type="trailer" if title and "trailer" in title.lower() else "video",
            title=title,
            url=url,
            thumbnail_url=thumbnail_url,
            source_name="youtube",
        )
        if created:
            created_count += 1
    return created_count


def _youtube_thumbnail_url(snippet: object) -> str | None:
    if not isinstance(snippet, dict):
        return None
    thumbnails = snippet.get("thumbnails")
    if not isinstance(thumbnails, dict):
        return None
    for key in ("high", "medium", "default"):
        thumbnail = thumbnails.get(key)
        if isinstance(thumbnail, dict) and thumbnail.get("url"):
            return str(thumbnail["url"])
    return None


def _add_media_if_missing(
    db: Session,
    entity: Entity,
    media_type: str,
    title: object,
    url: str,
    thumbnail_url: str | None,
    source_name: str,
) -> bool:
    exists = (
        db.query(EntityMedia)
        .filter(EntityMedia.entity_id == entity.id, EntityMedia.url == url)
        .one_or_none()
    )
    if exists is not None:
        return False

    db.add(
        EntityMedia(
            entity_id=entity.id,
            media_type=media_type,
            title=str(title) if title else None,
            url=url,
            thumbnail_url=thumbnail_url,
            source_name=source_name,
        )
    )
    return True
