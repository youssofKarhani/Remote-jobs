import type { Metadata } from "next";
import { Inter, Fira_Code } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/navbar";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "RemoteJobs Platform - Deterministic AI Job Engineering",
  description:
    "Upload your raw experience. We engineer the perfect application with zero hallucination and deterministic verifiable evidence.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${firaCode.variable} font-sans min-h-screen bg-zinc-950 text-zinc-100 relative selection:bg-indigo-500/30 selection:text-indigo-200 overflow-x-hidden`}>
        {/* Ambient background subtle lighting */}
        <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
          <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-indigo-600/5 rounded-full blur-[140px]" />
          <div className="absolute top-[40%] right-[-5%] w-[450px] h-[350px] bg-violet-600/5 rounded-full blur-[160px]" />
          <div className="absolute inset-0 bg-grid-pattern opacity-30" />
        </div>

        <div className="relative flex min-h-screen flex-col">
          <Navbar />
          <main className="flex-1 container py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}


