"use client";

import { FormEvent, useState } from "react";

import type { CommunityPostCreatePayload, PostType } from "@/types/post";

type CommunityPostFormProps = {
  error?: string | null;
  isSubmitting: boolean;
  onSubmit: (payload: CommunityPostCreatePayload) => Promise<void>;
  successMessage?: string | null;
};

const postTypes: Array<{ label: string; value: PostType }> = [
  { label: "Discussion", value: "discussion" },
  { label: "Review", value: "review" },
  { label: "Hot Take", value: "hot_take" },
  { label: "Poll", value: "poll" },
  { label: "Meme Edit", value: "meme_edit" },
  { label: "Fan Theory", value: "fan_theory" },
  { label: "Reaction", value: "reaction" },
  { label: "Ranking", value: "ranking" },
  { label: "Cover Clip", value: "cover_clip" },
];

export default function CommunityPostForm({
  error,
  isSubmitting,
  onSubmit,
  successMessage,
}: CommunityPostFormProps) {
  const [postType, setPostType] = useState<PostType>("discussion");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [mediaUrl, setMediaUrl] = useState("");
  const [spoiler, setSpoiler] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLocalError(null);

    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      setLocalError("Post title is required.");
      return;
    }

    try {
      await onSubmit({
        post_type: postType,
        title: trimmedTitle,
        body: body.trim() || null,
        media_url: mediaUrl.trim() || null,
        spoiler,
      });
      setPostType("discussion");
      setTitle("");
      setBody("");
      setMediaUrl("");
      setSpoiler(false);
    } catch {
      // The parent owns API error display so the form can stay reusable.
    }
  }

  const visibleError = localError ?? error;

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 rounded-lg border border-border bg-card p-5">
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="grid gap-2 text-sm font-medium">
          Post type
          <select
            value={postType}
            onChange={(event) => setPostType(event.target.value as PostType)}
            className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
          >
            {postTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-2 text-sm font-medium">
          Media URL
          <input
            value={mediaUrl}
            onChange={(event) => setMediaUrl(event.target.value)}
            className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
            placeholder="Optional"
          />
        </label>
      </div>

      <label className="grid gap-2 text-sm font-medium">
        Title
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
          placeholder="Post title"
          required
        />
      </label>

      <label className="grid gap-2 text-sm font-medium">
        Body
        <textarea
          value={body}
          onChange={(event) => setBody(event.target.value)}
          className="min-h-28 rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
          placeholder="Share a theory, reaction, ranking, or discussion starter"
        />
      </label>

      <label className="flex items-center gap-2 text-sm font-medium">
        <input
          type="checkbox"
          checked={spoiler}
          onChange={(event) => setSpoiler(event.target.checked)}
          className="h-4 w-4"
        />
        Contains spoilers
      </label>

      <div>
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? "Posting..." : "Create post"}
        </button>
      </div>

      {successMessage ? <p className="text-sm text-green-700">{successMessage}</p> : null}
      {visibleError ? <p className="text-sm text-red-700">{visibleError}</p> : null}
    </form>
  );
}
