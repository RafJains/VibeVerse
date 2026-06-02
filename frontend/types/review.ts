export type ReviewVisibility = "public" | "followers" | "private";

export interface ReviewTag {
  id: number;
  review_id: number;
  tag: string;
  created_at: string;
}

export interface ReviewListItem {
  id: number;
  entity_id: number;
  user_id: number;
  rating: number;
  title: string | null;
  body: string;
  spoiler: boolean;
  visibility: ReviewVisibility;
  attachment_url: string | null;
  created_at: string;
  updated_at: string;
  tags: ReviewTag[];
}

export interface Review extends ReviewListItem {
  is_deleted: boolean;
}

export interface EntityRatingSummary {
  entity_id: number;
  average_rating: number | null;
  review_count: number;
  rating_count: number;
}

export interface ReviewCreatePayload {
  entity_id: number;
  user_id: number;
  rating: number;
  title?: string | null;
  body: string;
  spoiler: boolean;
  visibility: ReviewVisibility;
  attachment_url?: string | null;
  tags: string[];
}

export interface ReviewReportCreatePayload {
  reporter_user_id: number;
  reason: string;
  details?: string | null;
}

export interface ReviewReport {
  id: number;
  review_id: number;
  reporter_user_id: number;
  reason: string;
  details: string | null;
  status: "pending" | "reviewed" | "dismissed" | "action_taken";
  created_at: string;
  resolved_at: string | null;
}
