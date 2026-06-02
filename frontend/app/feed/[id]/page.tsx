"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import ErrorState from "@/components/ErrorState";
import FeedCardTypeBadge from "@/components/FeedCardTypeBadge";
import FeedStatusBadge from "@/components/FeedStatusBadge";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { getErrorMessage, getFeedCard } from "@/lib/api";
import type { FeedCard as FeedCardDetail } from "@/types/feed";

export default function FeedCardDetailPage() {
  const params = useParams<{ id: string }>();
  const [card, setCard] = useState<FeedCardDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const feedCardId = Number(params.id);

  useEffect(() => {
    let isActive = true;

    async function loadFeedCard() {
      if (!Number.isInteger(feedCardId) || feedCardId <= 0) {
        setError("Invalid feed card id.");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const feedCard = await getFeedCard(feedCardId);

        if (isActive) {
          setCard(feedCard);
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

    loadFeedCard();

    return () => {
      isActive = false;
    };
  }, [feedCardId]);

  if (isLoading) {
    return <LoadingState label="Loading feed card..." />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (!card) {
    return <ErrorState message="Feed card details are unavailable." />;
  }

  return (
    <div>
      <Link href="/feed" className="mb-6 inline-flex text-sm font-medium text-primary">
        Back to feed
      </Link>

      <PageHeader
        eyebrow="Curated Feed Card"
        title={card.title}
        description={card.subtitle ?? undefined}
      />

      {card.image_url ? (
        <div className="mb-6 overflow-hidden rounded-lg border border-border bg-card">
          <img src={card.image_url} alt="" className="max-h-[420px] w-full object-cover" />
        </div>
      ) : null}

      <section className="mb-6 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center gap-2">
          <FeedCardTypeBadge type={card.card_type} />
          <FeedStatusBadge status={card.status} />
          {card.region ? (
            <span className="rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground">
              {card.region}
            </span>
          ) : null}
        </div>

        <div className="mt-5 space-y-4 text-sm leading-6 text-muted-foreground">
          {card.body ? <p>{card.body}</p> : <p>No body content available.</p>}
          {card.source_url ? (
            <a
              href={card.source_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex font-medium text-primary"
            >
              View source
            </a>
          ) : null}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-5">
        <h2 className="text-lg font-semibold">Linked Entities</h2>
        {card.entities.length > 0 ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {card.entities.map((entityLink) => (
              <Link
                key={entityLink.id}
                href={`/entities/${entityLink.entity_id}`}
                className="rounded-full border border-border px-2.5 py-1 text-sm text-muted-foreground hover:text-primary"
              >
                Entity #{entityLink.entity_id}
              </Link>
            ))}
          </div>
        ) : (
          <p className="mt-3 text-sm text-muted-foreground">
            No linked entities attached to this curated card.
          </p>
        )}
      </section>
    </div>
  );
}
