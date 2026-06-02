import type { EntityListItem } from "@/types/entity";

export type CollectionType =
  | "watchlist"
  | "playlist"
  | "favourites"
  | "custom_collection"
  | "gamelist";

export type CollectionVisibility = "public" | "private" | "followers";

export interface CollectionItem {
  id: number;
  collection_id: number;
  entity_id: number;
  note: string | null;
  order_index: number;
  created_at: string;
  entity: EntityListItem | null;
}

export interface CollectionListItem {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  collection_type: CollectionType;
  visibility: CollectionVisibility;
  created_at: string;
  updated_at: string;
}

export interface Collection extends CollectionListItem {
  items: CollectionItem[];
}
