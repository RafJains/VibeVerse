from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


FeedCardType = Literal[
    "trending_entity",
    "new_release",
    "trailer_drop",
    "top_chart",
    "spotlight",
    "official_update",
    "recommendation",
    "announcement",
]
FeedCardStatus = Literal[
    "draft",
    "pending_review",
    "approved",
    "rejected",
    "published",
    "archived",
]
FeedSourceType = Literal["admin_created", "system_suggested", "external_ingestion"]


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class FeedCardEntityCreate(BaseModel):
    entity_id: int
    order_index: int = 0


class FeedCardEntityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    feed_card_id: int
    entity_id: int
    order_index: int
    created_at: datetime


class FeedCardCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=180)
    subtitle: str | None = Field(default=None, max_length=255)
    body: str | None = None
    card_type: FeedCardType = "spotlight"
    status: FeedCardStatus = "draft"
    image_url: str | None = Field(default=None, max_length=1000)
    source_type: FeedSourceType = "admin_created"
    source_url: str | None = Field(default=None, max_length=1000)
    priority: int = 0
    region: str | None = Field(default=None, max_length=20)
    scheduled_at: datetime | None = None
    expires_at: datetime | None = None
    linked_entity_ids: list[int] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title is required.")
        return stripped

    @field_validator("subtitle", "body", "image_url", "source_url", "region")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)


class FeedCardUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=180)
    subtitle: str | None = Field(default=None, max_length=255)
    body: str | None = None
    card_type: FeedCardType | None = None
    status: FeedCardStatus | None = None
    image_url: str | None = Field(default=None, max_length=1000)
    source_type: FeedSourceType | None = None
    source_url: str | None = Field(default=None, max_length=1000)
    priority: int | None = None
    region: str | None = Field(default=None, max_length=20)
    scheduled_at: datetime | None = None
    expires_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        cleaned = _clean_optional_text(value)
        if value is not None and cleaned is None:
            raise ValueError("Title cannot be blank.")
        return cleaned

    @field_validator("subtitle", "body", "image_url", "source_url", "region")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)


class FeedCardListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    subtitle: str | None
    body: str | None
    card_type: FeedCardType
    status: FeedCardStatus
    image_url: str | None
    source_type: FeedSourceType
    source_url: str | None
    priority: int
    region: str | None
    created_by_user_id: int
    approved_by_user_id: int | None
    approved_at: datetime | None
    scheduled_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime
    entities: list[FeedCardEntityRead] = Field(default_factory=list)


class FeedCardRead(FeedCardListItem):
    pass


class FeedRegionCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=120)

    @field_validator("code")
    @classmethod
    def clean_code(cls, value: str) -> str:
        stripped = value.strip().lower()
        if not stripped:
            raise ValueError("Region code is required.")
        return stripped

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Region name is required.")
        return stripped


class FeedRegionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    created_at: datetime


class TrendingScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    score: float
    score_type: str
    calculated_at: datetime


class FeedCardStatusUpdate(BaseModel):
    status: FeedCardStatus
