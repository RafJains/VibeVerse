import axios from "axios";

import type {
  CollectionItem,
  CollectionListItem,
} from "@/types/collection";
import type {
  Community,
  CommunityCreatePayload,
  CommunityListItem,
  CommunityMember,
  CommunityMergeRequest,
  CommunityMergeRequestPayload,
  CommunityReport,
  CommunityReportPayload,
  CommunityRule,
  CommunityRuleCreatePayload,
  CommunityType,
} from "@/types/community";
import type { LoginPayload, SignupPayload, TokenResponse, User } from "@/types/auth";
import type {
  Entity,
  EntityCredit,
  EntityListItem,
  EntityMedia,
  EntityRelation,
  EntityType,
} from "@/types/entity";
import type { FeedCard, FeedCardListItem, TrendingScore } from "@/types/feed";
import type {
  EntityRatingSummary,
  Review,
  ReviewCreatePayload,
  ReviewListItem,
  ReviewReport,
  ReviewReportCreatePayload,
} from "@/types/review";
import type {
  CommunityBlockedWord,
  CommunityBlockedWordCreatePayload,
  CommunityPost,
  CommunityPostCreatePayload,
  CommunityPostListItem,
  CommunityPostUpdatePayload,
  PostModerationAction,
  PostReport as CommunityPostReport,
  PostReportPayload,
} from "@/types/post";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const AUTH_TOKEN_STORAGE_KEY = "vibeverse_access_token";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export function getStoredAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
}

export function setAuthToken(token: string): void {
  apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
  }
}

export function clearAuthToken(): void {
  delete apiClient.defaults.headers.common.Authorization;
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
  }
}

