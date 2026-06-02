import type { PostType } from "@/types/post";

const postTypeLabels: Record<PostType, string> = {
  review: "Review",
  hot_take: "Hot Take",
  poll: "Poll",
  meme_edit: "Meme Edit",
  fan_theory: "Fan Theory",
  reaction: "Reaction",
  ranking: "Ranking",
  cover_clip: "Cover Clip",
  discussion: "Discussion",
};

const postTypeClasses: Record<PostType, string> = {
  review: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  hot_take: "bg-red-50 text-red-700 ring-red-200",
  poll: "bg-cyan-50 text-cyan-700 ring-cyan-200",
  meme_edit: "bg-pink-50 text-pink-700 ring-pink-200",
  fan_theory: "bg-purple-50 text-purple-700 ring-purple-200",
  reaction: "bg-orange-50 text-orange-700 ring-orange-200",
  ranking: "bg-amber-50 text-amber-700 ring-amber-200",
  cover_clip: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  discussion: "bg-blue-50 text-blue-700 ring-blue-200",
};

export default function PostTypeBadge({ type }: { type: PostType }) {
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${postTypeClasses[type]}`}
    >
      {postTypeLabels[type]}
    </span>
  );
}
