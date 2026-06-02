import Link from "next/link";

import FeedCardTypeBadge from "@/components/FeedCardTypeBadge";
import FeedStatusBadge from "@/components/FeedStatusBadge";
import type { FeedCardListItem } from "@/types/feed";

export default function FeedCard({ card }: { card: FeedCardListItem }) {
  const bodyPreview = card.body?.trim();

  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-lg border border-border bg-card shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      {card.image_url ? (
        <Link href={`/feed/${card.id}`} className="block aspect-[16/9] bg-muted">
          <img
            src={card.image_url}
            alt=""
            className="h-full w-full object-cover"
          />
        </Link>
      ) : null}

      <div className="flex flex-1 flex-col p-5">
        <div className="flex flex-wrap items-center gap-2">
          <FeedCardTypeBadge type={card.card_type} />
          <FeedStatusBadge status={card.status} />
          {card.region ? (
            <span className="rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground">
              {card.region}
            </span>
          ) : null}
        </div>

        <Link href={`/feed/${card.id}`} className="mt-4 block">
          <h2 className="text-xl font-semibold text-card-foreground group-hover:text-primary">
            {card.title}
          </h2>
          {card.subtitle ? (
            <p className="mt-2 text-sm font-medium text-muted-foreground">
              {card.subtitle}
            </p>
          ) : null}
        </Link>

        {bodyPreview ? (
          <p className="mt-3 line-clamp-4 text-sm leading-6 text-muted-foreground">
            {bodyPreview}
          </p>
        ) : (
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            No summary available.
          </p>
        )}

        {card.entities.length > 0 ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {card.entities.map((entityLink) => (
              <Link
                key={entityLink.id}
                href={`/entities/${entityLink.entity_id}`}
                className="rounded-full border border-border px-2 py-1 text-xs text-muted-foreground hover:text-primary"
              >
                Entity #{entityLink.entity_id}
              </Link>
            ))}
          </div>
        ) : null}

        <div className="mt-auto flex flex-wrap items-center justify-between gap-3 pt-5 text-sm">
          <Link href={`/feed/${card.id}`} className="font-medium text-primary">
            View card
          </Link>
          {card.source_url ? (
            <a
              href={card.source_url}
              target="_blank"
              rel="noreferrer"
              className="font-medium text-muted-foreground hover:text-primary"
            >
              Source
            </a>
          ) : null}
        </div>
      </div>
    </article>
  );
}