apiClient.interceptors.request.use((config) => {
  const token = getStoredAuthToken();
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (typeof error.response?.data?.detail === "string") {
      return error.response.data.detail;
    }
    if (Array.isArray(error.response?.data?.detail)) {
      return (error.response.data.detail as Array<{ msg?: string }>)
        .map((item) => item?.msg ?? JSON.stringify(item))
        .join(" ");
    }
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong.";
}

export function getErrorStatus(error: unknown): number | null {
  if (axios.isAxiosError(error)) {
    return error.response?.status ?? null;
  }
  return null;
}

export async function signup(payload: SignupPayload): Promise<User> {
  const response = await apiClient.post<User>("/auth/signup", payload);
  return response.data;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/login", payload);
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>("/auth/me");
  return response.data;
}

export async function logout(): Promise<{ message: string }> {
  const response = await apiClient.post<{ message: string }>("/auth/logout");
  return response.data;
}

export async function getEntities(params?: {
  entity_type?: EntityType | "";
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<EntityListItem[]> {
  const response = await apiClient.get<EntityListItem[]>("/entities", { params });
  return response.data;
}

export async function getEntity(id: number): Promise<Entity> {
  const response = await apiClient.get<Entity>(`/entities/${id}`);
  return response.data;
}

export async function getEntityMedia(id: number): Promise<EntityMedia[]> {
  const response = await apiClient.get<EntityMedia[]>(`/entities/${id}/media`);
  return response.data;
}

export async function getEntityCredits(id: number): Promise<EntityCredit[]> {
  const response = await apiClient.get<EntityCredit[]>(`/entities/${id}/credits`);
  return response.data;
}

export async function getEntityRelations(id: number): Promise<EntityRelation[]> {
  const response = await apiClient.get<EntityRelation[]>(`/entities/${id}/related`);
  return response.data;
}

export async function getGlobalFeed(params?: {
  region?: string;
  limit?: number;
  offset?: number;
}): Promise<FeedCardListItem[]> {
  const response = await apiClient.get<FeedCardListItem[]>("/feed/global", {
    params: {
      ...params,
      region: params?.region?.trim() || undefined,
    },
  });
  return response.data;
}

export async function getFeedCard(id: number): Promise<FeedCard> {
  const response = await apiClient.get<FeedCard>(`/feed/cards/${id}`);
  return response.data;
}

export async function getTrendingScores(params?: {
  score_type?: string;
  limit?: number;
  offset?: number;
}): Promise<TrendingScore[]> {
  const response = await apiClient.get<TrendingScore[]>("/feed/trending-scores", {
    params: {
      ...params,
      score_type: params?.score_type?.trim() || undefined,
    },
  });
  return response.data;
}

export async function getCommunities(params?: {
  entity_id?: number;
  community_type?: CommunityType | "";
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<CommunityListItem[]> {
  const response = await apiClient.get<CommunityListItem[]>("/communities", {
    params: {
      ...params,
      community_type: params?.community_type || undefined,
      search: params?.search?.trim() || undefined,
    },
  });
  return response.data;
}

export async function getCommunity(id: number): Promise<Community> {
  const response = await apiClient.get<Community>(`/communities/${id}`);
  return response.data;
}

export async function getCommunityBySlug(slug: string): Promise<Community> {
  const response = await apiClient.get<Community>(`/communities/slug/${slug}`);
  return response.data;
}

export async function getEntityCommunities(entityId: number): Promise<CommunityListItem[]> {
  const response = await apiClient.get<CommunityListItem[]>(
    `/entities/${entityId}/communities`,
  );
  return response.data;
}

export async function getCommunityMembers(
  communityId: number,
): Promise<CommunityMember[]> {
  const response = await apiClient.get<CommunityMember[]>(
    `/communities/${communityId}/members`,
  );
  return response.data;
}

export async function createCommunity(
  payload: CommunityCreatePayload,
): Promise<Community> {
  const response = await apiClient.post<Community>("/communities", payload);
  return response.data;
}

export async function joinCommunity(
  communityId: number,
): Promise<CommunityMember> {
  const response = await apiClient.post<CommunityMember>(
    `/communities/${communityId}/join`,
  );
  return response.data;
}

export async function leaveCommunity(
  communityId: number,
): Promise<CommunityMember> {
  const response = await apiClient.post<CommunityMember>(
    `/communities/${communityId}/leave`,
  );
  return response.data;
}

export async function reportCommunity(
  communityId: number,
  payload: CommunityReportPayload,
): Promise<CommunityReport> {
  const response = await apiClient.post<CommunityReport>(
    `/communities/${communityId}/report`,
    payload,
  );
  return response.data;
}

export async function createCommunityRule(
  communityId: number,
  payload: CommunityRuleCreatePayload,
): Promise<CommunityRule> {
  const response = await apiClient.post<CommunityRule>(
    `/communities/${communityId}/rules`,
    payload,
  );
  return response.data;
}

export async function createCommunityMergeRequest(
  payload: CommunityMergeRequestPayload,
): Promise<CommunityMergeRequest> {
  const response = await apiClient.post<CommunityMergeRequest>(
    "/communities/merge-requests",
    payload,
  );
  return response.data;
}

export async function getCommunityPosts(
  communityId: number,
): Promise<CommunityPostListItem[]> {
  const response = await apiClient.get<CommunityPostListItem[]>(
    `/communities/${communityId}/posts`,
  );
  return response.data;
}

export async function getPost(postId: number): Promise<CommunityPost> {
  const response = await apiClient.get<CommunityPost>(`/posts/${postId}`);
  return response.data;
}

export async function createCommunityPost(
  communityId: number,
  payload: CommunityPostCreatePayload,
): Promise<CommunityPost> {
  const response = await apiClient.post<CommunityPost>(
    `/communities/${communityId}/posts`,
    payload,
  );
  return response.data;
}

export async function updatePost(
  postId: number,
  payload: CommunityPostUpdatePayload,
): Promise<CommunityPost> {
  const response = await apiClient.patch<CommunityPost>(`/posts/${postId}`, payload);
  return response.data;
}

export async function deletePost(postId: number): Promise<void> {
  await apiClient.delete(`/posts/${postId}`);
}

export async function reportPost(
  postId: number,
  payload: PostReportPayload,
): Promise<CommunityPostReport> {
  const response = await apiClient.post<CommunityPostReport>(
    `/posts/${postId}/report`,
    payload,
  );
  return response.data;
}

export async function hidePost(
  postId: number,
  reason: string | null,
): Promise<PostModerationAction> {
  const response = await apiClient.post<PostModerationAction>(`/posts/${postId}/hide`, {
    reason,
  });
  return response.data;
}

export async function unhidePost(
  postId: number,
  reason: string | null,
): Promise<PostModerationAction> {
  const response = await apiClient.post<PostModerationAction>(`/posts/${postId}/unhide`, {
    reason,
  });
  return response.data;
}

export async function getCommunityBlockedWords(
  communityId: number,
): Promise<CommunityBlockedWord[]> {
  const response = await apiClient.get<CommunityBlockedWord[]>(
    `/communities/${communityId}/blocked-words`,
  );
  return response.data;
}

export async function createCommunityBlockedWord(
  communityId: number,
  payload: CommunityBlockedWordCreatePayload,
): Promise<CommunityBlockedWord> {
  const response = await apiClient.post<CommunityBlockedWord>(
    `/communities/${communityId}/blocked-words`,
    payload,
  );
  return response.data;
}

export async function deleteCommunityBlockedWord(
  communityId: number,
  blockedWordId: number,
): Promise<void> {
  await apiClient.delete(`/communities/${communityId}/blocked-words/${blockedWordId}`);
}

export async function getEntityReviews(entityId: number): Promise<ReviewListItem[]> {
  const response = await apiClient.get<ReviewListItem[]>(`/entities/${entityId}/reviews`);
  return response.data;
}

export async function getEntityRatingSummary(entityId: number): Promise<EntityRatingSummary> {
  const response = await apiClient.get<EntityRatingSummary>(
    `/entities/${entityId}/rating-summary`,
  );
  return response.data;
}

export async function createReview(payload: ReviewCreatePayload): Promise<Review> {
  const response = await apiClient.post<Review>("/reviews", payload);
  return response.data;
}

export async function reportReview(
  reviewId: number,
  payload: ReviewReportCreatePayload,
): Promise<ReviewReport> {
  const response = await apiClient.post<ReviewReport>(`/reviews/${reviewId}/report`, payload);
  return response.data;
}

export async function getUserCollections(userId: number): Promise<CollectionListItem[]> {
  const response = await apiClient.get<CollectionListItem[]>(`/collections/user/${userId}`);
  return response.data;
}

export async function getMyCollections(): Promise<CollectionListItem[]> {
  const response = await apiClient.get<CollectionListItem[]>("/me/collections");
  return response.data;
}

export async function addToWatchlist(entityId: number): Promise<CollectionItem> {
  const response = await apiClient.post<CollectionItem>(`/me/watchlist/${entityId}`);
  return response.data;
}

export async function removeFromWatchlist(entityId: number): Promise<void> {
  await apiClient.delete(`/me/watchlist/${entityId}`);
}

export async function addToFavourites(entityId: number): Promise<CollectionItem> {
  const response = await apiClient.post<CollectionItem>(`/me/favourites/${entityId}`);
  return response.data;
}

export async function removeFromFavourites(entityId: number): Promise<void> {
  await apiClient.delete(`/me/favourites/${entityId}`);
}
