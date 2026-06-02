"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import CommunityCreateForm from "@/components/CommunityCreateForm";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import { createCommunity, getErrorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { CommunityCreatePayload } from "@/types/community";

export default function CreateCommunityPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCreateCommunity(payload: CommunityCreatePayload) {
    setIsSubmitting(true);
    setError(null);

    try {
      const community = await createCommunity(payload);
      router.push(`/communities/${community.id}`);
    } catch (createError) {
      setError(getErrorMessage(createError));
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return <LoadingState label="Checking session..." />;
  }

  if (!isAuthenticated) {
    return (
      <div>
        <PageHeader
          eyebrow="Communities"
          title="Create Community"
          description="Log in before creating a VibeVerse community."
        />
        <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
          <p>Log in to create a community.</p>
          <Link href="/auth/login" className="mt-3 inline-flex font-medium text-primary">
            Go to login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        eyebrow="Communities"
        title="Create Community"
        description="Create a fan community or request a restricted community type if your account is allowed."
      />
      <CommunityCreateForm
        error={error}
        isSubmitting={isSubmitting}
        onSubmit={handleCreateCommunity}
      />
    </div>
  );
}
