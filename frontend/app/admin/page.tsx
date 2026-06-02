"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import AdminSection from "@/components/AdminSection";
import ErrorState from "@/components/ErrorState";
import IngestionJobTable from "@/components/IngestionJobTable";
import IngestionResultCard from "@/components/IngestionResultCard";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import {
  getErrorMessage,
  getIngestionJobs,
  ingestTMDb,
  ingestYouTube,
  searchTMDb,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type {
  IngestionJob,
  IngestionResult,
  TMDbSearchResponse,
  TMDbType,
} from "@/types/ingestion";

export default function AdminPage() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const isAdmin = user?.role === "admin" || user?.role === "super_admin";

  if (isLoading) {
    return <LoadingState label="Checking admin access..." />;
  }

  if (!isAuthenticated) {
    return (
      <div>
        <PageHeader
          eyebrow="Admin"
          title="Admin"
          description="Administrative tools require an admin account."
        />
        <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
          <Link href="/auth/login" className="font-medium text-primary">
            Log in
          </Link>{" "}
          with an admin account to use ingestion tools.
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div>
        <PageHeader
          eyebrow="Admin"
          title="Admin"
          description="Administrative tools are restricted to admin accounts."
        />
        <ErrorState
          title="Admin access required"
          message="Your account does not have permission to run ingestion jobs."
        />
      </div>
    );
  }

  return <AdminIngestionTools />;
}

