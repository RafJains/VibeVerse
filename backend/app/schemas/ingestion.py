from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


TMDbType = Literal["movie", "tv", "person"]


class TMDbIngestionRequest(BaseModel):
    tmdb_id: int = Field(..., gt=0)
    tmdb_type: TMDbType
    import_media: bool = False


class TMDbSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Query is required.")
        return stripped


class YouTubeIngestionRequest(BaseModel):
    entity_id: int = Field(..., gt=0)
    query: str | None = None
    max_results: int = Field(default=5, ge=1, le=25)

    @field_validator("query")
    @classmethod
    def clean_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class IngestionJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    job_type: str
    status: str
    message: str | None
    created_at: datetime
    updated_at: datetime


class IngestionResult(BaseModel):
    job_id: int
    status: str
    message: str
    entity_id: int | None = None
    created_entity: bool = False
    updated_entity: bool = False
