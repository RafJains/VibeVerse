import PageHeader from "@/components/PageHeader";

export default function CollectionsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Future Phase"
        title="Collections"
        description="Watchlists, playlists, favourites, and custom collections will be implemented later."
      />
      <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
        Collection logic is intentionally not implemented in this frontend foundation pass.
      </div>
    </div>
  );
}
