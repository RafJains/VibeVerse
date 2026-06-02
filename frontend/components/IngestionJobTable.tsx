import type { IngestionJob } from "@/types/ingestion";

type IngestionJobTableProps = {
  jobs: IngestionJob[];
};

export default function IngestionJobTable({ jobs }: IngestionJobTableProps) {
  if (jobs.length === 0) {
    return (
      <div className="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">
        No ingestion jobs found.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-md border border-border">
      <table className="min-w-full divide-y divide-border text-left text-sm">
        <thead className="bg-muted text-xs uppercase tracking-wide text-muted-foreground">
          <tr>
            <th className="px-3 py-3 font-medium">ID</th>
            <th className="px-3 py-3 font-medium">Source</th>
            <th className="px-3 py-3 font-medium">Type</th>
            <th className="px-3 py-3 font-medium">Status</th>
            <th className="px-3 py-3 font-medium">Message</th>
            <th className="px-3 py-3 font-medium">Created</th>
            <th className="px-3 py-3 font-medium">Updated</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-card">
          {jobs.map((job) => (
            <tr key={job.id}>
              <td className="whitespace-nowrap px-3 py-3 font-medium text-foreground">
                {job.id}
              </td>
              <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">
                {job.source_name}
              </td>
              <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">
                {job.job_type}
              </td>
              <td className="whitespace-nowrap px-3 py-3">
                <span className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground">
                  {job.status}
                </span>
              </td>
              <td className="min-w-64 px-3 py-3 text-muted-foreground">
                {job.message ?? "No message"}
              </td>
              <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">
                {formatDate(job.created_at)}
              </td>
              <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">
                {formatDate(job.updated_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}
