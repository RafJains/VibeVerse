"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import PageHeader from "@/components/PageHeader";
import { getErrorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function SignupPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: isAuthLoading, signup } = useAuth();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isAuthLoading && isAuthenticated) {
      router.push("/entities");
    }
  }, [isAuthenticated, isAuthLoading, router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await signup({
        email: email.trim(),
        username: username.trim(),
        password,
      });
      router.push("/entities");
    } catch (signupError) {
      setError(getErrorMessage(signupError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-md">
      <PageHeader
        eyebrow="Auth"
        title="Create account"
        description="Create a basic VibeVerse account for reviews and saves."
      />

      <form onSubmit={handleSubmit} className="grid gap-4 rounded-lg border border-border bg-card p-5">
        <label className="grid gap-2 text-sm font-medium">
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
            autoComplete="email"
            placeholder="you@vibeverse.dev"
            required
          />
        </label>

        <label className="grid gap-2 text-sm font-medium">
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
            autoComplete="username"
            required
          />
        </label>

        <label className="grid gap-2 text-sm font-medium">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="min-h-11 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
            autoComplete="new-password"
            minLength={8}
            required
          />
        </label>

        <button
          type="submit"
          disabled={isSubmitting}
          className="min-h-11 rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? "Creating account..." : "Sign up"}
        </button>

        {error ? <p className="text-sm text-red-700">{error}</p> : null}

        <p className="text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/auth/login" className="font-medium text-primary">
            Log in
          </Link>
        </p>
      </form>
    </div>
  );
}
