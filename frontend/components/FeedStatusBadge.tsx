import type { FeedCardStatus } from "@/types/feed";

const statusLabels: Record<FeedCardStatus, string> = {
  draft: "Draft",
  pending_review: "Pending Review",
  approved: "Approved",
  rejected: "Rejected",
  published: "Published",
  archived: "Archived",
};

export default function FeedStatusBadge({ status }: { status: FeedCardStatus }) {
  return (
    <span className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground">
      {statusLabels[status] ?? status}
    </span>
  );
}
