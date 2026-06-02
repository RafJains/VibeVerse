"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import CommunityGrid from "@/components/CommunityGrid";
import EntityTypeBadge from "@/components/EntityTypeBadge";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import {
  addToFavourites,
  addToWatchlist,
  createReview,
  getEntity,
  getEntityCommunities,
  getEntityCredits,
  getEntityMedia,
  getEntityRatingSummary,
  getEntityRelations,
  getEntityReviews,
  getErrorMessage,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { CommunityListItem } from "@/types/community";
import type { Entity, EntityCredit, EntityMedia, EntityRelation } from "@/types/entity";
import type { EntityRatingSummary, ReviewListItem, ReviewVisibility } from "@/types/review";

type EntityDetailState = {
  entity: Entity;
  media: EntityMedia[];
  credits: EntityCredit[];
  related: EntityRelation[];
  reviews: ReviewListItem[];
  ratingSummary: EntityRatingSummary;
  communities: CommunityListItem[];
};

type ReviewFormState = {
  title: string;
  body: string;
  rating: string;
  spoiler: boolean;
  visibility: ReviewVisibility;
  tags: string;
};

const initialReviewForm: ReviewFormState = {
  title: "",
  body: "",
  rating: "4.0",
  spoiler: false,
  visibility: "public",
  tags: "",
};

export default function EntityDetailPage() {
  const params = useParams<{ id: string }>();
  const { isAuthenticated, isLoading: isAuthLoading, user } = useAuth();
  const [data, setData] = useState<EntityDetailState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reviewForm, setReviewForm] = useState<ReviewFormState>(initialReviewForm);
  const [reviewMessage, setReviewMessage] = useState<string | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [savingTarget, setSavingTarget] = useState<"watchlist" | "favourites" | null>(null);

  const entityId = Number(params.id);
  const canUseUserActions = isAuthenticated && !isAuthLoading && user !== null;

  async function loadEntityDetails(shouldUpdate: () => boolean = () => true) {
    if (!Number.isInteger(entityId) || entityId <= 0) {
      setError("Invalid entity id.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const [
        entity,
        media,
        credits,
        related,
        reviews,
        ratingSummary,
        communities,
      ] = await Promise.all([
        getEntity(entityId),
        getEntityMedia(entityId),
        getEntityCredits(entityId),
        getEntityRelations(entityId),
        getEntityReviews(entityId),
        getEntityRatingSummary(entityId),
        getEntityCommunities(entityId),
      ]);

      if (shouldUpdate()) {
        setData({ entity, media, credits, related, reviews, ratingSummary, communities });
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
    loadEntityDetails(() => isActive);

    return () => {
      isActive = false;
    };
    // loadEntityDetails is intentionally kept local to this page and keyed by entityId.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entityId]);

  async function handleReviewSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setReviewMessage(null);
    setReviewError(null);

    if (!canUseUserActions || !user) {
      setReviewError("Log in to review this entity.");
      return;
    }

    if (!data) {
      return;
    }

    const body = reviewForm.body.trim();
    if (!body) {
      setReviewError("Review body is required.");
      return;
    }

    setIsSubmittingReview(true);
    try {
      await createReview({
        entity_id: data.entity.id,
        rating: Number(reviewForm.rating),
        title: reviewForm.title.trim() || null,
        body,
        spoiler: reviewForm.spoiler,
        visibility: reviewForm.visibility,
        tags: reviewForm.tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
      });

      setReviewForm(initialReviewForm);
      setReviewMessage("Review submitted.");
      await loadEntityDetails();
    } catch (submitError) {
      setReviewError(getErrorMessage(submitError));
    } finally {
      setIsSubmittingReview(false);
    }
  }

  async function handleSave(target: "watchlist" | "favourites") {
    if (!canUseUserActions || !user) {
      setSaveError("Log in to save this entity.");
      return;
    }

    if (!data) {
      return;
    }

    setSaveMessage(null);
    setSaveError(null);
    setSavingTarget(target);

    try {
      if (target === "watchlist") {
        await addToWatchlist(data.entity.id);
        setSaveMessage("Saved to watchlist.");
      } else {
        await addToFavourites(data.entity.id);
        setSaveMessage("Saved to favourites.");
      }
    } catch (saveFailure) {
      setSaveError(getErrorMessage(saveFailure));
    } finally {
      setSavingTarget(null);
    }
  }

  if (isLoading) {
    return <LoadingState label="Loading entity details..." />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (!data) {
    return <ErrorState message="Entity details are unavailable." />;
  }

  const { entity, media, credits, related, reviews, ratingSummary, communities } = data;

  return (
    <div>
      <Link href="/entities" className="mb-6 inline-flex text-sm font-medium text-primary">
        Back to entities
      </Link>

      <PageHeader
        eyebrow="Entity Detail"
        title={entity.name}
        description={entity.description ?? undefined}
      />

      <section className="mb-6 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center gap-3">
          <EntityTypeBadge type={entity.entity_type} />
          <span className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground">
            {entity.status}
          </span>
          <span className="text-sm text-muted-foreground">
            Popularity {entity.popularity_score.toFixed(1)}
          </span>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          {entity.tags.length > 0 ? (
            entity.tags.map((tag) => (
              <span
                key={tag.id}
                className="rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground"
              >
                {tag.tag}
              </span>
            ))
          ) : (
            <span className="text-sm text-muted-foreground">No tags added yet.</span>
          )}
        </div>
      </section>

      <section className="mb-6 grid gap-4 rounded-lg border border-border bg-card p-5 sm:grid-cols-3">
        <MetricCard
          label="Average rating"
          value={ratingSummary.average_rating?.toFixed(1) ?? "No ratings"}
        />
        <MetricCard label="Reviews" value={ratingSummary.review_count.toString()} />
        <MetricCard label="Ratings" value={ratingSummary.rating_count.toString()} />
      </section>

      <section className="mb-6 rounded-lg border border-border bg-card p-5">
        <h2 className="text-lg font-semibold">Save actions</h2>
        {isAuthLoading ? (
          <p className="mt-2 text-sm text-muted-foreground">Checking session...</p>
        ) : canUseUserActions ? (
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => handleSave("watchlist")}
              disabled={savingTarget !== null}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
            >
              {savingTarget === "watchlist" ? "Saving..." : "Add to watchlist"}
            </button>
            <button
              type="button"
              onClick={() => handleSave("favourites")}
              disabled={savingTarget !== null}
              className="rounded-md border border-border px-4 py-2 text-sm font-medium text-foreground disabled:cursor-not-allowed disabled:opacity-60"
            >
              {savingTarget === "favourites" ? "Saving..." : "Add to favourites"}
            </button>
          </div>
        ) : (
          <p className="mt-2 text-sm text-muted-foreground">
            Log in to review or save this entity.
          </p>
        )}
        {saveMessage ? <p className="mt-3 text-sm text-green-700">{saveMessage}</p> : null}
        {saveError ? <p className="mt-3 text-sm text-red-700">{saveError}</p> : null}
      </section>

      <section className="mb-6">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold">Related Communities</h2>
          {canUseUserActions ? (
            <Link href="/communities/create" className="text-sm font-medium text-primary">
              Create community
            </Link>
          ) : null}
        </div>
        <CommunityGrid
          communities={communities}
          emptyMessage="No related communities linked to this entity yet."
        />
      </section>

      <div className="mb-6 grid gap-6 lg:grid-cols-3">
        <DetailSection title="Media">
          {media.length > 0 ? (
            <ul className="space-y-3">
              {media.map((item) => (
                <li key={item.id} className="rounded-md border border-border p-3">
                  <p className="font-medium">{item.title ?? item.media_type}</p>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 block break-all text-sm text-primary"
                  >
                    {item.url}
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyText text="No media attached yet." />
          )}
        </DetailSection>

        <DetailSection title="Credits">
          {credits.length > 0 ? (
            <ul className="space-y-3">
              {credits.map((credit) => (
                <li key={credit.id} className="rounded-md border border-border p-3 text-sm">
                  <p className="font-medium">{credit.role}</p>
                  <p className="mt-1 text-muted-foreground">
                    Person entity #{credit.person_entity_id}
                    {credit.character_name ? ` as ${credit.character_name}` : ""}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyText text="No credits attached yet." />
          )}
        </DetailSection>

        <DetailSection title="Related">
          {related.length > 0 ? (
            <ul className="space-y-3">
              {related.map((relation) => (
                <li key={relation.id} className="rounded-md border border-border p-3 text-sm">
                  <p className="font-medium">{relation.relation_type}</p>
                  <p className="mt-1 text-muted-foreground">
                    Entity #{relation.source_entity_id} to #{relation.target_entity_id}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyText text="No related entities attached yet." />
          )}
        </DetailSection>
      </div>

      <section className="mb-6 rounded-lg border border-border bg-card p-5">
        <h2 className="text-lg font-semibold">Reviews</h2>
        {reviews.length > 0 ? (
          <div className="mt-4 space-y-4">
            {reviews.map((review) => (
              <article key={review.id} className="rounded-md border border-border p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold">{review.rating.toFixed(1)} / 5</span>
                  {review.spoiler ? (
                    <span className="rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-800">
                      Spoiler
                    </span>
                  ) : null}
                  <span className="text-xs text-muted-foreground">
                    User #{review.user_id}
                  </span>
                </div>
                {review.title ? <h3 className="mt-3 font-semibold">{review.title}</h3> : null}
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{review.body}</p>
                {review.tags.length > 0 ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {review.tags.map((tag) => (
                      <span
                        key={tag.id}
                        className="rounded-full border border-border px-2 py-1 text-xs text-muted-foreground"
                      >
                        {tag.tag}
                      </span>
                    ))}
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-muted-foreground">No reviews yet.</p>
        )}
      </section>

      <section className="rounded-lg border border-border bg-card p-5">
        <h2 className="text-lg font-semibold">Write a review</h2>
        {isAuthLoading ? (
          <p className="mt-2 text-sm text-muted-foreground">Checking session...</p>
        ) : canUseUserActions ? (
          <form onSubmit={handleReviewSubmit} className="mt-5 grid gap-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="grid gap-2 text-sm font-medium">
                Title
                <input
                  value={reviewForm.title}
                  onChange={(event) =>
                    setReviewForm((current) => ({ ...current, title: event.target.value }))
                  }
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                  placeholder="Optional short title"
                />
              </label>
              <label className="grid gap-2 text-sm font-medium">
                Rating
                <select
                  value={reviewForm.rating}
                  onChange={(event) =>
                    setReviewForm((current) => ({ ...current, rating: event.target.value }))
                  }
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                >
                  {[
                    "0.5",
                    "1.0",
                    "1.5",
                    "2.0",
                    "2.5",
                    "3.0",
                    "3.5",
                    "4.0",
                    "4.5",
                    "5.0",
                  ].map((rating) => (
                    <option key={rating} value={rating}>
                      {rating}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label className="grid gap-2 text-sm font-medium">
              Body
              <textarea
                value={reviewForm.body}
                onChange={(event) =>
                  setReviewForm((current) => ({ ...current, body: event.target.value }))
                }
                className="min-h-32 rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
                placeholder="Share your thoughts"
                required
              />
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="grid gap-2 text-sm font-medium">
                Visibility
                <select
                  value={reviewForm.visibility}
                  onChange={(event) =>
                    setReviewForm((current) => ({
                      ...current,
                      visibility: event.target.value as ReviewVisibility,
                    }))
                  }
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                >
                  <option value="public">Public</option>
                  <option value="followers">Followers</option>
                  <option value="private">Private</option>
                </select>
              </label>
              <label className="grid gap-2 text-sm font-medium">
                Tags
                <input
                  value={reviewForm.tags}
                  onChange={(event) =>
                    setReviewForm((current) => ({ ...current, tags: event.target.value }))
                  }
                  className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
                  placeholder="anime, rewatchable"
                />
              </label>
            </div>

            <label className="flex items-center gap-2 text-sm font-medium">
              <input
                type="checkbox"
                checked={reviewForm.spoiler}
                onChange={(event) =>
                  setReviewForm((current) => ({ ...current, spoiler: event.target.checked }))
                }
                className="h-4 w-4"
              />
              Contains spoilers
            </label>

            <div>
              <button
                type="submit"
                disabled={isSubmittingReview}
                className="rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSubmittingReview ? "Submitting..." : "Submit review"}
              </button>
            </div>

            {reviewMessage ? <p className="text-sm text-green-700">{reviewMessage}</p> : null}
            {reviewError ? <p className="text-sm text-red-700">{reviewError}</p> : null}
          </form>
        ) : (
          <p className="mt-2 text-sm text-muted-foreground">
            Log in to review or save this entity.
          </p>
        )}
      </section>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function DetailSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border border-border bg-card p-5">
      <h2 className="mb-4 text-lg font-semibold">{title}</h2>
      {children}
    </section>
  );
}

function EmptyText({ text }: { text: string }) {
  return <p className="text-sm text-muted-foreground">{text}</p>;
}
