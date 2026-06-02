import type { CommunityType } from "@/types/community";

const typeLabels: Record<CommunityType, string> = {
  fan: "Fan",
  official: "Official",
  platform: "Platform",
};

const typeClasses: Record<CommunityType, string> = {
  fan: "bg-blue-50 text-blue-700 ring-blue-200",
  official: "bg-purple-50 text-purple-700 ring-purple-200",
  platform: "bg-emerald-50 text-emerald-700 ring-emerald-200",
};

export default function CommunityTypeBadge({ type }: { type: CommunityType }) {
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${typeClasses[type]}`}
    >
      {typeLabels[type]}
    </span>
  );
}
