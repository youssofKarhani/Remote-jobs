"use client";

import React from "react";
import { ShieldCheck, ArrowRight } from "lucide-react";
import Link from "next/link";

export function CoreGuaranteeBanner() {
  return (
    <section className="relative w-full max-w-5xl mx-auto my-16 md:my-24">
      {/* Subtle outer glow */}
      <div className="absolute inset-0 -z-10 bg-indigo-600/5 rounded-3xl blur-2xl pointer-events-none" />

      {/* Minimalist Banner */}
      <div className="relative rounded-2xl border border-zinc-800 bg-zinc-950/90 px-6 py-8 md:px-10 md:py-10 text-center shadow-xl backdrop-blur-md">
        
        {/* Anti-Hallucination Icon & Tag */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-zinc-900 border border-zinc-800 text-indigo-400 mb-4">
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
          <span>Core Guarantee</span>
        </div>

        {/* Core Guarantee Statement */}
        <h3 className="text-lg sm:text-xl md:text-2xl font-light text-zinc-100 max-w-3xl mx-auto leading-relaxed tracking-tight">
          <span className="font-medium text-white">Deterministic Anti-Hallucination Architecture:</span>{" "}
          <span className="text-zinc-300 font-light">The AI decides what is relevant, not what exists.</span>
        </h3>

        {/* Minimal Subtext & Interactive Link */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-6 text-xs text-zinc-400 font-sans">
          <span className="flex items-center gap-1.5 text-zinc-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Mathematical Set Inclusion Proof
          </span>
          <span className="text-zinc-700">•</span>
          <span className="flex items-center gap-1.5 text-zinc-400">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            Zero Generative Drift
          </span>
          <span className="text-zinc-700">•</span>
          <Link
            href="/cv-upload"
            className="text-indigo-400 hover:text-indigo-300 transition-colors inline-flex items-center gap-1 font-medium"
          >
            Start Ingestion <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

      </div>
    </section>
  );
}
