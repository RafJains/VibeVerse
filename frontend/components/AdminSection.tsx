import type { ReactNode } from "react";

type AdminSectionProps = {
  title: string;
  description?: string;
  children: ReactNode;
};

export default function AdminSection({
  title,
  description,
  children,
}: AdminSectionProps) {
  return (
    <section className="rounded-lg border border-border bg-card p-5">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-card-foreground">{title}</h2>
        {description ? (
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {children}
    </section>
  );
}
