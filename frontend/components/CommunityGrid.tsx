import CommunityCard from "@/components/CommunityCard";
import type { CommunityListItem } from "@/types/community";

type CommunityGridProps = {
  communities: CommunityListItem[];
  emptyMessage?: string;
};

export default function CommunityGrid({
  communities,
  emptyMessage = "No communities found.",
}: CommunityGridProps) {
  if (communities.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {communities.map((community) => (
        <CommunityCard key={community.id} community={community} />
      ))}
    </div>
  );
}
