import PageHeader from "@/components/PageHeader";

export default function ProfilePage() {
  return (
    <div>
      <PageHeader
        eyebrow="Future Phase"
        title="Profile"
        description="User profile UI will be added after auth and account foundations are implemented."
      />
      <div className="rounded-lg border border-border bg-card p-6 text-sm leading-6 text-muted-foreground">
        Login, signup, preferences, and profile editing are out of scope for this pass.
      </div>
    </div>
  );
}
