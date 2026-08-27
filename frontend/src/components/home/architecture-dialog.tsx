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
import { ShieldCheck, Database, Sliders, Cpu, FileCheck2, Terminal, Layers } from "lucide-react";
import Link from "next/link";

interface ArchitectureDialogProps {
  children?: React.ReactNode;
}

export function ArchitectureDialog({ children }: ArchitectureDialogProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        {children || (
          <Button variant="outline" size="lg" className="border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800/80 text-zinc-300 gap-2 font-mono text-xs">
            <Terminal className="h-4 w-4 text-blue-400" />
            Read the Architecture.md
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto bg-zinc-950 border border-zinc-800 text-zinc-100 shadow-2xl p-6 md:p-8">
        <DialogHeader className="space-y-2 text-left pb-4 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Layers className="h-5 w-5" />
            </div>
            <DialogTitle className="text-xl font-bold font-mono tracking-tight">
              ARCHITECTURE.md Overview
            </DialogTitle>
          </div>
          <DialogDescription className="text-zinc-400 text-sm">
            Core technical specifications, anti-hallucination guarantees, and deterministic pipeline invariants.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 pt-4 text-sm">
          {/* Architectural Invariant Callout */}
          <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-800/40 space-y-2">
            <div className="flex items-center gap-2 text-blue-400 font-mono text-xs font-semibold uppercase tracking-wider">
              <ShieldCheck className="h-4 w-4" />
              The Central Architectural Invariant
            </div>
            <blockquote className="italic text-zinc-200 text-sm pl-3 border-l-2 border-blue-500">
              &ldquo;LLMs may decide which verified evidence is relevant. They may never decide what evidence exists.&rdquo;
            </blockquote>
          </div>

          {/* 4 Core Pillars */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
                <Database className="h-4 w-4 text-blue-400" />
                1. Canonical Evidence Bank
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Raw resumes are decomposed into immutable entities assigned permanent stable IDs (<code className="text-blue-400 font-mono">EXP_001</code>, <code className="text-purple-400 font-mono">SKILL_001</code>). Only human-verified items can be used in downstream applications.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
                <Sliders className="h-4 w-4 text-amber-400" />
                2. Zero-Cost Deterministic Filtering
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                100% deterministic rules (word boundaries, remote policy, geographic matches, blacklist exclusions) filter thousands of raw jobs instantly with $0.00 compute and zero LLM latency.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
                <Cpu className="h-4 w-4 text-purple-400" />
                3. Two-Stage AI Gateway
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Stage 1 provides high-recall fast pre-screening. Surviving top candidates undergo Stage 2 multi-dimensional deep assessment with structured JSON scoring and explainable reasoning traces.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
                <FileCheck2 className="h-4 w-4 text-emerald-400" />
                4. Static Renderer & Validation Gate
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Before document synthesis, a strict mathematical set check enforces:
                <br />
                <code className="text-emerald-400 font-mono text-[11px] bg-zinc-950 px-1.5 py-0.5 rounded border border-zinc-800 mt-1 inline-block">
                  assert selected_ids.issubset(allowed_ids)
                </code>
              </p>
            </div>
          </div>

          {/* Database Schema Callout */}
          <div className="p-4 rounded-xl bg-zinc-900/40 border border-zinc-800/80 font-mono text-xs space-y-2">
            <span className="text-zinc-400 text-[11px] uppercase tracking-wider font-semibold block">
              12 Normalized Canonical Database Tables
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-zinc-300">
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-blue-300">users</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-blue-300">candidate_profiles</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-blue-300">experiences</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-purple-300">experience_bullets</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-purple-300">bullet_variants</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-purple-300">skills</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-emerald-300">projects</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-emerald-300">education</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-emerald-300">certifications</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-amber-300">candidate_preferences</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-amber-300">raw_jobs</div>
              <div className="p-1.5 bg-zinc-950 rounded border border-zinc-800/60 text-amber-300">normalized_jobs</div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-zinc-800 text-xs text-zinc-400">
            <span>FastAPI • PostgreSQL • Next.js App Router</span>
            <div className="flex gap-3">
              <Link
                href="/profile"
                className="text-blue-400 hover:text-blue-300 hover:underline flex items-center gap-1"
              >
                Inspect Evidence Bank &rarr;
              </Link>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
