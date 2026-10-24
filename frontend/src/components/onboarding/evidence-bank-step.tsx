"use client";

import React from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Briefcase,
  Wrench,
  FolderGit2,
  GraduationCap,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  FileCheck2,
  CheckCircle2,
  SlidersHorizontal,
  FileText,
  RotateCcw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { vcopy } from "@/lib/verification-copy";

export interface ExtractionSummaryData {
  experiencesCount: number;
  bulletsCount: number;
  skillsCount: number;
  projectsCount: number;
  educationCount: number;
  certificationsCount: number;
  sourceFilename?: string;
}

interface EvidenceBankStepProps {
  targetRole: string;
  summary: ExtractionSummaryData;
  onUploadAnother: () => void;
}

export function EvidenceBankStep({
  targetRole,
  summary,
  onUploadAnother,
}: EvidenceBankStepProps) {
  const totalVerifiedEntities =
    (summary.experiencesCount || 0) +
    (summary.bulletsCount || 0) +
    (summary.skillsCount || 0) +
    (summary.projectsCount || 0) +
    (summary.educationCount || 0) +
    (summary.certificationsCount || 0);

  const stats = [
    {
      label: "Experience Roles",
      value: summary.experiencesCount || 0,
      icon: Briefcase,
      color: "text-blue-400",
      border: "border-blue-500/20",
      bg: "bg-blue-950/20",
    },
    {
      label: vcopy("onboarding.achievementsLabel"),
      value: summary.bulletsCount || 0,
      icon: FileCheck2,
      color: "text-emerald-400",
      border: "border-emerald-500/20",
      bg: "bg-emerald-950/20",
    },
    {
      label: "Extracted Skills",
      value: summary.skillsCount || 0,
      icon: Wrench,
      color: "text-violet-400",
      border: "border-violet-500/20",
      bg: "bg-violet-950/20",
    },
    {
      label: "Projects & Education",
      value: (summary.projectsCount || 0) + (summary.educationCount || 0),
      icon: FolderGit2,
      color: "text-amber-400",
      border: "border-amber-500/20",
      bg: "bg-amber-950/20",
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto w-full py-6 md:py-10 space-y-8"
    >
      {/* Top Breadcrumb */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-mono font-medium bg-emerald-950/40 border border-emerald-800/40 text-emerald-300">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>{vcopy("onboarding.bankReady")}</span>
        </div>

        <h2 className="text-3xl sm:text-4xl md:text-5xl font-light tracking-tight text-zinc-100">
          Your profile is ingested.
        </h2>

        <p className="text-sm md:text-base text-zinc-400 font-light max-w-2xl mx-auto leading-relaxed">
          Targeting <span className="text-zinc-200 font-medium">{targetRole || "Software Engineer"}</span>. 
          {vcopy("onboarding.bankSubtitle")}
        </p>
      </div>

      {/* Main Evidence Bank Card */}
      <div className="relative rounded-3xl border border-zinc-800 bg-zinc-950/80 p-6 sm:p-10 md:p-12 shadow-2xl backdrop-blur-xl overflow-hidden space-y-8">
        {/* Soft background ambient glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-violet-600/10 rounded-full blur-[100px] pointer-events-none" />

        {/* Real Extracted Entities Grid */}
        <div className="relative z-10 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800/80 pb-4">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono uppercase tracking-wider text-zinc-300">
                {vcopy("onboarding.recordsIngested")}
              </span>
            </div>
            {summary.sourceFilename && (
              <span className="text-xs font-mono text-zinc-400 bg-zinc-900 px-3 py-1 rounded-md border border-zinc-800 truncate max-w-xs">
                Source: {summary.sourceFilename}
              </span>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
            {stats.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.label}
                  className={`p-4 rounded-2xl border ${item.border} ${item.bg} backdrop-blur-sm flex flex-col justify-between space-y-2`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-zinc-400">
                      {item.label}
                    </span>
                    <Icon className={`w-4 h-4 ${item.color}`} />
                  </div>
                  <div className="text-2xl sm:text-3xl font-bold font-mono text-zinc-100">
                    {item.value}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Zero-Hallucination Tailoring Banner */}
        <div className="relative z-10 rounded-2xl border border-violet-500/30 bg-violet-950/20 p-5 sm:p-6 space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-violet-950/80 border border-violet-800/40 text-violet-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-zinc-100">
                How Tailored Applications Work
              </h4>
              <p className="text-xs text-zinc-400">
                No arbitrary scores or fake percentages — compatibility is calculated for each specific job.
              </p>
            </div>
          </div>
          <p className="text-xs text-zinc-300 leading-relaxed">
            When you select any vacancy in the Jobs Feed, our engine extracts the vacancy&apos;s exact technical requirements and matches them against your {totalVerifiedEntities > 0 ? `${totalVerifiedEntities} career data points` : vcopy("bank.name")}. You can generate a tailored Word (.docx) CV and personalized cover letter with <strong>0% hallucination guarantee</strong> in seconds.
          </p>
        </div>

        {/* Primary Action Buttons */}
        <div className="relative z-10 flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Link href="/jobs" className="w-full sm:w-auto">
            <Button
              size="lg"
              className="w-full sm:w-auto h-12 px-8 rounded-full bg-violet-600 hover:bg-violet-500 text-white font-medium shadow-[0_0_25px_rgba(139,92,246,0.35)] hover:shadow-[0_0_35px_rgba(139,92,246,0.5)] transition-all duration-300 gap-2.5 text-xs sm:text-sm"
            >
              <Sparkles className="h-4 w-4" />
              <span>Explore Jobs &amp; Curate Applications</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>

          <Link href="/profile" className="w-full sm:w-auto">
            <Button
              size="lg"
              variant="outline"
              className="w-full sm:w-auto h-12 px-6 rounded-full border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white text-xs sm:text-sm transition-colors gap-2"
            >
              <FileText className="h-4 w-4 text-zinc-400" />
              <span>{vcopy("onboarding.reviewBank")}</span>
            </Button>
          </Link>

          <Link href="/preferences" className="w-full sm:w-auto">
            <Button
              size="lg"
              variant="ghost"
              className="w-full sm:w-auto h-12 px-5 rounded-full border border-zinc-800/80 bg-transparent hover:bg-zinc-900/60 text-zinc-400 hover:text-zinc-200 text-xs sm:text-sm transition-colors gap-2"
            >
              <SlidersHorizontal className="h-3.5 w-3.5" />
              <span>Job Preferences</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Upload Another Callout */}
      <div className="flex items-center justify-between px-2 text-xs font-mono text-zinc-400">
        <button
          type="button"
          onClick={onUploadAnother}
          className="hover:text-zinc-200 transition-colors inline-flex items-center gap-1.5"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Upload Another CV or Document</span>
        </button>
        <span className="text-zinc-400">
          {vcopy("onboarding.canonicalTag")}
        </span>
      </div>
    </motion.div>
  );
}
