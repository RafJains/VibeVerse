"use client";

import { FormEvent, useState } from "react";

import type { CommunityCreatePayload, CommunityType } from "@/types/community";

type CommunityCreateFormProps = {
  error?: string | null;
  isSubmitting: boolean;
  onSubmit: (payload: CommunityCreatePayload) => Promise<void>;
};

const communityTypes: Array<{ value: CommunityType; label: string }> = [
  { value: "fan", label: "Fan" },
  { value: "official", label: "Official" },
  { value: "platform", label: "Platform" },
];

export default function CommunityCreateForm({
  error,
  isSubmitting,
  onSubmit,
}: CommunityCreateFormProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [communityType, setCommunityType] = useState<CommunityType>("fan");
  const [entityId, setEntityId] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLocalError(null);

    const trimmedName = name.trim();
    if (!trimmedName) {
      setLocalError("Community name is required.");
      return;
    }

    const trimmedEntityId = entityId.trim();
    let parsedEntityId: number | null = null;
    if (trimmedEntityId) {
      const numericEntityId = Number(trimmedEntityId);
      if (!Number.isInteger(numericEntityId) || numericEntityId <= 0) {
        setLocalError("Entity id must be a positive number.");
        return;
      }
      parsedEntityId = numericEntityId;
    }

    await onSubmit({
      name: trimmedName,
      description: description.trim() || null,
      community_type: communityType,
      entity_id: parsedEntityId,
    });
  }

  const visibleError = localError ?? error;

  return (
    <form onSubmit={handleSubmit} className="grid gap-5 rounded-lg border border-border bg-card p-5">
      <label className="grid gap-2 text-sm font-medium">
        Name
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
          placeholder="Community name"
          required
        />
      </label>

      <label className="grid gap-2 text-sm font-medium">
        Description
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          className="min-h-28 rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
          placeholder="What should members expect here?"
        />
      </label>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="grid gap-2 text-sm font-medium">
          Type
          <select
            value={communityType}
            onChange={(event) => setCommunityType(event.target.value as CommunityType)}
            className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
          >
            {communityTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-2 text-sm font-medium">
          Linked entity id
          <input
            value={entityId}
            onChange={(event) => setEntityId(event.target.value)}
            className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
            inputMode="numeric"
            placeholder="Optional"
          />
        </label>
      </div>

      <div>
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? "Creating..." : "Create community"}
        </button>
      </div>

      {visibleError ? <p className="text-sm text-red-700">{visibleError}</p> : null}
    </form>
  );
}
