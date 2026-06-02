"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import CommunityStatusBadge from "@/components/CommunityStatusBadge";
import CommunityTypeBadge from "@/components/CommunityTypeBadge";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import {
  getCommunity,
  getCommunityMembers,
  getErrorMessage,
  joinCommunity,
  leaveCommunity,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Community, CommunityMember } from "@/types/community";

type CommunityDetailState = {
  community: Community;
  members: CommunityMember[];
};

export default function CommunityDetailPage() {
  const params = useParams<{ id: string }>();
  const { isAuthenticated, isLoading: isAuthLoading, user } = useAuth();
  const [data, setData] = useState<CommunityDetailState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isMembershipActionRunning, setIsMembershipActionRunning] = useState(false);

  const communityId = Number(params.id);

  async function loadCommunity(shouldUpdate: () => boolean = () => true) {
    if (!Number.isInteger(communityId) || communityId <= 0) {
      setError("Invalid community id.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const [community, members] = await Promise.all([
        getCommunity(communityId),
        getCommunityMembers(communityId),
      ]);

      if (shouldUpdate()) {
        setData({ community, members });
      }
    } catch (loadError) {
      if (shouldUpdate()) {
        setError(getErrorMessage(loadError));
      }
    } finally {
      if (shouldUpdate()) {
        setIsLoading(false);
      }
    }
  }

  useEffect(() => {
    let isActive = true;
    loadCommunity(() => isActive);

    return () => {
      isActive = false;
    };
    // loadCommunity is scoped to the current route id.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [communityId]);

  async function handleJoin() {
    setActionMessage(null);
    setActionError(null);
    setIsMembershipActionRunning(true);

    try {
      await joinCommunity(communityId);
      setActionMessage("Joined community.");
      await loadCommunity();
    } catch (joinError) {
      setActionError(getErrorMessage(joinError));
    } finally {
      setIsMembershipActionRunning(false);
    }
  }

  async function handleLeave() {
    setActionMessage(null);
    setActionError(null);
    setIsMembershipActionRunning(true);

    try {
      await leaveCommunity(communityId);
      setActionMessage("Left community.");
      await loadCommunity();
    } catch (leaveError) {
      setActionError(getErrorMessage(leaveError));
    } finally {
      setIsMembershipActionRunning(false);
    }
  }

  if (isLoading) {
    return <LoadingState label="Loading community..." />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (!data) {
    return <ErrorState message="Community details are unavailable." />;
  }

  const { community, members } = data;
  const currentMembership = user
    ? members.find((member) => member.user_id === user.id && member.status === "active")
    : undefined;
  const isOwner = currentMembership?.role === "owner";
  const canLeave = Boolean(currentMembership && !isOwner);

  return (
    <div>
      <Link href="/communities" className="mb-6 inline-flex text-sm font-medium text-primary">
        Back to communities
      </Link>

      <PageHeader
        eyebrow="Community Detail"
        title={community.name}
        description={community.description ?? undefined}
      />

      <section className="mb-6 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center gap-2">
          <CommunityTypeBadge type={community.community_type} />
          <CommunityStatusBadge status={community.status} />
          <span className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground">
            {community.member_count.toLocaleString()} members
          </span>
        </div>

        <div className="mt-5 grid gap-3 text-sm text-muted-foreground sm:grid-cols-2">
          <p>Slug: {community.slug}</p>
          <p>Owner user #{community.owner_user_id}</p>
          {community.entity_id ? (
            <Link href={`/entities/${community.entity_id}`} className="font-medium text-primary">
              Linked entity #{community.entity_id}
            </Link>
          ) : (
            <p>No linked entity.</p>
          )}
        </div>
      </section>

      <section className="mb-6 rounded-lg border border-border bg-card p-5">
        <h2 className="text-lg font-semibold">Membership</h2>
        {isAuthLoading ? (
          <p className="mt-2 text-sm text-muted-foreground">Checking session...</p>
        ) : !isAuthenticated ? (
          <p className="mt-2 text-sm text-muted-foreground">
            Log in to join this community.
          </p>
        ) : (
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {isOwner ? (
              <span className="text-sm text-muted-foreground">You own this community.</span>
            ) : canLeave ? (
              <button
                type="button"
                onClick={handleLeave}
                disabled={isMembershipActionRunning}
                className="rounded-md border border-border px-4 py-2 text-sm font-medium text-foreground disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isMembershipActionRunning ? "Leaving..." : "Leave community"}
              </button>
            ) : (
              <button
                type="button"
                onClick={handleJoin}
                disabled={isMembershipActionRunning}
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isMembershipActionRunning ? "Joining..." : "Join community"}
              </button>
            )}
          </div>
        )}
        {actionMessage ? <p className="mt-3 text-sm text-green-700">{actionMessage}</p> : null}
        {actionError ? <p className="mt-3 text-sm text-red-700">{actionError}</p> : null}
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-lg font-semibold">Rules</h2>
          {community.rules.length > 0 ? (
            <ol className="mt-4 space-y-3">
              {[...community.rules]
                .sort((left, right) => left.order_index - right.order_index)
                .map((rule) => (
                  <li key={rule.id} className="rounded-md border border-border p-3">
                    <p className="font-medium">{rule.title}</p>
                    {rule.description ? (
                      <p className="mt-1 text-sm leading-6 text-muted-foreground">
                        {rule.description}
                      </p>
                    ) : null}
                  </li>
                ))}
            </ol>
          ) : (
            <p className="mt-3 text-sm text-muted-foreground">No rules added yet.</p>
          )}
        </section>

        <section className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-lg font-semibold">Members Preview</h2>
          {members.length > 0 ? (
            <ul className="mt-4 space-y-3">
              {members.slice(0, 8).map((member) => (
                <li key={member.id} className="rounded-md border border-border p-3 text-sm">
                  <p className="font-medium">User #{member.user_id}</p>
                  <p className="mt-1 text-muted-foreground">
                    {member.role} - {member.status}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-muted-foreground">No members yet.</p>
          )}
        </section>
      </div>
    </div>
  );
}
