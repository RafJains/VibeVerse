"use client";

import { useState } from "react";

import PostReportForm from "@/components/PostReportForm";
import PostTypeBadge from "@/components/PostTypeBadge";
import type { CommunityPostListItem, PostReportPayload } from "@/types/post";

type CommunityPostCardProps = {
  canModerate: boolean;
  currentUserId?: number;
  isAuthenticated: boolean;
  isActionRunning: boolean;
  onDelete: (postId: number) => Promise<void>;
  onHide: (postId: number) => Promise<void>;
  onReport: (postId: number, payload: PostReportPayload) => Promise<void>;
  onUnhide: (postId: number) => Promise<void>;
  post: CommunityPostListItem;
};

export default function CommunityPostCard({
  canModerate,
  currentUserId,
  isAuthenticated,
  isActionRunning,
  onDelete,
  onHide,
  onReport,
  onUnhide,
  post,
}: CommunityPostCardProps) {
  const [isReportOpen, setIsReportOpen] = useState(false);

  const isAuthor = currentUserId === post.author_user_id;
  const createdAt = new Date(post.created_at).toLocaleString();

  return (
    <article className="rounded-lg border border-border bg-card p-5">
      <div className="flex flex-wrap items-center gap-2">
        <PostTypeBadge type={post.post_type} />
        {post.spoiler ? (
          <span className="rounded-full bg-yellow-100 px-2.5 py-1 text-xs font-medium text-yellow-800">
            Spoiler
          </span>
        ) : null}
        {post.status !== "published" ? (
          <span className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground">
            {post.status}
          </span>
        ) : null}
        <span className="text-xs text-muted-foreground">User #{post.author_user_id}</span>
      </div>

      <h3 className="mt-4 text-lg font-semibold">{post.title}</h3>
      {post.body ? (
        <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-muted-foreground">
          {post.body}
        </p>
      ) : null}
      {post.media_url ? (
        <a
          href={post.media_url}
          target="_blank"
          rel="noreferrer"
          className="mt-3 block break-all text-sm font-medium text-primary"
        >
          {post.media_url}
        </a>
      ) : null}

      <p className="mt-4 text-xs text-muted-foreground">Created {createdAt}</p>

      <div className="mt-4 flex flex-wrap gap-2">
        {isAuthenticated ? (
          <button
            type="button"
            onClick={() => setIsReportOpen((current) => !current)}
            className="rounded-md border border-border px-3 py-2 text-sm font-medium text-foreground"
          >
            Report
          </button>
        ) : null}

        {isAuthor ? (
          <button
            type="button"
            onClick={() => onDelete(post.id)}
            disabled={isActionRunning}
            className="rounded-md border border-red-200 px-3 py-2 text-sm font-medium text-red-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Delete
          </button>
        ) : null}

        {canModerate && post.status === "published" ? (
          <button
            type="button"
            onClick={() => onHide(post.id)}
            disabled={isActionRunning}
            className="rounded-md border border-border px-3 py-2 text-sm font-medium text-foreground disabled:cursor-not-allowed disabled:opacity-60"
          >
            Hide
          </button>
        ) : null}

        {canModerate && post.status === "hidden" ? (
          <button
            type="button"
            onClick={() => onUnhide(post.id)}
            disabled={isActionRunning}
            className="rounded-md border border-border px-3 py-2 text-sm font-medium text-foreground disabled:cursor-not-allowed disabled:opacity-60"
          >
            Unhide
          </button>
        ) : null}
      </div>

      {isReportOpen ? (
        <PostReportForm
          onCancel={() => setIsReportOpen(false)}
          onSubmit={(payload) => onReport(post.id, payload)}
        />
      ) : null}
    </article>
  );
}
