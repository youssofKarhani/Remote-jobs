"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Clock,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  LogIn,
  Sliders,
  FileUp,
  Loader2,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { AuthDialog } from "@/components/auth/auth-dialog";
import { profileApi, preferencesApi } from "@/lib/api";

export const DAILY_RUN_UTC_HOUR = 6;
export const DAILY_RUN_UTC_MINUTE = 0;

interface TimeRemaining {
  hours: number;
  minutes: number;
  seconds: number;
  totalSeconds: number;
  isRunning: boolean;
  nextRunDate: Date;
}

function calculateNextRun(): TimeRemaining {
  const now = new Date();
  const nextRun = new Date(now);

  nextRun.setUTCHours(DAILY_RUN_UTC_HOUR, DAILY_RUN_UTC_MINUTE, 0, 0);

  const runningWindowMs = 15 * 60 * 1000;
  const isRunning =
    now.getTime() >= nextRun.getTime() &&
    now.getTime() < nextRun.getTime() + runningWindowMs;

  if (now.getTime() >= nextRun.getTime() + runningWindowMs) {
    nextRun.setUTCDate(nextRun.getUTCDate() + 1);
  }

  const diffMs = Math.max(0, nextRun.getTime() - now.getTime());
  const totalSeconds = Math.floor(diffMs / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return {
    hours,
    minutes,
    seconds,
    totalSeconds,
    isRunning,
    nextRunDate: nextRun,
  };
}

interface MissingItem {
  id: string;
  title: string;
  description: string;
  href: string;
  actionText: string;
  severity: "warning" | "info";
  icon: "file" | "shield" | "sliders";
}

export function PipelineScheduleDialog() {
  const { user, isAuthenticated, loginAsDemo } = useAuth();
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);

  // Time state
  const [timeState, setTimeState] = useState<TimeRemaining>({
    hours: 0,
    minutes: 0,
    seconds: 0,
    totalSeconds: 0,
    isRunning: false,
    nextRunDate: new Date(),
  });

  // Readiness state for authenticated users
  const [readinessLoading, setReadinessLoading] = useState(false);
  const [missingItems, setMissingItems] = useState<MissingItem[]>([]);
  const [verifiedCount, setVerifiedCount] = useState(0);

  useEffect(() => {
    setMounted(true);
    setTimeState(calculateNextRun());

    const interval = setInterval(() => {
      setTimeState(calculateNextRun());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Fetch readiness audit when dialog opens and user is authenticated
  const checkReadiness = useCallback(async () => {
    if (!isAuthenticated) return;
    setReadinessLoading(true);

    try {
      const [profileRes, prefRes] = await Promise.allSettled([
        profileApi.getProfile(),
        preferencesApi.getPreferences(),
      ]);

      const items: MissingItem[] = [];
      let vCount = 0;

      if (profileRes.status === "fulfilled" && profileRes.value) {
        const p = profileRes.value;
        const bank = p.evidence_bank || {};
        const experiences = bank.experiences || [];
        const skills = bank.skills || [];

        const totalBullets = experiences.reduce(
          (acc: number, exp: any) => acc + (exp.bullets?.length || 0),
          0
        );
        const totalItems = totalBullets + skills.length;

        const unverifiedBullets = experiences.reduce(
          (acc: number, exp: any) =>
            acc + (exp.bullets?.filter((b: any) => !b.is_verified).length || 0),
          0
        );
        const unverifiedSkills = skills.filter((s: any) => !s.is_verified).length;
        const unverifiedTotal = unverifiedBullets + unverifiedSkills;

        vCount = totalItems - unverifiedTotal;

        if (totalItems === 0) {
          items.push({
            id: "missing-cv",
            title: "No CV evidence uploaded yet",
            description: "Upload your resume so the AI can extract skills and experience.",
            href: "/cv-upload",
            actionText: "Upload CV",
            severity: "warning",
            icon: "file",
          });
        } else if (unverifiedTotal > 0) {
          items.push({
            id: "unverified-evidence",
            title: `${unverifiedTotal} unverified evidence item${unverifiedTotal > 1 ? "s" : ""}`,
            description: "The AI strictly omits unverified items from tailored CVs to avoid hallucination.",
            href: "/profile",
            actionText: "Verify Evidence",
            severity: "warning",
            icon: "shield",
          });
        }
      } else {
        items.push({
          id: "missing-cv",
          title: "Profile not found",
          description: "Upload a CV to initialize your Evidence Bank before the batch.",
          href: "/cv-upload",
          actionText: "Upload CV",
          severity: "warning",
          icon: "file",
        });
      }

      if (prefRes.status === "fulfilled" && prefRes.value) {
        const pref = prefRes.value;
        if (!pref.target_roles || pref.target_roles.length === 0) {
          items.push({
            id: "missing-roles",
            title: "Target roles not configured",
            description: "Specify desired roles so the AI filters matching job postings accurately.",
            href: "/preferences",
            actionText: "Set Roles",
            severity: "info",
            icon: "sliders",
          });
        }
      }

      setMissingItems(items);
      setVerifiedCount(vCount);
    } catch (e) {
      console.warn("Could not load readiness status:", e);
    } finally {
      setReadinessLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (open && isAuthenticated) {
      checkReadiness();
    }
  }, [open, isAuthenticated, checkReadiness]);

  const handleDemoLogin = async () => {
    setIsDemoLoading(true);
    try {
      await loginAsDemo();
    } finally {
      setIsDemoLoading(false);
    }
  };

  const localTimeString = mounted
    ? timeState.nextRunDate.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      })
    : "06:00 UTC";

  const localTimezoneName = mounted
    ? Intl.DateTimeFormat().resolvedOptions().timeZone
    : "UTC";

  const getBadgeTime = () => {
    if (!mounted) return "06:00 UTC";
    if (timeState.hours > 0) {
      return `${timeState.hours}h ${timeState.minutes}m`;
    }
    return `${timeState.minutes}m ${timeState.seconds}s`;
  };

  const isUrgent = mounted && !timeState.isRunning && timeState.hours === 0 && timeState.minutes < 60;

  return (
    <>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <button
            type="button"
            aria-label="View AI Pipeline Timetable and Cutoff"
            className={`hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-mono whitespace-nowrap shrink-0 transition-all duration-200 cursor-pointer shadow-sm select-none ${
              timeState.isRunning
                ? "bg-violet-950/60 border border-violet-700/60 text-violet-300 hover:bg-violet-900/60"
                : isUrgent
                ? "bg-amber-950/50 border border-amber-700/50 text-amber-300 hover:bg-amber-900/50"
                : "bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 hover:bg-emerald-900/40 hover:border-emerald-700/60"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full shrink-0 ${
                timeState.isRunning
                  ? "bg-violet-400 animate-ping"
                  : isUrgent
                  ? "bg-amber-400 animate-bounce"
                  : "bg-emerald-400 animate-pulse"
              }`}
            />
            <Clock className="h-3 w-3 opacity-80 shrink-0" />
            {mounted && timeState.isRunning ? (
              <span>Pipeline Running...</span>
            ) : (
              <span>
                <span className="hidden xl:inline">Next Run: </span>
                {getBadgeTime()}
              </span>
            )}
          </button>
        </DialogTrigger>

        <DialogContent className="max-w-md bg-zinc-950 border border-zinc-800 text-zinc-100 shadow-2xl p-6 rounded-2xl">
          <DialogHeader className="space-y-1.5 text-left pb-3 border-b border-zinc-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                  <Clock className="h-4 w-4" />
                </div>
                <div>
                  <DialogTitle className="text-base font-bold tracking-tight text-zinc-100">
                    Next AI Batch Run
                  </DialogTitle>
                  <DialogDescription className="text-zinc-400 text-xs">
                    Automated job matching & CV tailoring cutoff
                  </DialogDescription>
                </div>
              </div>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-[10px] font-mono text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Daily &bull; 06:00 UTC
              </span>
            </div>
          </DialogHeader>

          <div className="space-y-4 pt-1">
            {/* Countdown Box */}
            <div className="rounded-xl border border-zinc-800/90 bg-gradient-to-b from-zinc-900/80 to-zinc-950 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                    Batch Countdown
                  </span>
                  <div className="text-xs text-zinc-300 font-mono mt-0.5">
                    {mounted ? `${localTimeString} (${localTimezoneName})` : "06:00 UTC"}
                  </div>
                </div>

                <div className="flex items-center gap-1.5 font-mono">
                  <div className="flex flex-col items-center bg-zinc-950 border border-zinc-800 px-2.5 py-1.5 rounded-lg min-w-[46px]">
                    <span className="text-lg font-bold text-emerald-400 leading-tight">
                      {mounted ? String(timeState.hours).padStart(2, "0") : "--"}
                    </span>
                    <span className="text-[8px] uppercase tracking-wider text-zinc-500">Hours</span>
                  </div>
                  <span className="text-sm font-bold text-zinc-600">:</span>
                  <div className="flex flex-col items-center bg-zinc-950 border border-zinc-800 px-2.5 py-1.5 rounded-lg min-w-[46px]">
                    <span className="text-lg font-bold text-emerald-400 leading-tight">
                      {mounted ? String(timeState.minutes).padStart(2, "0") : "--"}
                    </span>
                    <span className="text-[8px] uppercase tracking-wider text-zinc-500">Mins</span>
                  </div>
                  <span className="text-sm font-bold text-zinc-600">:</span>
                  <div className="flex flex-col items-center bg-zinc-950 border border-zinc-800 px-2.5 py-1.5 rounded-lg min-w-[46px]">
                    <span className="text-lg font-bold text-emerald-400 leading-tight">
                      {mounted ? String(timeState.seconds).padStart(2, "0") : "--"}
                    </span>
                    <span className="text-[8px] uppercase tracking-wider text-zinc-500">Secs</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Dynamic Readiness Section */}
            {!isAuthenticated ? (
              /* Unauthenticated: Push to sign in so we can recommend changes / missing evidence */
              <div className="rounded-xl border border-violet-800/40 bg-gradient-to-br from-violet-950/30 via-zinc-900/60 to-zinc-950 p-4 space-y-3.5">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-violet-500/10 border border-violet-500/20 text-violet-400 shrink-0 mt-0.5">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <div className="space-y-1">
                    <h4 className="text-xs font-semibold text-zinc-100">
                      Sign in to audit what&apos;s missing
                    </h4>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                      Connect your account before the 06:00 UTC batch so our AI can check your evidence bank, flag missing metrics, and recommend role adjustments.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[10px] text-zinc-300 font-mono pt-1 border-t border-zinc-800/60">
                  <div className="flex items-center gap-1.5 text-zinc-400">
                    <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                    <span>Evidence audit</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-zinc-400">
                    <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                    <span>Missing skill alerts</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-zinc-400">
                    <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                    <span>Role preference match</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-zinc-400">
                    <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                    <span>Auto-tailored CV</span>
                  </div>
                </div>

                <div className="flex flex-col gap-2 pt-1">
                  <Button
                    size="sm"
                    className="w-full h-8 text-xs bg-violet-600 hover:bg-violet-500 text-white font-medium gap-1.5 shadow-md shadow-violet-600/20"
                    onClick={() => {
                      setOpen(false);
                      setAuthOpen(true);
                    }}
                  >
                    <LogIn className="h-3.5 w-3.5" />
                    Sign In to Check Your Profile
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={isDemoLoading}
                    onClick={handleDemoLogin}
                    className="w-full h-7 text-[11px] text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50 font-mono gap-1"
                  >
                    {isDemoLoading ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      <Sparkles className="h-3 w-3 text-violet-400" />
                    )}
                    or try 1-Click Demo
                  </Button>
                </div>
              </div>
            ) : (
              /* Authenticated: Real status of what is missing or recommended */
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-zinc-200 flex items-center gap-1.5">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                    What&apos;s Missing Before Next Batch
                  </span>
                  {readinessLoading && (
                    <Loader2 className="h-3 w-3 animate-spin text-zinc-500" />
                  )}
                </div>

                {readinessLoading ? (
                  <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/30 text-center text-xs text-zinc-400">
                    Checking evidence bank & preferences...
                  </div>
                ) : missingItems.length > 0 ? (
                  <div className="space-y-2">
                    {missingItems.map((item) => (
                      <div
                        key={item.id}
                        className={`p-3 rounded-lg border flex items-start justify-between gap-3 ${
                          item.severity === "warning"
                            ? "bg-amber-950/20 border-amber-800/40"
                            : "bg-zinc-900/60 border-zinc-800"
                        }`}
                      >
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-1.5 text-xs font-semibold text-zinc-200">
                            {item.severity === "warning" ? (
                              <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                            ) : (
                              <Sliders className="h-3.5 w-3.5 text-indigo-400 shrink-0" />
                            )}
                            <span>{item.title}</span>
                          </div>
                          <p className="text-[11px] text-zinc-400 leading-snug">
                            {item.description}
                          </p>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          asChild
                          className="h-7 px-2.5 text-[11px] shrink-0 border-zinc-700 bg-zinc-900 hover:bg-zinc-800 text-zinc-200"
                          onClick={() => setOpen(false)}
                        >
                          <Link href={item.href}>
                            {item.actionText} &rarr;
                          </Link>
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  /* 100% Ready */
                  <div className="p-3.5 rounded-xl border border-emerald-800/40 bg-emerald-950/20 space-y-1 text-left">
                    <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
                      <CheckCircle2 className="h-4 w-4" />
                      All Systems Ready for Batch
                    </div>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">
                      Your evidence items ({verifiedCount} verified) and target role preferences are primed. The AI will process fresh jobs at 06:00 UTC.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Minimal Footer */}
            <div className="pt-2 flex items-center justify-between text-xs text-zinc-400 border-t border-zinc-800/80">
              <span className="text-[11px] text-zinc-500 font-mono">
                {isAuthenticated ? `Signed in as ${user?.full_name || user?.email}` : "Deterministic AI Matching"}
              </span>
              <Link
                href="/jobs"
                onClick={() => setOpen(false)}
                className="text-[11px] text-zinc-400 hover:text-zinc-200 flex items-center gap-1 transition-colors"
              >
                Browse jobs feed
                <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Controlled AuthDialog when user clicks Sign In */}
      <AuthDialog open={authOpen} onOpenChange={setAuthOpen} />
    </>
  );
}
