"use client";

import React from "react";
import { ShieldCheck, ArrowRight } from "lucide-react";
import Link from "next/link";
import { vcopy } from "@/lib/verification-copy";

export function CoreGuaranteeBanner() {
  return (
    <section className="relative w-full my-16 md:my-24">
      {/* Outer ambient glow */}
      <div className="absolute inset-0 -z-10 bg-violet-600/5 rounded-2xl blur-3xl pointer-events-none" />

      {/* Sleek full-width container */}
      <div className="relative w-full rounded-2xl border border-zinc-800 bg-zinc-950/90 p-8 sm:p-10 md:p-12 text-center shadow-2xl backdrop-blur-md overflow-hidden">
        
        {/* Anti-Hallucination Icon & Tag */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-mono font-medium bg-zinc-900 border border-zinc-800 text-violet-400 mb-6">
          <ShieldCheck className="w-3.5 h-3.5 text-violet-400" />
          <span>Core Guarantee</span>
        </div>

        {/* Monospaced Core Statement */}
        <div className="max-w-4xl mx-auto space-y-4">
          <p className="font-mono text-sm sm:text-base md:text-lg lg:text-xl text-zinc-100 tracking-tight leading-relaxed">
            &ldquo;Deterministic Anti-Hallucination Architecture: The AI decides what is relevant, not what exists.&rdquo;
          </p>
        </div>

        {/* Minimal Subtext & Interactive Onboarding Link */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-zinc-400 font-sans">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            {vcopy("visual.guaranteeBanner")}
          </span>
          <span className="text-zinc-700 hidden sm:inline">&bull;</span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
            Zero Generative Drift
          </span>
          <span className="text-zinc-700 hidden sm:inline">&bull;</span>
          <Link
            href="/onboarding"
            className="text-violet-400 hover:text-violet-300 transition-colors inline-flex items-center gap-1.5 font-medium"
          >
            Launch Onboarding Flow <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

      </div>
    </section>
  );
}
