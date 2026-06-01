type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  description?: string;
};

export default function PageHeader({ eyebrow, title, description }: PageHeaderProps) {
  return (
    <header className="mb-8">
      {eyebrow ? (
        <p className="mb-2 text-sm font-medium uppercase tracking-wide text-muted-foreground">
          {eyebrow}
        </p>
      ) : null}
      <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
        {title}
      </h1>
      {description ? (
        <p className="mt-3 max-w-3xl text-base leading-7 text-muted-foreground">
          {description}
        </p>
      ) : null}
    </header>
  );
}
