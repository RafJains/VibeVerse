from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ReviewVisibility = Literal["public", "followers", "private"]
ReviewReportStatus = Literal["pending", "reviewed", "dismissed", "action_taken"]


def validate_half_step_rating(value: float) -> float:
    if (value * 2) % 1 != 0:
        raise ValueError("Rating must use 0.5 increments.")
    return value


class ReviewTagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    review_id: int
    tag: str
    created_at: datetime


class ReviewCreate(BaseModel):
    entity_id: int
    user_id: int
    rating: float = Field(..., ge=0.5, le=5.0)
    title: str | None = Field(default=None, max_length=160)
    body: str = Field(..., min_length=1)
    spoiler: bool = False
    visibility: ReviewVisibility = "public"
    attachment_url: str | None = Field(default=None, max_length=1000)
    tags: list[str] = Field(default_factory=list)

    @field_validator("rating")
    @classmethod
    def rating_must_use_half_steps(cls, value: float) -> float:
        return validate_half_step_rating(value)


class ReviewUpdate(BaseModel):
    rating: float | None = Field(default=None, ge=0.5, le=5.0)
    title: str | None = Field(default=None, max_length=160)
    body: str | None = Field(default=None, min_length=1)
    spoiler: bool | None = None
    visibility: ReviewVisibility | None = None
    attachment_url: str | None = Field(default=None, max_length=1000)
    tags: list[str] | None = None

    @field_validator("rating")
    @classmethod
    def rating_must_use_half_steps(cls, value: float | None) -> float | None:
        if value is None:
            return value
        return validate_half_step_rating(value)


class ReviewListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    user_id: int
    rating: float
    title: str | None
    body: str
    spoiler: bool
    visibility: str
    attachment_url: str | None
    created_at: datetime
    updated_at: datetime
    tags: list[ReviewTagRead] = Field(default_factory=list)


class ReviewRead(ReviewListItem):
    is_deleted: bool


class ReviewReportCreate(BaseModel):
    reporter_user_id: int
    reason: str = Field(..., min_length=1, max_length=120)
    details: str | None = None


class ReviewReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    review_id: int
    reporter_user_id: int
    reason: str
    details: str | None
    status: ReviewReportStatus
    created_at: datetime
    resolved_at: datetime | None


class EntityRatingSummary(BaseModel):
    entity_id: int
    average_rating: float | None
    review_count: int
    rating_count: int
