from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.entity import EntityListItem


CollectionType = Literal["watchlist", "playlist", "favourites", "custom_collection", "gamelist"]
CollectionVisibility = Literal["public", "private", "followers"]


class CollectionItemCreate(BaseModel):
    entity_id: int
    note: str | None = None
    order_index: int = 0


class CollectionItemUpdate(BaseModel):
    note: str | None = None
    order_index: int | None = None


class CollectionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    collection_id: int
    entity_id: int
    note: str | None
    order_index: int
    created_at: datetime
    entity: EntityListItem | None = None


class CollectionCreate(BaseModel):
    user_id: int
    name: str | None = Field(default=None, max_length=160)
    description: str | None = None
    collection_type: CollectionType
    visibility: CollectionVisibility = "private"

    @model_validator(mode="after")
    def validate_custom_collection_name(self) -> "CollectionCreate":
        if self.collection_type == "custom_collection" and not (self.name and self.name.strip()):
            raise ValueError("Name is required for custom_collection.")
        return self


class CollectionUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=160)
    description: str | None = None
    collection_type: CollectionType | None = None
    visibility: CollectionVisibility | None = None


class CollectionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    description: str | None
    collection_type: str
    visibility: str
    created_at: datetime
    updated_at: datetime


class CollectionRead(CollectionListItem):
    items: list[CollectionItemRead] = Field(default_factory=list)
