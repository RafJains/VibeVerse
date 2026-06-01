export default function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
      {label}
    </div>
  );
}
