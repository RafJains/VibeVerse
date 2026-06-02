export type PostType =
  | "review"
  | "hot_take"
  | "poll"
  | "meme_edit"
  | "fan_theory"
  | "reaction"
  | "ranking"
  | "cover_clip"
  | "discussion";

export type PostStatus = "published" | "hidden" | "removed";
export type PostActionStatus = "pending" | "reviewed" | "dismissed" | "action_taken";
export type PostModerationActionType = "hide" | "unhide" | "remove" | "restore";

export interface CommunityPostListItem {
  id: number;
  community_id: number;
  author_user_id: number;
  post_type: PostType;
  title: string;
  body: string | null;
  media_url: string | null;
  spoiler: boolean;
  status: PostStatus;
  created_at: string;
  updated_at: string;
}

export interface CommunityPost extends CommunityPostListItem {}

export interface CommunityPostCreatePayload {
  post_type: PostType;
  title: string;
  body?: string | null;
  media_url?: string | null;
  spoiler: boolean;
}

export interface CommunityPostUpdatePayload {
  post_type?: PostType;
  title?: string;
  body?: string | null;
  media_url?: string | null;
  spoiler?: boolean;
}

export interface PostReportPayload {
  reason: string;
  details?: string | null;
}

export interface PostReport {
  id: number;
  post_id: number;
  reporter_user_id: number;
  reason: string;
  details: string | null;
  status: PostActionStatus;
  created_at: string;
  resolved_at: string | null;
}

export interface PostModerationAction {
  id: number;
  post_id: number;
  moderator_user_id: number;
  action_type: PostModerationActionType;
  reason: string | null;
  created_at: string;
}

export interface CommunityBlockedWord {
  id: number;
  community_id: number;
  word: string;
  created_by_user_id: number;
  created_at: string;
}

export interface CommunityBlockedWordCreatePayload {
  word: string;
}
