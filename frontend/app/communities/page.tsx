import PageHeader from "@/components/PageHeader";

export default function CommunitiesPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Future Phase"
        title="Communities"
        description="Organized fandom communities and community-only posts will be implemented later."
      />
      <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
        Community creation, membership, moderation, and posts are out of scope for this pass.
      </div>
    </div>
  );
}
