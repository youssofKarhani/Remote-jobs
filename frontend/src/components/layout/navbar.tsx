"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Briefcase,
  FileUp,
  Settings2,
  User as UserIcon,
  Sparkles,
  LogIn,
  LogOut,
  Compass,
  FolderKanban,
  Menu,
  X,
  Clock,
  ChevronRight,
} from "lucide-react";
import { BrandIcon } from "@/components/layout/brand-icon";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { AuthDialog } from "@/components/auth/auth-dialog";
import { SignOutDialog } from "@/components/auth/sign-out-dialog";
import { Button } from "@/components/ui/button";
import { PipelineScheduleDialog } from "./pipeline-schedule-dialog";

interface NavItem {
  href: string;
  label: string;
  shortLabel: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/onboarding", label: "Get Started", shortLabel: "Guide", icon: Compass },
  { href: "/cv-upload", label: "CV Ingestion", shortLabel: "Upload CV", icon: FileUp },
  { href: "/profile", label: "Evidence Bank", shortLabel: "Evidence", icon: UserIcon },
  { href: "/preferences", label: "Preferences", shortLabel: "Preferences", icon: Settings2 },
  { href: "/jobs", label: "Jobs Feed", shortLabel: "Jobs", icon: Briefcase },
  { href: "/applications", label: "ATS Pipeline", shortLabel: "Pipeline", icon: FolderKanban },
];

