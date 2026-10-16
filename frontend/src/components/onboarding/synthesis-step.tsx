"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, ArrowRight, ShieldCheck, Sparkles, Briefcase, Wrench, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SynthesisStepProps {
  targetRole: string;
  filesCount: number;
  dataPointsCount: number;
  baselineMatch?: number;
  onProceed: () => void;
  onBack: () => void;
}

export function SynthesisStep({
  targetRole,
  filesCount,
  dataPointsCount,
  baselineMatch = 92,
  onProceed,
  onBack,
}: SynthesisStepProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  // Smooth score counter animation to baselineMatch (92%)
  useEffect(() => {
    let current = 0;
    const increment = baselineMatch / 45;
    const interval = setInterval(() => {
      current += increment;
      if (current >= baselineMatch) {
        setAnimatedScore(baselineMatch);
        clearInterval(interval);
      } else {
        setAnimatedScore(Math.floor(current));
      }
    }, 20);

    return () => clearInterval(interval);
  }, [baselineMatch]);

  // SVG ring calculations
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto w-full py-6 md:py-12 space-y-10"
    >
      {/* Step Breadcrumb */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-zinc-900 border border-zinc-800 text-zinc-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          Step 03 &bull; Profile Synthesis
        </div>
        <h2 className="text-3xl sm:text-4xl md:text-5xl font-light tracking-tight text-zinc-100">
          Profile Synthesis &amp; Match Scoring
        </h2>
      </div>

      {/* Main Synthesis Dashboard Card */}
      <div className="relative rounded-3xl border border-zinc-800 bg-zinc-950/80 p-8 sm:p-12 md:p-14 shadow-2xl backdrop-blur-xl overflow-hidden space-y-10">
        
        {/* Ambient background soft glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-violet-600/10 rounded-full blur-[100px] pointer-events-none" />

        {/* Dynamic Output Message Panel */}
        <div className="relative z-10 text-center space-y-4 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-mono font-medium bg-violet-950/50 border border-violet-800/40 text-violet-300">
            <Sparkles className="w-3.5 h-3.5 text-violet-400" />
            <span>Synthesis Complete</span>
          </div>

          <p className="text-xl sm:text-2xl md:text-3xl font-light text-zinc-100 leading-snug tracking-tight">
            You are targeting{" "}
            <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-violet-300 via-indigo-200 to-purple-300">
              {targetRole}
            </span>
            . Based on your uploaded evidence, we have verified a{" "}
            <span className="font-semibold text-emerald-400 font-mono">
              {baselineMatch}% baseline match
            </span>
            .
          </p>
        </div>

        {/* Minimalist Circular Ring Chart */}
        <div className="relative z-10 flex flex-col items-center justify-center py-4">
          <div className="relative w-48 h-48 flex items-center justify-center">
            
            {/* SVG Ring Gauge */}
            <svg className="w-full h-full -rotate-90" viewBox="0 0 160 160">
              {/* Background Track */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                className="text-zinc-900 stroke-current"
                strokeWidth="10"
                fill="transparent"
              />
              {/* Animated Glowing Value Stroke */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                className="text-violet-500 stroke-current transition-all duration-300 ease-out"
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                style={{
                  filter: "drop-shadow(0 0 12px rgba(139, 92, 246, 0.6))",
                }}
              />
            </svg>

            {/* Centered Percentage Value */}
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-4xl sm:text-5xl font-mono font-bold text-zinc-100 tracking-tight">
                {animatedScore}%
              </span>
              <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-400 mt-1 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                Verified
              </span>
            </div>

          </div>

          <span className="text-xs text-zinc-400 font-mono mt-4">
            Deterministic set overlap calculated across {dataPointsCount} verified data points
          </span>
        </div>

        {/* Evidence Bank Breakdown Grid */}
        <div className="relative z-10 grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-zinc-800/80">
          <div className="p-4 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 space-y-1">
            <div className="flex items-center gap-2 text-zinc-400 text-xs font-mono">
              <Layers className="w-4 h-4 text-violet-400" />
              <span>Evidence Facts</span>
            </div>
            <div className="text-xl font-mono font-semibold text-zinc-100">
              {dataPointsCount}
            </div>
            <p className="text-[11px] text-zinc-400">Canonical deduplicated entries</p>
          </div>

          <div className="p-4 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 space-y-1">
            <div className="flex items-center gap-2 text-zinc-400 text-xs font-mono">
              <Wrench className="w-4 h-4 text-violet-400" />
              <span>Verified Skills</span>
            </div>
            <div className="text-xl font-mono font-semibold text-zinc-100">
              18
            </div>
            <p className="text-[11px] text-zinc-400">Deconstructed competencies</p>
          </div>

          <div className="p-4 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 space-y-1">
            <div className="flex items-center gap-2 text-zinc-400 text-xs font-mono">
              <Briefcase className="w-4 h-4 text-violet-400" />
              <span>Ingested Roles</span>
            </div>
            <div className="text-xl font-mono font-semibold text-zinc-100">
              3 Roles
            </div>
            <p className="text-[11px] text-zinc-400">Merged across {filesCount} source files</p>
          </div>
        </div>

      </div>

      {/* Navigation Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <button
          type="button"
          onClick={onBack}
          className="text-xs font-mono text-zinc-400 hover:text-zinc-300 transition-colors"
        >
          &larr; Re-upload Evidence
        </button>

        <Button
          size="lg"
          onClick={onProceed}
          className="h-12 px-8 rounded-full bg-violet-600 hover:bg-violet-500 text-white font-medium shadow-[0_0_25px_rgba(139,92,246,0.35)] transition-all duration-300 gap-2 text-sm"
        >
          <span>Identify Skill Gaps</span>
          <ArrowRight className="w-4 h-4" />
        </Button>
      </div>

    </motion.div>
  );
}
