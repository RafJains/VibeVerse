import axios from "axios";

import type {
  Entity,
  EntityCredit,
  EntityListItem,
  EntityMedia,
  EntityRelation,
  EntityType,
} from "@/types/entity";

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
