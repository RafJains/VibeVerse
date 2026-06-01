import type { EntityListItem } from "@/types/entity";
import EntityCard from "@/components/EntityCard";

export default function EntityGrid({ entities }: { entities: EntityListItem[] }) {
  if (entities.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
        No entities found.
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {entities.map((entity) => (
        <EntityCard key={entity.id} entity={entity} />
      ))}
    </div>
  );
}