export function Navbar() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout, loginAsDemo } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [signOutDialogOpen, setSignOutDialogOpen] = useState(false);

  // Close mobile drawer on navigation
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  // Lock body scroll when mobile drawer is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileMenuOpen]);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl supports-[backdrop-filter]:bg-zinc-950/70">
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between gap-2 sm:gap-4">
        {/* Left Section: Logo & Desktop Navigation */}
        <div className="flex items-center gap-3 lg:gap-4 xl:gap-6 min-w-0">
          <Link href="/" className="flex items-center gap-2.5 group shrink-0">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-violet-500 via-indigo-600 to-sky-500 p-0.5 shadow-lg shadow-violet-500/20 group-hover:shadow-violet-500/40 transition-all duration-300 shrink-0">
              <div className="h-full w-full bg-zinc-950 rounded-[6px] flex items-center justify-center p-1.5">
                <BrandIcon className="w-full h-full group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
            <div className="flex flex-col whitespace-nowrap">
              <span className="font-bold text-sm tracking-tight text-zinc-100 flex items-center gap-1.5">
                FindJobFit
                <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-400 border border-violet-500/20">
                  PLATFORM
                </span>
              </span>
              <span className="text-[10px] text-zinc-400 font-sans hidden 2xl:inline">
                Deterministic AI Pipeline
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-1.5 text-sm font-medium shrink-0">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-1.5 px-2 xl:px-2.5 2xl:px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap shrink-0 transition-all duration-200",
                    isActive
                      ? "bg-zinc-800/90 text-zinc-100 shadow-sm border border-zinc-700/60"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60"
                  )}
                >
                  <Icon className={cn("h-3.5 w-3.5 shrink-0 hidden xl:block", isActive ? "text-violet-400" : "text-zinc-500")} />
                  <span className="hidden 2xl:inline">{item.label}</span>
                  <span className="2xl:hidden">{item.shortLabel}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right Section: Actions & Mobile Toggle */}
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          {isAuthenticated && user ? (
            <div className="flex items-center gap-1.5 sm:gap-2">
              <div className="flex items-center gap-1.5 text-xs text-zinc-300 font-mono bg-zinc-900/90 px-2.5 sm:px-3 py-1.5 rounded-lg border border-zinc-800 whitespace-nowrap">
                <UserIcon className="h-3.5 w-3.5 text-violet-400 shrink-0" />
                <span className="max-w-[100px] sm:max-w-[130px] truncate">{user.full_name || user.email}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSignOutDialogOpen(true)}
                title="Sign out"
                className="h-8 px-2 sm:px-2.5 text-xs border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 shrink-0"
              >
                <LogOut className="h-3.5 w-3.5" />
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 sm:gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={loginAsDemo}
                className="h-8 px-2 sm:px-2.5 text-xs border-violet-900/50 bg-violet-950/30 hover:bg-violet-900/50 text-violet-300 gap-1.5 font-mono whitespace-nowrap shrink-0"
              >
                <Sparkles className="h-3 w-3 text-violet-400 shrink-0" />
                <span className="hidden sm:inline">Quick</span> Demo
              </Button>

              <AuthDialog>
                <Button size="sm" className="h-8 px-2.5 sm:px-3 text-xs bg-violet-600 hover:bg-violet-500 text-white gap-1.5 font-medium whitespace-nowrap shrink-0">
                  <LogIn className="h-3.5 w-3.5 shrink-0" />
                  Sign In
                </Button>
              </AuthDialog>
            </div>
          )}

          {/* Mobile Menu Toggle Button (Visible on < lg) */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
            className="flex lg:hidden items-center justify-center h-8 w-8 rounded-lg border border-zinc-800 bg-zinc-900/60 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors shrink-0"
          >
            {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Mobile & Tablet Drawer (< lg) */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
            aria-hidden="true"
          />

          {/* Drawer Content */}
          <div className="fixed inset-y-0 right-0 w-full max-w-sm bg-zinc-950 border-l border-zinc-800/80 shadow-2xl p-6 flex flex-col justify-between overflow-y-auto animate-in slide-in-from-right duration-200">
            <div className="space-y-6">
              {/* Drawer Header */}
              <div className="flex items-center justify-between pb-4 border-b border-zinc-800/80">
                <div className="flex items-center gap-2.5">
                  <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500 via-indigo-600 to-sky-500 p-0.5 shadow-md shadow-violet-500/20">
                    <div className="h-full w-full bg-zinc-950 rounded-[6px] flex items-center justify-center p-1">
                      <BrandIcon className="w-full h-full" />
                    </div>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-bold text-sm tracking-tight text-zinc-100 flex items-center gap-1.5">
                      FindJobFit
                      <span className="text-[9px] font-mono font-medium px-1.5 py-0.2 rounded bg-violet-500/10 text-violet-400 border border-violet-500/20">
                        PLATFORM
                      </span>
                    </span>
                    <span className="text-[10px] text-zinc-400 font-sans">Deterministic AI Pipeline</span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(false)}
                  aria-label="Close menu"
                  className="h-8 w-8 rounded-lg flex items-center justify-center text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 border border-zinc-800"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* AI Cutoff / Pipeline Schedule Trigger in Mobile */}
              <div className="p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-900/50 space-y-2">
                <div className="flex items-center justify-between text-xs font-medium text-zinc-300">
                  <div className="flex items-center gap-2">
                    <Clock className="h-3.5 w-3.5 text-emerald-400" />
                    <span>AI Batch Schedule</span>
                  </div>
                  <PipelineScheduleDialog className="flex" showPrefix={true} />
                </div>
                <p className="text-[11px] text-zinc-400 leading-relaxed">
                  Automated matching and document tailoring batch runs daily at 06:00 UTC.
                </p>
              </div>

              {/* Navigation Links */}
              <div className="space-y-1">
                <div className="text-[11px] font-mono uppercase tracking-wider text-zinc-500 px-3 pb-1">
                  Navigation
                </div>
                {NAV_ITEMS.map((item) => {
                  const Icon = item.icon;
                  const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(
                        "flex items-center justify-between p-3 rounded-xl text-sm font-medium transition-colors",
                        isActive
                          ? "bg-violet-950/40 text-violet-300 border border-violet-800/50"
                          : "text-zinc-300 hover:text-white hover:bg-zinc-900/60 border border-transparent"
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={cn(
                            "h-8 w-8 rounded-lg flex items-center justify-center border",
                            isActive
                              ? "bg-violet-500/20 border-violet-500/30 text-violet-300"
                              : "bg-zinc-900 border-zinc-800 text-zinc-400"
                          )}
                        >
                          <Icon className="h-4 w-4" />
                        </div>
                        <span>{item.label}</span>
                      </div>
                      <ChevronRight className="h-4 w-4 text-zinc-600" />
                    </Link>
                  );
                })}
              </div>
            </div>

            {/* Mobile Footer Auth Section */}
            <div className="pt-6 border-t border-zinc-800/80 space-y-3">
              {isAuthenticated && user ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2.5 p-3 rounded-xl bg-zinc-900/60 border border-zinc-800">
                    <div className="h-8 w-8 rounded-lg bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400">
                      <UserIcon className="h-4 w-4" />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <span className="text-xs font-semibold text-zinc-200 truncate">
                        {user.full_name || "Candidate"}
                      </span>
                      <span className="text-[11px] text-zinc-400 font-mono truncate">{user.email}</span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setMobileMenuOpen(false);
                      setSignOutDialogOpen(true);
                    }}
                    className="w-full h-9 text-xs border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white gap-2"
                  >
                    <LogOut className="h-3.5 w-3.5" />
                    Sign Out
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      loginAsDemo();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full h-9 text-xs border-violet-900/50 bg-violet-950/30 hover:bg-violet-900/50 text-violet-300 gap-1.5 font-mono"
                  >
                    <Sparkles className="h-3.5 w-3.5 text-violet-400" />
                    Quick Demo Mode
                  </Button>

                  <AuthDialog>
                    <Button
                      size="sm"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full h-9 text-xs bg-violet-600 hover:bg-violet-500 text-white gap-1.5 font-medium"
                    >
                      <LogIn className="h-3.5 w-3.5" />
                      Sign In / Register
                    </Button>
                  </AuthDialog>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Confirmation modal before signing out */}
      <SignOutDialog
        open={signOutDialogOpen}
        onOpenChange={setSignOutDialogOpen}
      />
    </header>
  );
}
