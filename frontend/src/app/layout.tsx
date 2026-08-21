import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "RemoteJobs Public - AI Job Application Platform",
  description:
    "Multi-user AI job discovery, deterministic filtering, and hallucination-free candidate evidence management platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="relative flex min-h-screen flex-col">
          <Navbar />
          <main className="flex-1 container py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
