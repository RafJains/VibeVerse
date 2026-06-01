import Link from "next/link";

import type { EntityListItem } from "@/types/entity";
import EntityTypeBadge from "@/components/EntityTypeBadge";

export default function EntityCard({ entity }: { entity: EntityListItem }) {
  return (
    <Link
      href={`/entities/${entity.id}`}
      className="group flex h-full flex-col rounded-lg border border-border bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <EntityTypeBadge type={entity.entity_type} />
        <span className="rounded-full bg-muted px-2 py-1 text-xs text-muted-foreground">
          {entity.status}
        </span>
      </div>
      <h2 className="mt-4 text-xl font-semibold text-card-foreground group-hover:text-primary">
        {entity.name}
      </h2>
      <p className="mt-3 line-clamp-3 text-sm leading-6 text-muted-foreground">
        {entity.description ?? "No description available yet."}
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        {entity.tags.slice(0, 4).map((tag) => (
          <span
            key={tag.id}
            className="rounded-full border border-border px-2 py-1 text-xs text-muted-foreground"
          >
            {tag.tag}
          </span>
        ))}
      </div>
      <p className="mt-auto pt-5 text-sm font-medium text-foreground">
        Popularity {entity.popularity_score.toFixed(1)}
      </p>
    </Link>
  );
}
