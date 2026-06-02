export type FeedCardType =
  | "trending_entity"
  | "new_release"
  | "trailer_drop"
  | "top_chart"
  | "spotlight"
  | "official_update"
  | "recommendation"
  | "announcement";

export type FeedCardStatus =
  | "draft"
  | "pending_review"
  | "approved"
  | "rejected"
  | "published"
  | "archived";

export type FeedSourceType =
  | "admin_created"
  | "system_suggested"
  | "external_ingestion";

export interface FeedCardEntity {
  id: number;
  feed_card_id: number;
  entity_id: number;
  order_index: number;
  created_at: string;
}

export interface FeedCardListItem {
  id: number;
  title: string;
  subtitle: string | null;
  body: string | null;
  card_type: FeedCardType;
  status: FeedCardStatus;
  image_url: string | null;
  source_type: FeedSourceType;
  source_url: string | null;
  priority: number;
  region: string | null;
  created_by_user_id: number;
  approved_by_user_id: number | null;
  approved_at: string | null;
  scheduled_at: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
  entities: FeedCardEntity[];
}

export interface FeedCard extends FeedCardListItem {}

export interface TrendingScore {
  id: number;
  entity_id: number;
  score: number;
  score_type: string;
  calculated_at: string;
}
