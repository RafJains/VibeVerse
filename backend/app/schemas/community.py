from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CommunityType = Literal["fan", "official", "platform"]
CommunityStatus = Literal["pending", "approved", "rejected", "hidden"]
CommunityMemberRole = Literal["owner", "moderator", "member"]
CommunityMemberStatus = Literal["active", "banned", "left"]
CommunityActionStatus = Literal["pending", "reviewed", "dismissed", "action_taken"]


class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    description: str | None = None
    community_type: CommunityType = "fan"
    entity_id: int | None = None
    image_url: str | None = Field(default=None, max_length=1000)
    banner_url: str | None = Field(default=None, max_length=1000)


class CommunityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    entity_id: int | None = None
    image_url: str | None = Field(default=None, max_length=1000)
    banner_url: str | None = Field(default=None, max_length=1000)


class CommunityListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    community_type: CommunityType
    entity_id: int | None
    owner_user_id: int
    status: CommunityStatus
    image_url: str | None
    banner_url: str | None
    member_count: int
    created_at: datetime
    updated_at: datetime


class CommunityMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    community_id: int
    user_id: int
    role: CommunityMemberRole
    status: CommunityMemberStatus
    joined_at: datetime


class CommunityRuleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    description: str | None = None
    order_index: int = 0


class CommunityRuleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    order_index: int | None = None


class CommunityRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    community_id: int
    title: str
    description: str | None
    order_index: int
    created_at: datetime
    updated_at: datetime


class CommunityRead(CommunityListItem):
    rules: list[CommunityRuleRead] = Field(default_factory=list)


class CommunityReportCreate(BaseModel):
    reason: str = Field(..., min_length=1, max_length=120)
    details: str | None = None


class CommunityReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    community_id: int
    reporter_user_id: int
    reason: str
    details: str | None
    status: CommunityActionStatus
    created_at: datetime
    resolved_at: datetime | None


class CommunityMergeRequestCreate(BaseModel):
    source_community_id: int
    target_community_id: int
    reason: str = Field(..., min_length=1, max_length=240)


class CommunityMergeRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_community_id: int
    target_community_id: int
    requested_by_user_id: int
    reason: str
    status: CommunityActionStatus
    created_at: datetime
    resolved_at: datetime | None
