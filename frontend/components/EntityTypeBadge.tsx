import type { EntityType } from "@/types/entity";

const labels: Record<EntityType, string> = {
  film: "Film",
  series: "Series",
  song: "Song",
  album: "Album",
  game: "Game",
  sport: "Sport",
  tournament: "Tournament",
  team: "Team",
  person: "Person",
  live_event: "Live Event",
};

export default function EntityTypeBadge({ type }: { type: EntityType }) {
  return (
    <span className="inline-flex items-center rounded-full bg-primary px-2.5 py-1 text-xs font-medium text-primary-foreground">
      {labels[type]}
    </span>
  );
}
