import PageHeader from "@/components/PageHeader";

export default function CollectionsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Future Phase"
        title="Collections"
        description="Watchlists, playlists, favourites, and custom collections now exist in the backend."
      />
      <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
        Collection browsing will be connected after auth/profile flow. For now, entity detail pages can save
        entities to the demo user&apos;s watchlist and favourites.
      </div>
    </div>
  );
}
