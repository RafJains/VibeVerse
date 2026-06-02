import axios from "axios";

import type {
  CollectionItem,
  CollectionListItem,
} from "@/types/collection";
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

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
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

export async function addToWatchlist(userId: number, entityId: number): Promise<CollectionItem> {
  const response = await apiClient.post<CollectionItem>(
    `/users/${userId}/watchlist/${entityId}`,
  );
  return response.data;
}

export async function removeFromWatchlist(userId: number, entityId: number): Promise<void> {
  await apiClient.delete(`/users/${userId}/watchlist/${entityId}`);
}

export async function addToFavourites(userId: number, entityId: number): Promise<CollectionItem> {
  const response = await apiClient.post<CollectionItem>(
    `/users/${userId}/favourites/${entityId}`,
  );
  return response.data;
}

export async function removeFromFavourites(userId: number, entityId: number): Promise<void> {
  await apiClient.delete(`/users/${userId}/favourites/${entityId}`);
}
