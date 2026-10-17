"use client";

import React, { useState, useEffect } from "react";
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
  Calendar,
  Sparkles,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  FileText,
  Sliders,
  Play,
  Info,
} from "lucide-react";

// Default daily scheduled run hour in UTC (06:00 UTC)
// This is optimal for global remote jobs: catches overnight postings and delivers tailored applications for the start of business day.
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

  // If today's run has already passed (or is currently running within a 15-minute window), schedule for tomorrow
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

export function PipelineScheduleDialog() {
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);
  const [timeState, setTimeState] = useState<TimeRemaining>({
    hours: 0,
    minutes: 0,
    seconds: 0,
    totalSeconds: 0,
    isRunning: false,
    nextRunDate: new Date(),
  });

  useEffect(() => {
    setMounted(true);
    setTimeState(calculateNextRun());

    const interval = setInterval(() => {
      setTimeState(calculateNextRun());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Format local user time
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

  // Compact badge text for Navbar
  const getBadgeText = () => {
    if (!mounted) return "Next Run: 06:00 UTC";
    if (timeState.isRunning) return "Pipeline Running...";
    if (timeState.hours > 0) {
      return `Next Run: ${timeState.hours}h ${timeState.minutes}m`;
    }
    return `Next Run: ${timeState.minutes}m ${timeState.seconds}s`;
  };

  const isUrgent = mounted && !timeState.isRunning && timeState.hours === 0 && timeState.minutes < 60;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <button
          type="button"
          aria-label="View AI Pipeline Timetable and Countdown"
          className={`hidden lg:flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-mono transition-all duration-200 cursor-pointer shadow-sm select-none ${
            timeState.isRunning
              ? "bg-violet-950/60 border border-violet-700/60 text-violet-300 hover:bg-violet-900/60 hover:border-violet-600"
              : isUrgent
              ? "bg-amber-950/50 border border-amber-700/50 text-amber-300 hover:bg-amber-900/50 hover:border-amber-600"
              : "bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 hover:bg-emerald-900/40 hover:border-emerald-700/60"
          }`}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              timeState.isRunning
                ? "bg-violet-400 animate-ping"
                : isUrgent
                ? "bg-amber-400 animate-bounce"
                : "bg-emerald-400 animate-pulse"
            }`}
          />
          <Clock className="h-3 w-3 opacity-80" />
          <span>{getBadgeText()}</span>
        </button>
      </DialogTrigger>

      <DialogContent className="max-w-2xl max-h-[88vh] overflow-y-auto bg-zinc-950 border border-zinc-800 text-zinc-100 shadow-2xl p-6 sm:p-8">
        <DialogHeader className="space-y-2 text-left pb-4 border-b border-zinc-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <Clock className="h-5 w-5" />
              </div>
              <div>
                <DialogTitle className="text-xl font-bold tracking-tight text-zinc-100">
                  AI Pipeline Timetable & Cutoff
                </DialogTitle>
                <DialogDescription className="text-zinc-400 text-xs sm:text-sm">
                  Automated daily batch processing schedule & candidate preparation checklist
                </DialogDescription>
              </div>
            </div>
            {timeState.isRunning ? (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-400 font-mono text-xs font-semibold">
                <span className="h-2 w-2 rounded-full bg-violet-400 animate-ping" />
                Processing Batch
              </span>
            ) : (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-semibold">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                Active Schedule
              </span>
            )}
          </div>
        </DialogHeader>

        <div className="space-y-6 pt-2">
          {/* Main Countdown Display */}
          <div className="relative overflow-hidden rounded-xl border border-zinc-800 bg-gradient-to-b from-zinc-900/90 to-zinc-950 p-5">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-center sm:text-left">
                <span className="text-xs font-mono uppercase tracking-wider text-zinc-400 flex items-center justify-center sm:justify-start gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-emerald-400" />
                  Next Scheduled AI Batch
                </span>
                <div className="text-lg font-bold text-zinc-100 mt-1">
                  Daily at 06:00 UTC
                </div>
                <div className="text-xs text-zinc-400 font-mono">
                  {mounted ? `${localTimeString} in ${localTimezoneName}` : "06:00 UTC"}
                </div>
              </div>

              {/* Countdown Digits */}
              <div className="flex items-center gap-2 font-mono">
                <div className="flex flex-col items-center bg-zinc-950/80 border border-zinc-800 px-3 py-2 rounded-lg min-w-[54px]">
                  <span className="text-2xl font-bold text-emerald-400">
                    {mounted ? String(timeState.hours).padStart(2, "0") : "--"}
                  </span>
                  <span className="text-[9px] uppercase tracking-wider text-zinc-500">Hours</span>
                </div>
                <span className="text-xl font-bold text-zinc-600">:</span>
                <div className="flex flex-col items-center bg-zinc-950/80 border border-zinc-800 px-3 py-2 rounded-lg min-w-[54px]">
                  <span className="text-2xl font-bold text-emerald-400">
                    {mounted ? String(timeState.minutes).padStart(2, "0") : "--"}
                  </span>
                  <span className="text-[9px] uppercase tracking-wider text-zinc-500">Mins</span>
                </div>
                <span className="text-xl font-bold text-zinc-600">:</span>
                <div className="flex flex-col items-center bg-zinc-950/80 border border-zinc-800 px-3 py-2 rounded-lg min-w-[54px]">
                  <span className="text-2xl font-bold text-emerald-400">
                    {mounted ? String(timeState.seconds).padStart(2, "0") : "--"}
                  </span>
                  <span className="text-[9px] uppercase tracking-wider text-zinc-500">Secs</span>
                </div>
              </div>
            </div>

            {/* Why this time info */}
            <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-start gap-2 text-xs text-zinc-400">
              <Info className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>Why 06:00 UTC?</strong> This captures overnight postings from international job boards and company ATS feeds, ensuring tailored applications are ready for recruiters at the start of the European and US workdays.
              </span>
            </div>
          </div>

          {/* Action Checklist Before Cutoff */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-violet-400" />
                Prepare Before Cutoff
              </h4>
              <span className="text-[11px] text-zinc-400">Fix your profile details before the batch runs</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Link
                href="/profile"
                onClick={() => setOpen(false)}
                className="group p-3.5 rounded-lg border border-zinc-800 bg-zinc-900/40 hover:bg-zinc-800/60 hover:border-zinc-700 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-semibold text-zinc-200 mb-1">
                    <span className="flex items-center gap-1.5">
                      <FileText className="h-3.5 w-3.5 text-violet-400" />
                      Evidence Bank
                    </span>
                    <ArrowRight className="h-3 w-3 text-zinc-500 group-hover:text-violet-400 transition-colors" />
                  </div>
                  <p className="text-[11px] text-zinc-400 leading-relaxed">
                    Add new metrics & achievements. The AI only uses verified facts to avoid hallucination.
                  </p>
                </div>
                <span className="mt-2 text-[10px] text-violet-400 font-medium group-hover:underline">
                  Update Evidence &rarr;
                </span>
              </Link>

              <Link
                href="/preferences"
                onClick={() => setOpen(false)}
                className="group p-3.5 rounded-lg border border-zinc-800 bg-zinc-900/40 hover:bg-zinc-800/60 hover:border-zinc-700 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-semibold text-zinc-200 mb-1">
                    <span className="flex items-center gap-1.5">
                      <Sliders className="h-3.5 w-3.5 text-indigo-400" />
                      Preferences
                    </span>
                    <ArrowRight className="h-3 w-3 text-zinc-500 group-hover:text-indigo-400 transition-colors" />
                  </div>
                  <p className="text-[11px] text-zinc-400 leading-relaxed">
                    Set target job titles, minimum salary, and remote location filters for strict matching.
                  </p>
                </div>
                <span className="mt-2 text-[10px] text-indigo-400 font-medium group-hover:underline">
                  Edit Preferences &rarr;
                </span>
              </Link>

              <Link
                href="/cv-upload"
                onClick={() => setOpen(false)}
                className="group p-3.5 rounded-lg border border-zinc-800 bg-zinc-900/40 hover:bg-zinc-800/60 hover:border-zinc-700 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-semibold text-zinc-200 mb-1">
                    <span className="flex items-center gap-1.5">
                      <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
                      CV Ingestion
                    </span>
                    <ArrowRight className="h-3 w-3 text-zinc-500 group-hover:text-emerald-400 transition-colors" />
                  </div>
                  <p className="text-[11px] text-zinc-400 leading-relaxed">
                    Upload an updated resume to re-extract skills and structure your master profile.
                  </p>
                </div>
                <span className="mt-2 text-[10px] text-emerald-400 font-medium group-hover:underline">
                  Upload Resume &rarr;
                </span>
              </Link>
            </div>
          </div>

          {/* Timetable / Pipeline Stages breakdown */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-zinc-200">Daily Execution Stages</h4>
            <div className="divide-y divide-zinc-800/60 border border-zinc-800 rounded-lg bg-zinc-900/30 overflow-hidden text-xs">
              <div className="flex items-center justify-between p-3">
                <div className="flex items-center gap-2.5">
                  <span className="h-2 w-2 rounded-full bg-zinc-500" />
                  <span className="font-mono text-zinc-300 font-medium">05:45 UTC</span>
                  <span className="text-zinc-400">Cutoff: Profile, evidence & preference changes lock</span>
                </div>
                <span className="text-[10px] text-zinc-500 font-mono">15 min prior</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-zinc-900/60">
                <div className="flex items-center gap-2.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="font-mono text-emerald-300 font-medium">06:00 UTC</span>
                  <span className="text-zinc-200 font-medium">Job Board Ingestion & Deduplication</span>
                </div>
                <span className="text-[10px] text-emerald-400 font-mono">Batch Start</span>
              </div>

              <div className="flex items-center justify-between p-3">
                <div className="flex items-center gap-2.5">
                  <span className="h-2 w-2 rounded-full bg-violet-400" />
                  <span className="font-mono text-violet-300 font-medium">06:05 UTC</span>
                  <span className="text-zinc-400">Deep AI Compatibility Assessment & Filtering</span>
                </div>
                <span className="text-[10px] text-zinc-500 font-mono">Stage 2</span>
              </div>

              <div className="flex items-center justify-between p-3">
                <div className="flex items-center gap-2.5">
                  <span className="h-2 w-2 rounded-full bg-indigo-400" />
                  <span className="font-mono text-indigo-300 font-medium">06:10 UTC</span>
                  <span className="text-zinc-400">Tailored CV & Cover Letter Generation (Verified Evidence)</span>
                </div>
                <span className="text-[10px] text-zinc-500 font-mono">Stage 3</span>
              </div>

              <div className="flex items-center justify-between p-3">
                <div className="flex items-center gap-2.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  <span className="font-mono text-zinc-300 font-medium">06:15 UTC</span>
                  <span className="text-zinc-400">Applications ready in your ATS Pipeline feed</span>
                </div>
                <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" /> Ready
                </span>
              </div>
            </div>
          </div>

          {/* Quick Action Footer */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-zinc-800">
            <span className="text-xs text-zinc-400">
              Need immediate results instead of waiting?
            </span>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Button
                variant="outline"
                size="sm"
                asChild
                className="w-full sm:w-auto text-xs border-zinc-700 bg-zinc-900 text-zinc-200 hover:bg-zinc-800 gap-1.5"
                onClick={() => setOpen(false)}
              >
                <Link href="/jobs">
                  <Play className="h-3 w-3 text-emerald-400" />
                  Browse Current Jobs
                </Link>
              </Button>
              <Button
                size="sm"
                asChild
                className="w-full sm:w-auto text-xs bg-emerald-600 hover:bg-emerald-500 text-white gap-1.5"
                onClick={() => setOpen(false)}
              >
                <Link href="/applications">
                  View ATS Pipeline
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
