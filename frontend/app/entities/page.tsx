"use client";

import { FormEvent, useEffect, useState } from "react";

import EntityGrid from "@/components/EntityGrid";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { getEntities, getErrorMessage } from "@/lib/api";
import type { EntityListItem, EntityType } from "@/types/entity";

const entityTypeOptions: Array<{ value: EntityType | ""; label: string }> = [
  { value: "", label: "All types" },
  { value: "film", label: "Film" },
  { value: "series", label: "Series" },
  { value: "song", label: "Song" },
  { value: "album", label: "Album" },
  { value: "game", label: "Game" },
  { value: "sport", label: "Sport" },
  { value: "tournament", label: "Tournament" },
  { value: "team", label: "Team" },
  { value: "person", label: "Person" },
  { value: "live_event", label: "Live Event" },
];

export default function EntitiesPage() {
  const [entities, setEntities] = useState<EntityListItem[]>([]);
  const [entityType, setEntityType] = useState<EntityType | "">("");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    async function loadEntities() {
      setIsLoading(true);
      setError(null);

      try {
        const data = await getEntities({
          entity_type: entityType || undefined,
          search: search || undefined,
          limit: 50,
          offset: 0,
        });

        if (isActive) {
          setEntities(data);
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

    loadEntities();

    return () => {
      isActive = false;
    };
  }, [entityType, search]);

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSearch(searchInput.trim());
  }

  return (
    <div>
      <PageHeader
        eyebrow="Entity System"
        title="Browse entities"
        description="Data is loaded from the FastAPI backend. Subtypes such as anime or k-drama are represented as tags on core entity types."
      />

      <form
        onSubmit={handleSearch}
        className="mb-6 grid gap-3 rounded-lg border border-border bg-card p-4 sm:grid-cols-[1fr_220px_auto]"
      >
        <input
          value={searchInput}
          onChange={(event) => setSearchInput(event.target.value)}
          placeholder="Search by entity name"
          className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
        />
        <select
          value={entityType}
          onChange={(event) => setEntityType(event.target.value as EntityType | "")}
          className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
        >
          {entityTypeOptions.map((option) => (
            <option key={option.value || "all"} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="min-h-11 rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition hover:opacity-90"
        >
          Search
        </button>
      </form>

      {isLoading ? <LoadingState label="Loading entities..." /> : null}
      {!isLoading && error ? <ErrorState message={error} /> : null}
      {!isLoading && !error ? <EntityGrid entities={entities} /> : null}
    </div>
  );
}
