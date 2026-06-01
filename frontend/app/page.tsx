import Link from "next/link";

import PageHeader from "@/components/PageHeader";

const sections = [
  {
    href: "/entities",
    title: "Browse Entities",
    description: "Explore structured Film, Series, Song, Album, Person, and future entity records from the backend.",
  },
  {
    href: "/feed",
    title: "Curated Feed",
    description: "Placeholder for the future admin-controlled global discovery feed.",
  },
  {
    href: "/communities",
    title: "Communities",
    description: "Placeholder for organized fandom communities and community-only posts.",
  },
  {
    href: "/collections",
    title: "Collections",
    description: "Placeholder for watchlists, playlists, favourites, and custom collections.",
  },
];

export default function HomePage() {
  return (
    <div>
      <PageHeader
        eyebrow="VibeVerse"
        title="Entertainment intelligence foundation"
        description="Browse the structured entity backend now. Reviews, collections, communities, feed logic, and recommendations are later phases."
      />

      <div className="grid gap-4 sm:grid-cols-2">
        {sections.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="rounded-lg border border-border bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <h2 className="text-lg font-semibold text-card-foreground">{section.title}</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              {section.description}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
