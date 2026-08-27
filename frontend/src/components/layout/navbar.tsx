"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Briefcase, FileUp, Settings2, User, Sparkles, ShieldCheck } from "lucide-react";
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
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl">
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="h-8 w-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200 group-hover:border-indigo-500/50 transition-colors">
              <Sparkles className="h-4 w-4 text-indigo-400" />
            </div>
            <div className="flex flex-col">
              <span className="font-normal text-sm tracking-tight text-zinc-100 flex items-center gap-1.5">
                RemoteJobs
                <span className="text-[10px] font-mono font-medium px-1.5 py-0.2 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                  PUBLIC
                </span>
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center space-x-1 text-sm font-light">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-light transition-all duration-200",
                    isActive
                      ? "bg-zinc-900 text-zinc-100 border border-zinc-800"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50"
                  )}
                >
                  <Icon className={cn("h-3.5 w-3.5", isActive ? "text-indigo-400" : "text-zinc-500")} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-[11px] font-sans text-zinc-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>FastAPI • Online</span>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-sans bg-zinc-900/80 px-2.5 py-1.5 rounded-lg border border-zinc-800">
            <ShieldCheck className="h-3.5 w-3.5 text-indigo-400" />
            <span>Verifiable</span>
          </div>
        </div>
      </div>
    </header>
  );
}


