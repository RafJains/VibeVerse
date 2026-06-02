export type CommunityType = "fan" | "official" | "platform";
export type CommunityStatus = "pending" | "approved" | "rejected" | "hidden";
export type CommunityMemberRole = "owner" | "moderator" | "member";
export type CommunityMemberStatus = "active" | "banned" | "left";
export type CommunityActionStatus =
  | "pending"
  | "reviewed"
  | "dismissed"
  | "action_taken";

export interface CommunityListItem {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  community_type: CommunityType;
  entity_id: number | null;
  owner_user_id: number;
  status: CommunityStatus;
  image_url: string | null;
  banner_url: string | null;
  member_count: number;
  created_at: string;
  updated_at: string;
}

export interface CommunityRule {
  id: number;
  community_id: number;
  title: string;
  description: string | null;
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface Community extends CommunityListItem {
  rules: CommunityRule[];
}

export interface CommunityMember {
  id: number;
  community_id: number;
  user_id: number;
  role: CommunityMemberRole;
  status: CommunityMemberStatus;
  joined_at: string;
}

export interface CommunityCreatePayload {
  name: string;
  description?: string | null;
  community_type: CommunityType;
  entity_id?: number | null;
  image_url?: string | null;
  banner_url?: string | null;
}

export interface CommunityRuleCreatePayload {
  title: string;
  description?: string | null;
  order_index?: number;
}

export interface CommunityReportPayload {
  reason: string;
  details?: string | null;
}

export interface CommunityReport {
  id: number;
  community_id: number;
  reporter_user_id: number;
  reason: string;
  details: string | null;
  status: CommunityActionStatus;
  created_at: string;
  resolved_at: string | null;
}

export interface CommunityMergeRequestPayload {
  source_community_id: number;
  target_community_id: number;
  reason: string;
}

export interface CommunityMergeRequest {
  id: number;
  source_community_id: number;
  target_community_id: number;
  requested_by_user_id: number;
  reason: string;
  status: CommunityActionStatus;
  created_at: string;
  resolved_at: string | null;
}
