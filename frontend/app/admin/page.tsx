"use client";

import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { useAuth } from "@/lib/auth-context";

export default function AdminPage() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const isAdmin = user?.role === "admin" || user?.role === "super_admin";

  if (isLoading) {
    return <LoadingState label="Checking admin access..." />;
  }

  return (
    <div>
      <PageHeader
        eyebrow="Admin"
        title="Admin"
        description="Administrative surfaces are intentionally narrow in this phase."
      />

      {!isAuthenticated ? (
        <ErrorState
          title="Login required"
          message="Log in with an admin account to view admin placeholders."
        />
      ) : isAdmin ? (
        <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
          Feed management backend is available. Full admin UI will be added later.
        </div>
      ) : (
        <ErrorState
          title="Admin access required"
          message="Admin tools are restricted to admin and super admin accounts."
        />
      )}
    </div>
  );
}
