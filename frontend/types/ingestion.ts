export type TMDbType = "movie" | "tv" | "person";

export interface TMDbIngestionRequest {
  tmdb_id: number;
  tmdb_type: TMDbType;
  import_media: boolean;
}

export interface TMDbSearchRequest {
  query: string;
}

export interface YouTubeIngestionRequest {
  entity_id: number;
  query?: string | null;
  max_results: number;
}

export interface IngestionJob {
  id: number;
  source_name: string;
  job_type: string;
  status: string;
  message: string | null;
  created_at: string;
  updated_at: string;
}

export interface IngestionResult {
  job_id: number;
  status: string;
  message: string;
  entity_id: number | null;
  created_entity: boolean;
  updated_entity: boolean;
}

export interface TMDbSearchResult {
  id: number;
  media_type?: string;
  title?: string;
  name?: string;
  overview?: string;
  release_date?: string;
  first_air_date?: string;
}

export interface TMDbSearchResponse extends IngestionResult {
  results?: TMDbSearchResult[];
}
