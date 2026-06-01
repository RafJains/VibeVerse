import PageHeader from "@/components/PageHeader";

export default function AdminPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Future Phase"
        title="Admin"
        description="Admin workflows will be added later. This page exists only as a route placeholder."
      />
      <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
        Entity administration, ingestion approvals, and feed curation are not implemented in this pass.
      </div>
    </div>
  );
}
