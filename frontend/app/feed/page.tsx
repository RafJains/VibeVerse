import PageHeader from "@/components/PageHeader";

export default function FeedPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Future Phase"
        title="Curated feed"
        description="The global feed will be platform-controlled and admin-approved. Feed logic is intentionally not implemented in this frontend foundation pass."
      />
      <PhaseCard />
    </div>
  );
}

function PhaseCard() {
  return (
    <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
      No normal user posts are shown here. Curated feed cards will be added in a later phase.
    </div>
  );
}
