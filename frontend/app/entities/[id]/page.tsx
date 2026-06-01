"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import EntityTypeBadge from "@/components/EntityTypeBadge";
import ErrorState from "@/components/ErrorState";
import LoadingState from "@/components/LoadingState";
import PageHeader from "@/components/PageHeader";
import {
  getEntity,
  getEntityCredits,
  getEntityMedia,
  getEntityRelations,
  getErrorMessage,
} from "@/lib/api";
import type { Entity, EntityCredit, EntityMedia, EntityRelation } from "@/types/entity";

type EntityDetailState = {
  entity: Entity;
  media: EntityMedia[];
  credits: EntityCredit[];
  related: EntityRelation[];
};

export default function EntityDetailPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<EntityDetailState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    const entityId = Number(params.id);

    async function loadEntity() {
      if (!Number.isInteger(entityId) || entityId <= 0) {
        setError("Invalid entity id.");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const [entity, media, credits, related] = await Promise.all([
          getEntity(entityId),
          getEntityMedia(entityId),
          getEntityCredits(entityId),
          getEntityRelations(entityId),
        ]);

        if (isActive) {
          setData({ entity, media, credits, related });
        }
      } catch (loadError) {
        if (isActive) {
          setError(getErrorMessage(loadError));
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadEntity();

    return () => {
      isActive = false;
    };
  }, [params.id]);

  if (isLoading) {
    return <LoadingState label="Loading entity details..." />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (!data) {
    return <ErrorState message="Entity details are unavailable." />;
  }

  const { entity, media, credits, related } = data;

  return (
    <div>
      <Link href="/entities" className="mb-6 inline-flex text-sm font-medium text-primary">
        Back to entities
      </Link>

      <PageHeader eyebrow="Entity Detail" title={entity.name} description={entity.description ?? undefined} />

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

      <div className="grid gap-6 lg:grid-cols-3">
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
