"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ShieldCheck, Database, Sliders, Cpu, FileCheck2, ArrowRight, Layers } from "lucide-react";
import Link from "next/link";

interface ArchitectureDialogProps {
  children?: React.ReactNode;
}

export function ArchitectureDialog({ children }: ArchitectureDialogProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        {children || (
          <Button
            variant="ghost"
            size="lg"
            className="border border-zinc-800 bg-transparent hover:bg-zinc-900 text-zinc-300 hover:text-zinc-100 gap-2 text-sm font-normal rounded-full px-6 h-12"
          >
            <span>Read the Architecture</span>
            <ArrowRight className="h-4 w-4 text-violet-400" />
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto bg-zinc-950 border border-zinc-800 text-zinc-100 shadow-2xl p-6 md:p-8">
        <DialogHeader className="space-y-2 text-left pb-4 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-violet-500/10 border border-violet-500/20 text-violet-400">
              <Layers className="h-5 w-5" />
            </div>
            <DialogTitle className="text-xl font-bold tracking-tight">
              Deterministic Architecture Overview
            </DialogTitle>
          </div>
          <DialogDescription className="text-zinc-400 text-sm">
            Core specifications, anti-hallucination guarantees, and deterministic pipeline invariants.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 pt-4 text-sm">
          {/* Architectural Invariant Callout */}
          <div className="p-4 rounded-xl bg-violet-950/20 border border-violet-800/40 space-y-2">
            <div className="flex items-center gap-2 text-violet-400 font-mono text-xs font-semibold uppercase tracking-wider">
              <ShieldCheck className="h-4 w-4" />
              The Central Architectural Invariant
            </div>
            <blockquote className="italic text-zinc-200 text-sm pl-3 border-l-2 border-violet-500">
              &ldquo;The AI decides what is relevant, not what exists.&rdquo;
            </blockquote>
          </div>

          {/* 4 Core Pillars */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
                <Database className="h-4 w-4 text-violet-400" />
                1. Canonical Evidence Bank
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Raw resumes are decomposed into immutable data points assigned permanent verification IDs. Only verified items from your past experience can be used in downstream applications.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
                <Sliders className="h-4 w-4 text-amber-400" />
                2. Instant Zero-Waste Filtering
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Strict deterministic rules (location boundaries, remote policy, salary thresholds, blacklist criteria) instantly eliminate misaligned roles without delays or guesswork.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
                <Cpu className="h-4 w-4 text-purple-400" />
                3. Two-Stage Compatibility Engine
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Stage 1 executes high-recall pre-screening. Surviving top candidate positions undergo multi-dimensional deep assessment with explainable, verifiable match scores.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
                <FileCheck2 className="h-4 w-4 text-emerald-400" />
                4. Mathematical Set Inclusion Gate
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Before document synthesis, a strict mathematical proof guarantees that every single claim in your tailored CV is an exact subset of your verified profile facts.
              </p>
            </div>
          </div>

          {/* Canonical Profile Elements Callout */}
          <div className="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/80 font-mono text-xs space-y-2">
            <span className="text-zinc-400 text-[11px] uppercase tracking-wider font-semibold block">
              Immutable Verified Data Store
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-zinc-300">
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-violet-300">Profiles</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-violet-300">Experiences</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-violet-300">Verified Bullets</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-purple-300">Role Variants</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-purple-300">Canonical Skills</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-purple-300">Projects</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-emerald-300">Education</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-emerald-300">Certifications</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-emerald-300">Target Matches</div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-zinc-800 text-xs text-zinc-400">
            <span>Deterministic Anti-Hallucination Pipeline</span>
            <div className="flex gap-3">
              <Link
                href="/onboarding"
                className="text-violet-400 hover:text-violet-300 hover:underline flex items-center gap-1"
              >
                Start Onboarding &rarr;
              </Link>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
