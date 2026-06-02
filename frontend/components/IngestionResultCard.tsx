import Link from "next/link";

import type { IngestionResult } from "@/types/ingestion";

export default function IngestionResultCard({
  result,
}: {
  result: IngestionResult | null;
}) {
  if (!result) {
    return null;
  }

  return (
    <div className="rounded-md border border-border bg-background p-4 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground">
          Job #{result.job_id}
        </span>
        <span className="rounded-full bg-primary px-2.5 py-1 text-xs font-medium text-primary-foreground">
          {result.status}
        </span>
      </div>
      <p className="mt-3 leading-6 text-muted-foreground">{result.message}</p>
      <dl className="mt-4 grid gap-3 sm:grid-cols-3">
        <ResultField label="Created entity" value={result.created_entity ? "Yes" : "No"} />
        <ResultField label="Updated entity" value={result.updated_entity ? "Yes" : "No"} />
        <div>
          <dt className="text-xs uppercase tracking-wide text-muted-foreground">Entity</dt>
          <dd className="mt-1 font-medium text-foreground">
            {result.entity_id ? (
              <Link href={`/entities/${result.entity_id}`} className="text-primary">
                Entity #{result.entity_id}
              </Link>
            ) : (
              "None"
            )}
          </dd>
        </div>
      </dl>
    </div>
  );
}

function ResultField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="mt-1 font-medium text-foreground">{value}</dd>
    </div>
  );
}
