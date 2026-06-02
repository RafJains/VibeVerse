from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PostType = Literal[
    "review",
    "hot_take",
    "poll",
    "meme_edit",
    "fan_theory",
    "reaction",
    "ranking",
    "cover_clip",
    "discussion",
]
PostStatus = Literal["published", "hidden", "removed"]
PostReportStatus = Literal["pending", "reviewed", "dismissed", "action_taken"]
PostModerationActionType = Literal["hide", "unhide", "remove", "restore"]


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class CommunityPostCreate(BaseModel):
    post_type: PostType = "discussion"
    title: str = Field(..., min_length=1, max_length=180)
    body: str | None = None
    media_url: str | None = Field(default=None, max_length=1000)
    spoiler: bool = False

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title is required.")
        return stripped

    @field_validator("body", "media_url")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)

    @model_validator(mode="after")
    def title_or_body_required(self) -> "CommunityPostCreate":
        if not self.title and not self.body:
            raise ValueError("At least title or body is required.")
        return self


class CommunityPostUpdate(BaseModel):
    post_type: PostType | None = None
    title: str | None = Field(default=None, max_length=180)
    body: str | None = None
    media_url: str | None = Field(default=None, max_length=1000)
    spoiler: bool | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        cleaned = _clean_optional_text(value)
        if value is not None and cleaned is None:
            raise ValueError("Title cannot be blank.")
        return cleaned

    @field_validator("body", "media_url")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)


class CommunityPostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    community_id: int
    author_user_id: int
    post_type: PostType
    title: str
    body: str | None
    media_url: str | None
    spoiler: bool
    status: PostStatus
    created_at: datetime
    updated_at: datetime


class CommunityPostRead(CommunityPostListItem):
    pass


class PostReportCreate(BaseModel):
    reason: str = Field(..., min_length=1, max_length=120)
    details: str | None = None

    @field_validator("reason")
    @classmethod
    def reason_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Reason is required.")
        return stripped

    @field_validator("details")
    @classmethod
    def clean_details(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)


class PostReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    reporter_user_id: int
    reason: str
    details: str | None
    status: PostReportStatus
    created_at: datetime
    resolved_at: datetime | None


class PostModerationActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    moderator_user_id: int
    action_type: PostModerationActionType
    reason: str | None
    created_at: datetime


class CommunityBlockedWordCreate(BaseModel):
    word: str = Field(..., min_length=1, max_length=120)

    @field_validator("word")
    @classmethod
    def word_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip().lower()
        if not stripped:
            raise ValueError("Blocked word is required.")
        return stripped


class CommunityBlockedWordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    community_id: int
    word: str
    created_by_user_id: int
    created_at: datetime
