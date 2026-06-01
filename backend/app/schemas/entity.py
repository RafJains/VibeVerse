from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.entity import EntityType


class EntityTagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    tag: str
    created_at: datetime


class EntityMediaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    media_type: str
    title: str | None
    url: str
    thumbnail_url: str | None
    source_name: str | None
    created_at: datetime


class EntityCreditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    person_entity_id: int
    role: str
    character_name: str | None
    order_index: int
    created_at: datetime


class EntityRelationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    created_at: datetime


class ExternalIdRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    source_name: str
    source_entity_id: str
    source_url: str | None
    created_at: datetime


class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    entity_type: EntityType
    description: str | None = None
    release_date: date | None = None
    image_url: str | None = None
    banner_url: str | None = None
    status: str = "draft"
    popularity_score: float = 0.0
    canonical_entity_id: int | None = None


class EntityCreate(EntityBase):
    tags: list[str] = Field(default_factory=list)


class EntityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    entity_type: EntityType | None = None
    description: str | None = None
    release_date: date | None = None
    image_url: str | None = None
    banner_url: str | None = None
    status: str | None = None
    popularity_score: float | None = None
    canonical_entity_id: int | None = None
    tags: list[str] | None = None


class EntityListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    entity_type: EntityType
    description: str | None
    image_url: str | None
    banner_url: str | None
    status: str
    popularity_score: float
    tags: list[EntityTagRead] = Field(default_factory=list)


class EntityRead(EntityListItem):
    release_date: date | None
    canonical_entity_id: int | None
    created_at: datetime
    updated_at: datetime
