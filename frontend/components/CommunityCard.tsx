import Link from "next/link";

import CommunityStatusBadge from "@/components/CommunityStatusBadge";
import CommunityTypeBadge from "@/components/CommunityTypeBadge";
import type { CommunityListItem } from "@/types/community";

export default function CommunityCard({ community }: { community: CommunityListItem }) {
  return (
    <Link
      href={`/communities/${community.id}`}
      className="group flex h-full flex-col rounded-lg border border-border bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="flex flex-wrap items-center gap-2">
        <CommunityTypeBadge type={community.community_type} />
        <CommunityStatusBadge status={community.status} />
      </div>

      <h2 className="mt-4 text-xl font-semibold text-card-foreground group-hover:text-primary">
        {community.name}
      </h2>
      <p className="mt-3 line-clamp-3 text-sm leading-6 text-muted-foreground">
        {community.description ?? "No description available yet."}
      </p>

      <div className="mt-auto flex flex-wrap items-center gap-3 pt-5 text-sm text-muted-foreground">
        <span>{community.member_count.toLocaleString()} members</span>
        {community.entity_id ? <span>Entity #{community.entity_id}</span> : null}
      </div>
    </Link>
  );
}
