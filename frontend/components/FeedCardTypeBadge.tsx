import type { FeedCardType } from "@/types/feed";

const typeLabels: Record<FeedCardType, string> = {
  trending_entity: "Trending",
  new_release: "New Release",
  trailer_drop: "Trailer Drop",
  top_chart: "Top Chart",
  spotlight: "Spotlight",
  official_update: "Official Update",
  recommendation: "Recommendation",
  announcement: "Announcement",
};

export default function FeedCardTypeBadge({ type }: { type: FeedCardType }) {
  return (
    <span className="rounded-full bg-primary px-2.5 py-1 text-xs font-medium text-primary-foreground">
      {typeLabels[type] ?? type}
    </span>
  );
}
