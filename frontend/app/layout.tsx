import type { Metadata } from "next";

import Navbar from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "VibeVerse",
  description: "Structured entertainment intelligence and fandom platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="mx-auto flex min-h-[calc(100vh-65px)] w-full max-w-6xl flex-col px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
