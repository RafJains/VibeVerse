import CommunityPostCard from "@/components/CommunityPostCard";
import type { CommunityPostListItem, PostReportPayload } from "@/types/post";

type CommunityPostListProps = {
  canModerate: boolean;
  currentUserId?: number;
  isAuthenticated: boolean;
  runningActionPostId: number | null;
  onDelete: (postId: number) => Promise<void>;
  onHide: (postId: number) => Promise<void>;
  onReport: (postId: number, payload: PostReportPayload) => Promise<void>;
  onUnhide: (postId: number) => Promise<void>;
  posts: CommunityPostListItem[];
};

export default function CommunityPostList({
  canModerate,
  currentUserId,
  isAuthenticated,
  runningActionPostId,
  onDelete,
  onHide,
  onReport,
  onUnhide,
  posts,
}: CommunityPostListProps) {
  if (posts.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
        No posts in this community yet.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <CommunityPostCard
          key={post.id}
          canModerate={canModerate}
          currentUserId={currentUserId}
          isAuthenticated={isAuthenticated}
          isActionRunning={runningActionPostId === post.id}
          onDelete={onDelete}
          onHide={onHide}
          onReport={onReport}
          onUnhide={onUnhide}
          post={post}
        />
      ))}
    </div>
  );
}
