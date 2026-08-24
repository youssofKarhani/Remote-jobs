"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Briefcase, FileUp, Settings2, User, Sparkles, Terminal, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/cv-upload", label: "CV Ingestion", icon: FileUp },
  { href: "/profile", label: "Evidence Bank", icon: User },
  { href: "/preferences", label: "Preferences", icon: Settings2 },
  { href: "/jobs", label: "Jobs Feed", icon: Briefcase },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-zinc-950/75 backdrop-blur-xl supports-[backdrop-filter]:bg-zinc-950/60">
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 p-0.5 shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-all duration-300">
              <div className="h-full w-full bg-zinc-950 rounded-[6px] flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-blue-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight text-zinc-100 flex items-center gap-1.5">
                RemoteJobs
                <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  PLATFORM
                </span>
              </span>
              <span className="text-[10px] text-zinc-400 font-mono">Anti-Hallucination AI</span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center space-x-1 text-sm font-medium">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all duration-200",
                    isActive
                      ? "bg-zinc-800/90 text-zinc-100 shadow-sm border border-zinc-700/60"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60"
                  )}
                >
                  <Icon className={cn("h-3.5 w-3.5", isActive ? "text-blue-400" : "text-zinc-500")} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-950/40 border border-emerald-800/40 text-[11px] font-mono text-emerald-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>FastAPI • Online</span>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-mono bg-zinc-900/80 px-2.5 py-1.5 rounded-lg border border-zinc-800">
            <ShieldCheck className="h-3.5 w-3.5 text-blue-400" />
            <span>v1.0 Immutable</span>
          </div>
        </div>
      </div>
    </header>
  );
}

