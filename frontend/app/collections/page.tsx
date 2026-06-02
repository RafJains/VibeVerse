"use client";

import Link from "next/link";

import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { useAuth } from "@/lib/auth-context";

export default function CollectionsPage() {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <LoadingState label="Loading collections..." />;
  }

  if (!isAuthenticated || !user) {
    return (
      <div>
        <PageHeader
          eyebrow="Collections"
          title="Log in to view collections"
          description="Watchlists, favourites, and custom collections are tied to an account."
        />
        <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
          <Link href="/auth/login" className="font-medium text-primary">
            Log in
          </Link>{" "}
          to view collections connected to your account.
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        eyebrow="Collections"
        title="Collections"
        description={`Collections are connected to ${user.username}'s logged-in account.`}
      />
      <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
        Full collection browsing will be added in a later phase. For now, entity detail pages
        can save entities to your watchlist and favourites.
      </div>
    </div>
  );
}
