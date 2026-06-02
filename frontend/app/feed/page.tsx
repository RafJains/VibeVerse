"use client";

import { FormEvent, useEffect, useState } from "react";

import ErrorState from "@/components/ErrorState";
import FeedCardGrid from "@/components/FeedCardGrid";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { getErrorMessage, getGlobalFeed } from "@/lib/api";
import type { FeedCardListItem } from "@/types/feed";

export default function FeedPage() {
  const [cards, setCards] = useState<FeedCardListItem[]>([]);
  const [regionInput, setRegionInput] = useState("");
  const [region, setRegion] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    async function loadFeedCards() {
      setIsLoading(true);
      setError(null);

      try {
        const feedCards = await getGlobalFeed({
          region,
          limit: 50,
        });

        if (isActive) {
          setCards(feedCards);
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

    loadFeedCards();

    return () => {
      isActive = false;
    };
  }, [region]);

  function handleRegionFilter(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setRegion(regionInput.trim().toLowerCase());
  }

  return (
    <div>
      <PageHeader
        eyebrow="Curated Discovery"
        title="Global Feed"
        description="A platform-curated discovery feed managed by VibeVerse. Community posts are not shown here and remain inside their communities."
      />

      <form
        onSubmit={handleRegionFilter}
        className="mb-6 grid gap-3 rounded-lg border border-border bg-card p-4 sm:grid-cols-[1fr_auto_auto]"
      >
        <input
          value={regionInput}
          onChange={(event) => setRegionInput(event.target.value)}
          className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
          placeholder="Filter by region code, for example global"
        />
        <button
          type="submit"
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
        >
          Apply
        </button>
        <button
          type="button"
          onClick={() => {
            setRegionInput("");
            setRegion("");
          }}
          className="rounded-md border border-border px-4 py-2 text-sm font-medium text-foreground"
        >
          Clear
        </button>
      </form>

      <div className="mb-6 rounded-lg border border-border bg-card p-4 text-sm leading-6 text-muted-foreground">
        This page only reads from <span className="font-medium text-foreground">GET /feed/global</span>.
        It does not fetch community post endpoints.
      </div>

      {isLoading ? <LoadingState label="Loading curated feed..." /> : null}
      {!isLoading && error ? <ErrorState message={error} /> : null}
      {!isLoading && !error ? (
        <FeedCardGrid
          cards={cards}
          emptyMessage={
            region
              ? `No curated feed cards found for region "${region}".`
              : "No curated feed cards are available yet."
          }
        />
      ) : null}
    </div>
  );
}
