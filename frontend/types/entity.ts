export type EntityType =
  | "film"
  | "series"
  | "song"
  | "album"
  | "game"
  | "sport"
  | "tournament"
  | "team"
  | "person"
  | "live_event";

export interface EntityTag {
  id: number;
  entity_id: number;
  tag: string;
  created_at: string;
}

export interface EntityListItem {
  id: number;
  name: string;
  entity_type: EntityType;
  description: string | null;
  image_url: string | null;
  banner_url: string | null;
  status: string;
  popularity_score: number;
  tags: EntityTag[];
}

export interface Entity extends EntityListItem {
  release_date: string | null;
  canonical_entity_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface EntityMedia {
  id: number;
  entity_id: number;
  media_type: string;
  title: string | null;
  url: string;
  thumbnail_url: string | null;
  source_name: string | null;
  created_at: string;
}

export interface EntityCredit {
  id: number;
  entity_id: number;
  person_entity_id: number;
  role: string;
  character_name: string | null;
  order_index: number;
  created_at: string;
}

export interface EntityRelation {
  id: number;
  source_entity_id: number;
  target_entity_id: number;
  relation_type: string;
  created_at: string;
}
