import FeedCard from "@/components/FeedCard";
import type { FeedCardListItem } from "@/types/feed";

type FeedCardGridProps = {
  cards: FeedCardListItem[];
  emptyMessage?: string;
};

export default function FeedCardGrid({
  cards,
  emptyMessage = "No curated feed cards are available yet.",
}: FeedCardGridProps) {
  if (cards.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map((card) => (
        <FeedCard key={card.id} card={card} />
      ))}
    </div>
  );
}