function AdminIngestionTools() {
  const [tmdbSearchQuery, setTmdbSearchQuery] = useState("");
  const [tmdbSearchResult, setTmdbSearchResult] = useState<TMDbSearchResponse | null>(
    null,
  );
  const [tmdbSearchError, setTmdbSearchError] = useState<string | null>(null);
  const [isSearchingTmdb, setIsSearchingTmdb] = useState(false);

  const [tmdbId, setTmdbId] = useState("");
  const [tmdbType, setTmdbType] = useState<TMDbType>("movie");
  const [importMedia, setImportMedia] = useState(false);
  const [tmdbImportResult, setTmdbImportResult] = useState<IngestionResult | null>(
    null,
  );
  const [tmdbImportError, setTmdbImportError] = useState<string | null>(null);
  const [isImportingTmdb, setIsImportingTmdb] = useState(false);

  const [youtubeEntityId, setYoutubeEntityId] = useState("");
  const [youtubeQuery, setYoutubeQuery] = useState("");
  const [youtubeMaxResults, setYoutubeMaxResults] = useState("5");
  const [youtubeResult, setYoutubeResult] = useState<IngestionResult | null>(null);
  const [youtubeError, setYoutubeError] = useState<string | null>(null);
  const [isImportingYoutube, setIsImportingYoutube] = useState(false);

  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [isLoadingJobs, setIsLoadingJobs] = useState(false);

  const loadJobs = useCallback(async () => {
    setIsLoadingJobs(true);
    setJobsError(null);

    try {
      const recentJobs = await getIngestionJobs({ limit: 20 });
      setJobs(recentJobs);
    } catch (loadError) {
      setJobsError(getErrorMessage(loadError));
    } finally {
      setIsLoadingJobs(false);
    }
  }, []);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  async function handleTmdbSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = tmdbSearchQuery.trim();
    if (!query) {
      setTmdbSearchError("Enter a search query.");
      return;
    }

    setIsSearchingTmdb(true);
    setTmdbSearchError(null);
    setTmdbSearchResult(null);

    try {
      const result = await searchTMDb({ query });
      setTmdbSearchResult(result);
      await loadJobs();
    } catch (searchError) {
      setTmdbSearchError(getErrorMessage(searchError));
    } finally {
      setIsSearchingTmdb(false);
    }
  }

  async function handleTmdbImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const numericTmdbId = Number(tmdbId);
    if (!Number.isInteger(numericTmdbId) || numericTmdbId <= 0) {
      setTmdbImportError("Enter a valid TMDb ID.");
      return;
    }

    setIsImportingTmdb(true);
    setTmdbImportError(null);
    setTmdbImportResult(null);

    try {
      const result = await ingestTMDb({
        tmdb_id: numericTmdbId,
        tmdb_type: tmdbType,
        import_media: importMedia,
      });
      setTmdbImportResult(result);
      await loadJobs();
    } catch (importError) {
      setTmdbImportError(getErrorMessage(importError));
    } finally {
      setIsImportingTmdb(false);
    }
  }

  async function handleYouTubeImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const numericEntityId = Number(youtubeEntityId);
    const numericMaxResults = Number(youtubeMaxResults);
    if (!Number.isInteger(numericEntityId) || numericEntityId <= 0) {
      setYoutubeError("Enter a valid entity ID.");
      return;
    }
    if (
      !Number.isInteger(numericMaxResults) ||
      numericMaxResults < 1 ||
      numericMaxResults > 25
    ) {
      setYoutubeError("Max results must be between 1 and 25.");
      return;
    }

    setIsImportingYoutube(true);
    setYoutubeError(null);
    setYoutubeResult(null);

    try {
      const result = await ingestYouTube({
        entity_id: numericEntityId,
        query: youtubeQuery.trim() || null,
        max_results: numericMaxResults,
      });
      setYoutubeResult(result);
      await loadJobs();
    } catch (importError) {
      setYoutubeError(getErrorMessage(importError));
    } finally {
      setIsImportingYoutube(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Admin"
        title="Ingestion Tools"
        description="Run backend-only TMDb and YouTube ingestion. The frontend calls only VibeVerse backend routes."
      />

      <div className="mb-6 rounded-lg border border-border bg-card p-4 text-sm leading-6 text-muted-foreground">
        External API keys stay on the backend. This page never calls TMDb or YouTube
        directly.
      </div>

      <div className="grid gap-6">
        <AdminSection
          title="TMDb Search"
          description="Stores the raw TMDb search response backend-side and records an ingestion job."
        >
          <form onSubmit={handleTmdbSearch} className="grid gap-3 sm:grid-cols-[1fr_auto]">
            <input
              value={tmdbSearchQuery}
              onChange={(event) => setTmdbSearchQuery(event.target.value)}
              className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
              placeholder="Search TMDb, for example Inception"
            />
            <button
              type="submit"
              disabled={isSearchingTmdb}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSearchingTmdb ? "Searching..." : "Search TMDb"}
            </button>
          </form>

          <div className="mt-4 space-y-3">
            {tmdbSearchError ? <ErrorState message={tmdbSearchError} /> : null}
            <IngestionResultCard result={tmdbSearchResult} />
            {tmdbSearchResult ? (
              <TMDbSearchResults results={tmdbSearchResult.results ?? []} />
            ) : null}
          </div>
        </AdminSection>

        <AdminSection
          title="TMDb Import"
          description="Imports a TMDb movie, TV series, or person into VibeVerse entities through the backend."
        >
          <form onSubmit={handleTmdbImport} className="grid gap-4">
            <div className="grid gap-4 sm:grid-cols-3">
              <label className="grid gap-2 text-sm font-medium">
                TMDb ID
                <input
                  type="number"
                  min="1"
                  value={tmdbId}
                  onChange={(event) => setTmdbId(event.target.value)}
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                  required
                />
              </label>
              <label className="grid gap-2 text-sm font-medium">
                TMDb type
                <select
                  value={tmdbType}
                  onChange={(event) => setTmdbType(event.target.value as TMDbType)}
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                >
                  <option value="movie">Movie</option>
                  <option value="tv">TV</option>
                  <option value="person">Person</option>
                </select>
              </label>
              <label className="flex items-center gap-2 pt-7 text-sm font-medium">
                <input
                  type="checkbox"
                  checked={importMedia}
                  onChange={(event) => setImportMedia(event.target.checked)}
                  className="h-4 w-4"
                />
                Import TMDb media
              </label>
            </div>

            <div>
              <button
                type="submit"
                disabled={isImportingTmdb}
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isImportingTmdb ? "Importing..." : "Import from TMDb"}
              </button>
            </div>
          </form>

          <div className="mt-4 space-y-3">
            {tmdbImportError ? <ErrorState message={tmdbImportError} /> : null}
            <IngestionResultCard result={tmdbImportResult} />
          </div>
        </AdminSection>

        <AdminSection
          title="YouTube Media Import"
          description="Stores YouTube search results as entity media through the backend ingestion route."
        >
          <form onSubmit={handleYouTubeImport} className="grid gap-4">
            <div className="grid gap-4 sm:grid-cols-[160px_1fr_160px]">
              <label className="grid gap-2 text-sm font-medium">
                Entity ID
                <input
                  type="number"
                  min="1"
                  value={youtubeEntityId}
                  onChange={(event) => setYoutubeEntityId(event.target.value)}
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                  required
                />
              </label>
              <label className="grid gap-2 text-sm font-medium">
                Query
                <input
                  value={youtubeQuery}
                  onChange={(event) => setYoutubeQuery(event.target.value)}
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                  placeholder="Optional; defaults to entity name official trailer"
                />
              </label>
              <label className="grid gap-2 text-sm font-medium">
                Max results
                <input
                  type="number"
                  min="1"
                  max="25"
                  value={youtubeMaxResults}
                  onChange={(event) => setYoutubeMaxResults(event.target.value)}
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                />
              </label>
            </div>

            <div>
              <button
                type="submit"
                disabled={isImportingYoutube}
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isImportingYoutube ? "Importing..." : "Import YouTube Media"}
              </button>
            </div>
          </form>

          <div className="mt-4 space-y-3">
            {youtubeError ? <ErrorState message={youtubeError} /> : null}
            <IngestionResultCard result={youtubeResult} />
          </div>
        </AdminSection>

        <AdminSection
          title="Ingestion Jobs"
          description="Recent backend ingestion jobs, including failed missing-key attempts."
        >
          <div className="mb-4">
            <button
              type="button"
              onClick={loadJobs}
              disabled={isLoadingJobs}
              className="rounded-md border border-border px-4 py-2 text-sm font-medium text-foreground disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoadingJobs ? "Loading jobs..." : "Fetch recent jobs"}
            </button>
          </div>
          {jobsError ? <ErrorState message={jobsError} /> : null}
          {!jobsError ? <IngestionJobTable jobs={jobs} /> : null}
        </AdminSection>
      </div>
    </div>
  );
}

function TMDbSearchResults({
  results,
}: {
  results: NonNullable<TMDbSearchResponse["results"]>;
}) {
  if (results.length === 0) {
    return (
      <p className="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">
        Search job completed. This backend response did not include individual TMDb
        result rows.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-md border border-border">
      <table className="min-w-full divide-y divide-border text-left text-sm">
        <thead className="bg-muted text-xs uppercase tracking-wide text-muted-foreground">
          <tr>
            <th className="px-3 py-3 font-medium">TMDb ID</th>
            <th className="px-3 py-3 font-medium">Type</th>
            <th className="px-3 py-3 font-medium">Title/Name</th>
            <th className="px-3 py-3 font-medium">Date</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-card">
          {results.map((result) => (
            <tr key={`${result.media_type ?? "tmdb"}-${result.id}`}>
              <td className="whitespace-nowrap px-3 py-3 font-medium">{result.id}</td>
              <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">
                {result.media_type ?? "unknown"}
              </td>
              <td className="px-3 py-3 text-muted-foreground">
                {result.title ?? result.name ?? "Untitled"}
              </td>
              <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">
                {result.release_date ?? result.first_air_date ?? "No date"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
