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
import { ShieldCheck, Database, Sliders, Cpu, FileCheck2, BookOpen } from "lucide-react";
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
            className="text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/50 font-normal text-sm"
          >
            Read the Architecture
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto bg-zinc-950 border border-zinc-800 text-zinc-100 shadow-2xl p-6 sm:p-8">
        <DialogHeader className="space-y-2 text-left pb-4 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-indigo-400">
              <BookOpen className="h-4 w-4" />
            </div>
            <DialogTitle className="text-lg font-medium tracking-tight text-zinc-100">
              System Architecture
            </DialogTitle>
          </div>
          <DialogDescription className="text-zinc-400 text-xs font-light">
            Core principles and deterministic anti-hallucination invariants.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 pt-3 text-sm">
          {/* Architectural Invariant Callout */}
          <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-medium uppercase tracking-wider">
              <ShieldCheck className="h-3.5 w-3.5" />
              Core Invariant
            </div>
            <blockquote className="italic text-zinc-200 text-sm pl-3 border-l-2 border-indigo-500 font-light">
              &ldquo;The AI decides what is relevant, not what exists.&rdquo;
            </blockquote>
          </div>

          {/* 4 Core Pillars */}
          <div className="grid sm:grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center gap-2 text-zinc-200 font-medium text-xs">
                <Database className="h-3.5 w-3.5 text-indigo-400" />
                1. Canonical Evidence Bank
              </div>
              <p className="text-xs text-zinc-400 font-light leading-relaxed">
                Raw resumes are decomposed into immutable entities with permanent verified IDs. Only verified items enter synthesized applications.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center gap-2 text-zinc-200 font-medium text-xs">
                <Sliders className="h-3.5 w-3.5 text-indigo-400" />
                2. Zero-Cost Filtering
              </div>
              <p className="text-xs text-zinc-400 font-light leading-relaxed">
                Deterministic rules (remote-only, location boundaries, exclusion keywords) eliminate irrelevant roles before LLM evaluation.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center gap-2 text-zinc-200 font-medium text-xs">
                <Cpu className="h-3.5 w-3.5 text-indigo-400" />
                3. High-Confidence Matching
              </div>
              <p className="text-xs text-zinc-400 font-light leading-relaxed">
                Surviving jobs are scored against your verified profile for technical alignment and explainable compatibility.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-1.5">
              <div className="flex items-center gap-2 text-zinc-200 font-medium text-xs">
                <FileCheck2 className="h-3.5 w-3.5 text-indigo-400" />
                4. Cryptographic Validation Gate
              </div>
              <p className="text-xs text-zinc-400 font-light leading-relaxed">
                Every synthesized claim is validated with a mathematical subset check against the verified evidence bank.
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-zinc-800 text-xs text-zinc-400 font-sans">
            <span>FastAPI • PostgreSQL • Next.js</span>
            <Link
              href="/profile"
              className="text-indigo-400 hover:text-indigo-300 hover:underline flex items-center gap-1 font-medium"
            >
              Open Evidence Bank &rarr;
            </Link>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

