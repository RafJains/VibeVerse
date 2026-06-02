import axios from "axios";

import type {
  CollectionItem,
  CollectionListItem,
} from "@/types/collection";
import type { LoginPayload, SignupPayload, TokenResponse, User } from "@/types/auth";
import type {
  Entity,
  EntityCredit,
  EntityListItem,
  EntityMedia,
  EntityRelation,
  EntityType,
} from "@/types/entity";
import type {
  EntityRatingSummary,
  Review,
  ReviewCreatePayload,
  ReviewListItem,
  ReviewReport,
  ReviewReportCreatePayload,
} from "@/types/review";

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
