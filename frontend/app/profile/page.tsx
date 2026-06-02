"use client";

import Link from "next/link";

import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { useAuth } from "@/lib/auth-context";

export default function ProfilePage() {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <LoadingState label="Loading profile..." />;
  }

  if (!isAuthenticated || !user) {
    return (
      <div>
        <PageHeader
          eyebrow="Profile"
          title="Log in to view your profile"
          description="Your account profile is available after login."
        />
        <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
          <Link href="/auth/login" className="font-medium text-primary">
            Log in
          </Link>{" "}
          to view your profile and account details.
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        eyebrow="Profile"
        title={user.username}
        description="Basic account information from the authenticated session."
      />

      <div className="grid gap-3 rounded-lg border border-border bg-card p-6 text-sm">
        <ProfileRow label="Email" value={user.email} />
        <ProfileRow label="Role" value={user.role} />
        <ProfileRow label="Status" value={user.is_active ? "Active" : "Inactive"} />
        <ProfileRow label="Created" value={new Date(user.created_at).toLocaleString()} />
        <ProfileRow label="Updated" value={new Date(user.updated_at).toLocaleString()} />
      </div>
    </div>
  );
}

function ProfileRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid gap-1 border-b border-border pb-3 last:border-b-0 last:pb-0 sm:grid-cols-[160px_1fr]">
      <span className="font-medium text-foreground">{label}</span>
      <span className="text-muted-foreground">{value}</span>
    </div>
  );
}
