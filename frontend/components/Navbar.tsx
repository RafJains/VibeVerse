"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth-context";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/entities", label: "Entities" },
  { href: "/feed", label: "Feed" },
  { href: "/communities", label: "Communities" },
  { href: "/collections", label: "Collections" },
  { href: "/admin", label: "Admin" },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isLoading, logout, user } = useAuth();

  async function handleLogout() {
    await logout();
    router.push("/");
  }

  return (
    <nav className="border-b border-border bg-card">
      <div className="mx-auto flex min-h-16 w-full max-w-6xl flex-col gap-3 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <Link href="/" className="text-xl font-semibold tracking-tight text-primary">
          VibeVerse
        </Link>
        <div className="flex flex-wrap items-center gap-2">
          {navItems.map((item) => {
            const isActive =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
          <span className="mx-1 hidden h-6 w-px bg-border sm:inline-flex" />
          {isLoading ? (
            <span className="rounded-md px-3 py-2 text-sm text-muted-foreground">
              Checking session...
            </span>
          ) : isAuthenticated && user ? (
            <>
              <span className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground">
                {user.username}
              </span>
              <Link
                href="/communities/create"
                className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                  pathname.startsWith("/communities/create")
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                Create Community
              </Link>
              <Link
                href="/profile"
                className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                  pathname.startsWith("/profile")
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                Profile
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-md border border-border px-3 py-2 text-sm font-medium text-foreground transition hover:bg-muted"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/auth/login"
                className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                  pathname === "/auth/login"
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                Login
              </Link>
              <Link
                href="/auth/signup"
                className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                  pathname === "/auth/signup"
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                Signup
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
