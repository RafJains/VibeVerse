import type { CommunityStatus } from "@/types/community";

const statusLabels: Record<CommunityStatus, string> = {
  pending: "Pending",
  approved: "Approved",
  rejected: "Rejected",
  hidden: "Hidden",
};

const statusClasses: Record<CommunityStatus, string> = {
  pending: "bg-yellow-50 text-yellow-800 ring-yellow-200",
  approved: "bg-green-50 text-green-700 ring-green-200",
  rejected: "bg-red-50 text-red-700 ring-red-200",
  hidden: "bg-muted text-muted-foreground ring-border",
};

export default function CommunityStatusBadge({ status }: { status: CommunityStatus }) {
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${statusClasses[status]}`}
    >
      {statusLabels[status]}
    </span>
  );
}
