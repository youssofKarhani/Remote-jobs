"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Briefcase, FileUp, Settings2, User as UserIcon, Sparkles, LogIn, LogOut, Compass, FolderKanban } from "lucide-react";
import { BrandIcon } from "@/components/layout/brand-icon";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { AuthDialog } from "@/components/auth/auth-dialog";
import { Button } from "@/components/ui/button";
import { PipelineScheduleDialog } from "./pipeline-schedule-dialog";

const NAV_ITEMS = [
  { href: "/onboarding", label: "Get Started", icon: Compass },
  { href: "/cv-upload", label: "CV Ingestion", icon: FileUp },
  { href: "/profile", label: "Evidence Bank", icon: UserIcon },
  { href: "/preferences", label: "Preferences", icon: Settings2 },
  { href: "/jobs", label: "Jobs Feed", icon: Briefcase },
  { href: "/applications", label: "ATS Pipeline", icon: FolderKanban },
];

export function Navbar() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout, loginAsDemo } = useAuth();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl supports-[backdrop-filter]:bg-zinc-950/70">
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-violet-500 via-indigo-600 to-sky-500 p-0.5 shadow-lg shadow-violet-500/20 group-hover:shadow-violet-500/40 transition-all duration-300">
              <div className="h-full w-full bg-zinc-950 rounded-[6px] flex items-center justify-center p-1.5">
                <BrandIcon className="w-full h-full group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight text-zinc-100 flex items-center gap-1.5">
                FindJobFit
                <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-400 border border-violet-500/20">
                  PLATFORM
                </span>
              </span>
              <span className="text-[10px] text-zinc-400 font-sans">Deterministic AI Pipeline</span>
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
                  <Icon className={cn("h-3.5 w-3.5", isActive ? "text-violet-400" : "text-zinc-500")} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center space-x-2.5">
          <PipelineScheduleDialog />

          {isAuthenticated && user ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 text-xs text-zinc-300 font-mono bg-zinc-900/90 px-3 py-1.5 rounded-lg border border-zinc-800">
                <UserIcon className="h-3.5 w-3.5 text-violet-400" />
                <span className="max-w-[120px] truncate">{user.full_name || user.email}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={logout}
                title="Sign out"
                className="h-8 px-2.5 text-xs border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
              >
                <LogOut className="h-3.5 w-3.5" />
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={loginAsDemo}
                className="h-8 px-2.5 text-xs border-violet-900/50 bg-violet-950/30 hover:bg-violet-900/50 text-violet-300 gap-1.5 font-mono"
              >
                <Sparkles className="h-3 w-3 text-violet-400" />
                <span className="hidden sm:inline">Quick</span> Demo
              </Button>

              <AuthDialog>
                <Button size="sm" className="h-8 px-3 text-xs bg-violet-600 hover:bg-violet-500 text-white gap-1.5 font-medium">
                  <LogIn className="h-3.5 w-3.5" />
                  Sign In
                </Button>
              </AuthDialog>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
