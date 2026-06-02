"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import CommunityGrid from "@/components/CommunityGrid";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { getCommunities, getErrorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { CommunityListItem, CommunityType } from "@/types/community";

export default function CommunitiesPage() {
  const { isAuthenticated } = useAuth();
  const [communities, setCommunities] = useState<CommunityListItem[]>([]);
  const [searchInput, setSearchInput] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [communityType, setCommunityType] = useState<CommunityType | "">("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    async function loadCommunities() {
      setIsLoading(true);
      setError(null);

      try {
        const communityList = await getCommunities({
          community_type: communityType,
          search: searchTerm,
          limit: 50,
        });

        if (isActive) {
          setCommunities(communityList);
        }
      } catch (loadError) {
        if (isActive) {
          setError(getErrorMessage(loadError));
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadCommunities();

    return () => {
      isActive = false;
    };
  }, [communityType, searchTerm]);

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSearchTerm(searchInput.trim());
  }

  return (
    <div>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <PageHeader
          eyebrow="Communities"
          title="Browse Communities"
          description="Find entity-linked and platform communities created by VibeVerse users."
        />
        {isAuthenticated ? (
          <Link
            href="/communities/create"
            className="inline-flex rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
          >
            Create Community
          </Link>
        ) : null}
      </div>

      <form
        onSubmit={handleSearch}
        className="mb-6 grid gap-3 rounded-lg border border-border bg-card p-4 sm:grid-cols-[1fr_180px_auto]"
      >
        <input
          value={searchInput}
          onChange={(event) => setSearchInput(event.target.value)}
          className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
          placeholder="Search communities"
        />
        <select
          value={communityType}
          onChange={(event) => setCommunityType(event.target.value as CommunityType | "")}
          className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
        >
          <option value="">All types</option>
          <option value="fan">Fan</option>
          <option value="official">Official</option>
          <option value="platform">Platform</option>
        </select>
        <button
          type="submit"
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
        >
          Search
        </button>
      </form>

      {isLoading ? <LoadingState label="Loading communities..." /> : null}
      {!isLoading && error ? <ErrorState message={error} /> : null}
      {!isLoading && !error ? <CommunityGrid communities={communities} /> : null}
    </div>
  );
}
