import type { Metadata } from "next";
import { Inter, Fira_Code } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { AuthProvider } from "@/lib/auth-context";
import { vcopy } from "@/lib/verification-copy";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "FindJobFit - Deterministic AI Job Engineering",
  description:
    vcopy("meta.description"),
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${firaCode.variable} font-sans min-h-screen bg-zinc-950 text-zinc-100 relative selection:bg-blue-600/30 selection:text-blue-200 overflow-x-hidden`}>
        <AuthProvider>
          {/* Ambient background glowing gradients */}
          <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
            <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] opacity-70" />
            <div className="absolute top-[20%] right-[-10%] w-[500px] h-[400px] bg-purple-600/10 rounded-full blur-[140px] opacity-60" />
            <div className="absolute top-[60%] left-[-10%] w-[600px] h-[500px] bg-indigo-600/10 rounded-full blur-[150px] opacity-50" />
            <div className="absolute inset-0 bg-grid-pattern opacity-40" />
          </div>

          <div className="relative flex min-h-screen flex-col">
            <Navbar />
            <main className="flex-1 container py-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {children}
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}

