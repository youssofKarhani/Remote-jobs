"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Briefcase, FileUp, Settings2, User, Sparkles } from "lucide-react";
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
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between">
        <div className="flex items-center space-x-6">
          <Link href="/" className="flex items-center space-x-2 font-bold text-lg">
            <Sparkles className="h-5 w-5 text-primary" />
            <span>RemoteJobs <span className="text-primary text-xs font-semibold uppercase px-1.5 py-0.5 rounded bg-primary/10">Public</span></span>
          </Link>

          <nav className="flex items-center space-x-4 text-sm font-medium">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground font-semibold shadow-sm"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-muted-foreground font-mono bg-muted px-2.5 py-1 rounded">
            Phase 1 & 2
          </span>
        </div>
      </div>
    </header>
  );
}
