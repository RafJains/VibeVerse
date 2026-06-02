"use client";

import { FormEvent, useState } from "react";

import { getErrorMessage } from "@/lib/api";
import type { PostReportPayload } from "@/types/post";

type PostReportFormProps = {
  onSubmit: (payload: PostReportPayload) => Promise<void>;
  onCancel: () => void;
};

export default function PostReportForm({ onSubmit, onCancel }: PostReportFormProps) {
  const [reason, setReason] = useState("");
  const [details, setDetails] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    setError(null);

    const trimmedReason = reason.trim();
    if (!trimmedReason) {
      setError("Report reason is required.");
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        reason: trimmedReason,
        details: details.trim() || null,
      });
      setReason("");
      setDetails("");
      setMessage("Report submitted.");
    } catch (submitError) {
      setError(getErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 grid gap-3 rounded-md border border-border p-3">
      <label className="grid gap-2 text-sm font-medium">
        Reason
        <input
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          className="min-h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
          placeholder="spoiler, spam, abusive"
          required
        />
      </label>
      <label className="grid gap-2 text-sm font-medium">
        Details
        <textarea
          value={details}
          onChange={(event) => setDetails(event.target.value)}
          className="min-h-20 rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
          placeholder="Optional context"
        />
      </label>
      <div className="flex flex-wrap gap-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? "Reporting..." : "Submit report"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-border px-3 py-2 text-sm font-medium text-foreground"
        >
          Cancel
        </button>
      </div>
      {message ? <p className="text-sm text-green-700">{message}</p> : null}
      {error ? <p className="text-sm text-red-700">{error}</p> : null}
    </form>
  );
}
