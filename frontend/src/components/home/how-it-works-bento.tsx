"use client";

import React, { useState } from "react";
import {
  Database,
  Sliders,
  Cpu,
  FileCheck2,
  CheckCircle2,
  ShieldAlert,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Check,
  FileText,
  Lock,
  Search,
  Zap,
  Layers,
  ChevronRight
} from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import Link from "next/link";

export function HowItWorksBento() {
  // Step 1 interactive state: Verify Draft toggle
  const [isDraftVerified, setIsDraftVerified] = useState(false);

  // Step 2 interactive states: Preferences toggles
  const [strictRemote, setStrictRemote] = useState(true);
  const [locationMatch, setLocationMatch] = useState(true);
  const [keywordExclusions, setKeywordExclusions] = useState(true);

  // Step 3 interactive state: Active stage tab
  const [activeStage, setActiveStage] = useState<"prescreen" | "deep">("deep");

  // Step 4 interactive state: Active document format preview
  const [docFormat, setDocFormat] = useState<"pdf" | "docx">("pdf");

  // Calculate filtered count dynamically based on Step 2 toggles
  const totalRawJobs = 1420;
  const filteredJobsCount = (strictRemote ? 120 : 640) - (locationMatch ? 60 : 0) - (keywordExclusions ? 32 : 0);

  return (
    <section className="space-y-8">
      <div className="text-center space-y-3 max-w-2xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-blue-950/60 text-blue-400 border border-blue-800/40">
          <Zap className="h-3.5 w-3.5" />
          The Deterministic Pipeline
        </div>
        <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-zinc-100">
          How It Works
        </h2>
        <p className="text-sm md:text-base text-zinc-400 leading-relaxed">
          From unorganized resume text to mathematically validated, hallucination-free job applications in four zero-compromise steps.
        </p>
      </div>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* STEP 1: Ingestion (The Canonical Evidence Bank) */}
        <div className="group relative rounded-2xl border border-zinc-800/80 bg-zinc-950/70 p-6 md:p-7 flex flex-col justify-between space-y-6 glass-card glass-card-hover overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-blue-500/5 rounded-full blur-2xl pointer-events-none" />

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="h-9 w-9 rounded-xl bg-blue-950/60 border border-blue-800/50 flex items-center justify-center text-blue-400">
                  <Database className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-blue-400">
                    Step 01 &bull; Ingestion
                  </span>
                  <h3 className="text-lg font-bold text-zinc-100">
                    The Canonical Evidence Bank
                  </h3>
                </div>
              </div>
              <Link href="/cv-upload" className="text-xs font-mono text-zinc-400 hover:text-blue-400 flex items-center gap-1 transition-colors">
                Ingest <ChevronRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            <p className="text-xs md:text-sm text-zinc-400 leading-relaxed">
              Upload your base CV. Our extraction engine deconstructs it into immutable, verified data points. You review the drafts, we lock them in.
            </p>

            {/* Visual Mockup */}
            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-zinc-800/60 pb-2">
                <span className="text-[11px] text-zinc-400 flex items-center gap-1.5">
                  <FileText className="h-3 w-3 text-blue-400" />
                  Extracted Evidence Blocks
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-zinc-300 font-medium">Verify Draft</span>
                  <Switch
                    checked={isDraftVerified}
                    onCheckedChange={setIsDraftVerified}
                    className="data-[state=checked]:bg-emerald-600"
                  />
                </div>
              </div>

              {/* Discrete Blocks */}
              <div className="space-y-2">
                {/* Block 1: EXP_001 */}
                <div
                  className={`p-2.5 rounded-lg border transition-all duration-300 ${
                    isDraftVerified
                      ? "bg-emerald-950/20 border-emerald-800/40 text-zinc-200"
                      : "bg-zinc-950/80 border-zinc-800 text-zinc-300"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      [EXP_001]
                    </span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                        isDraftVerified
                          ? "bg-emerald-900/60 text-emerald-300 border border-emerald-700/50"
                          : "bg-amber-900/40 text-amber-300 border border-amber-700/40"
                      }`}
                    >
                      {isDraftVerified ? "LOCKED & VERIFIED" : "DRAFT (Unverified)"}
                    </span>
                  </div>
                  <p className="text-[11px] font-sans text-zinc-300 leading-snug">
                    Architected high-throughput event streaming pipeline in Go & Kafka processing 250k events/sec.
                  </p>
                </div>

                {/* Block 2: SKILL_001 & PROJ_001 */}
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-2 rounded-lg bg-zinc-950/80 border border-zinc-800/80 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                        [SKILL_001]
                      </span>
                      <span className="text-[11px] text-zinc-300">PostgreSQL</span>
                    </div>
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  </div>

                  <div className="p-2 rounded-lg bg-zinc-950/80 border border-zinc-800/80 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        [PROJ_001]
                      </span>
                      <span className="text-[11px] text-zinc-300">Raft Consensus</span>
                    </div>
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-zinc-400 font-mono">
            <Lock className="h-3.5 w-3.5 text-blue-400" />
            <span>Immutable primary keys persist across all generation runs</span>
          </div>
        </div>

        {/* STEP 2: Deterministic Filtering (Zero-Cost Pass) */}
        <div className="group relative rounded-2xl border border-zinc-800/80 bg-zinc-950/70 p-6 md:p-7 flex flex-col justify-between space-y-6 glass-card glass-card-hover overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-amber-500/5 rounded-full blur-2xl pointer-events-none" />

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="h-9 w-9 rounded-xl bg-amber-950/60 border border-amber-800/50 flex items-center justify-center text-amber-400">
                  <Sliders className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-amber-400">
                    Step 02 &bull; Deterministic
                  </span>
                  <h3 className="text-lg font-bold text-zinc-100">
                    Deterministic Filtering (Zero-Cost Pass)
                  </h3>
                </div>
              </div>
              <Link href="/preferences" className="text-xs font-mono text-zinc-400 hover:text-amber-400 flex items-center gap-1 transition-colors">
                Configure <ChevronRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            <p className="text-xs md:text-sm text-zinc-400 leading-relaxed">
              Set your non-negotiables. Our deduplication engine and deterministic filters weed out irrelevant roles instantly, saving expensive AI compute for the jobs that actually matter.
            </p>

            {/* Visual Dashboard Mockup */}
            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-3 text-xs">
              <div className="flex items-center justify-between border-b border-zinc-800/60 pb-2">
                <span className="font-mono text-[11px] text-zinc-400">CandidatePreferences Rules</span>
                <span className="font-mono text-[10px] text-emerald-400 bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-800/40">
                  $0.00 LLM Cost &bull; 0ms Latency
                </span>
              </div>

              {/* Toggles */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between p-2 rounded-lg bg-zinc-950/80 border border-zinc-800/80">
                  <div className="space-y-0.5">
                    <div className="font-semibold text-zinc-200 text-xs">Strict Remote-Only</div>
                    <div className="text-[10px] text-zinc-400">Exclude all hybrid / on-site postings</div>
                  </div>
                  <Switch checked={strictRemote} onCheckedChange={setStrictRemote} />
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg bg-zinc-950/80 border border-zinc-800/80">
                  <div className="space-y-0.5">
                    <div className="font-semibold text-zinc-200 text-xs">Location Match (EU / Germany)</div>
                    <div className="text-[10px] text-zinc-400">Word-boundary geographic boundary check</div>
                  </div>
                  <Switch checked={locationMatch} onCheckedChange={setLocationMatch} />
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg bg-zinc-950/80 border border-zinc-800/80">
                  <div className="space-y-0.5">
                    <div className="font-semibold text-zinc-200 text-xs">Keyword Exclusions</div>
                    <div className="text-[10px] text-zinc-400">Regex discard (e.g. &quot;Wordpress&quot;, &quot;unpaid&quot;)</div>
                  </div>
                  <Switch checked={keywordExclusions} onCheckedChange={setKeywordExclusions} />
                </div>
              </div>

              {/* Live Metric Counter */}
              <div className="p-2 rounded-lg bg-zinc-950/90 border border-amber-800/40 flex items-center justify-between font-mono text-[11px]">
                <span className="text-zinc-400">{totalRawJobs} Ingested Postings</span>
                <div className="flex items-center gap-1.5 text-amber-400 font-bold">
                  <ArrowRight className="h-3 w-3" />
                  <span>{filteredJobsCount} High-Precision Jobs</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-zinc-400 font-mono">
            <Check className="h-3.5 w-3.5 text-amber-400" />
            <span>Over 98% of compute budget saved for deep matching</span>
          </div>
        </div>

        {/* STEP 3: AI Gateway & Deep Compatibility */}
        <div className="group relative rounded-2xl border border-zinc-800/80 bg-zinc-950/70 p-6 md:p-7 flex flex-col justify-between space-y-6 glass-card glass-card-hover overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-purple-500/5 rounded-full blur-2xl pointer-events-none" />

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="h-9 w-9 rounded-xl bg-purple-950/60 border border-purple-800/50 flex items-center justify-center text-purple-400">
                  <Cpu className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-purple-400">
                    Step 03 &bull; AI Gateway
                  </span>
                  <h3 className="text-lg font-bold text-zinc-100">
                    AI Gateway & Deep Compatibility
                  </h3>
                </div>
              </div>
              <span className="text-xs font-mono text-purple-400 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800/50">
                Stage 1 &rarr; Stage 2
              </span>
            </div>

            <p className="text-xs md:text-sm text-zinc-400 leading-relaxed">
              Our AI evaluates the surviving jobs against your Canonical Profile, scoring technical alignment and surfacing explainable reasoning for every high-confidence match.
            </p>

            {/* Visual Pipeline & Score Mockup */}
            <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-3 font-mono text-xs">
              {/* Vertical Pipeline Visual */}
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setActiveStage("prescreen")}
                  className={`p-2 rounded-lg border text-left transition-all ${
                    activeStage === "prescreen"
                      ? "bg-purple-950/40 border-purple-600/60 text-purple-200 shadow-sm"
                      : "bg-zinc-950/80 border-zinc-800 text-zinc-400"
                  }`}
                >
                  <div className="text-[10px] font-bold">1. AI Pre-Screen</div>
                  <div className="text-[9px] text-zinc-400 font-sans">High-Recall Embedding Filter</div>
                </button>

                <button
                  onClick={() => setActiveStage("deep")}
                  className={`p-2 rounded-lg border text-left transition-all ${
                    activeStage === "deep"
                      ? "bg-purple-950/40 border-purple-600/60 text-purple-200 shadow-sm"
                      : "bg-zinc-950/80 border-zinc-800 text-zinc-400"
                  }`}
                >
                  <div className="text-[10px] font-bold">2. Deep Assessment</div>
                  <div className="text-[9px] text-zinc-400 font-sans">Multi-dimensional Evaluation</div>
                </button>
              </div>

              {/* Match JSON output glassmorphic card */}
              <div className="p-3.5 rounded-lg bg-zinc-950/90 border border-purple-800/40 space-y-2.5">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-[11px] font-bold text-zinc-200">Senior AI Systems Engineer</span>
                    <span className="text-[10px] text-zinc-400 block">Nexus Intelligence &bull; Munich</span>
                  </div>
                  <div className="px-2.5 py-1 rounded-lg bg-gradient-to-br from-emerald-500/20 to-blue-500/20 border border-emerald-500/40 text-emerald-400 font-bold text-sm">
                    94% Match
                  </div>
                </div>

                <div className="space-y-1 text-[11px] font-sans text-zinc-300">
                  <div className="flex justify-between text-[10px] font-mono text-zinc-400">
                    <span>Backend Architecture: 96%</span>
                    <span>Distributed AI: 92%</span>
                  </div>
                  <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-emerald-400 h-full w-[94%]" />
                  </div>
                </div>

                <div className="p-2 rounded bg-zinc-900/80 border border-zinc-800/60 text-[10px] text-zinc-300 font-sans leading-relaxed">
                  <span className="font-mono text-purple-400 font-bold">Reasoning: </span>
                  Candidate profile has verified mastery in Go, distributed event-driven pipelines ([EXP_001]), and consensus protocols ([PROJ_001]).
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-zinc-400 font-mono">
            <Sparkles className="h-3.5 w-3.5 text-purple-400" />
            <span>Structured JSON responses with guaranteed deterministic schema</span>
          </div>
        </div>

        {/* STEP 4: Static Document Generation (Zero Hallucination) */}
        <div className="group relative rounded-2xl border border-zinc-800/80 bg-zinc-950/70 p-6 md:p-7 flex flex-col justify-between space-y-6 glass-card glass-card-hover overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-emerald-500/5 rounded-full blur-2xl pointer-events-none" />

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="h-9 w-9 rounded-xl bg-emerald-950/60 border border-emerald-800/50 flex items-center justify-center text-emerald-400">
                  <FileCheck2 className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-emerald-400">
                    Step 04 &bull; Generation
                  </span>
                  <h3 className="text-lg font-bold text-zinc-100">
                    Static Document Generation (Zero Hallucination)
                  </h3>
                </div>
              </div>
              <div className="flex gap-1 font-mono text-[10px]">
                <button
                  onClick={() => setDocFormat("pdf")}
                  className={`px-2 py-0.5 rounded border transition-colors ${
                    docFormat === "pdf" ? "bg-emerald-950 text-emerald-300 border-emerald-700" : "bg-zinc-900 text-zinc-400 border-zinc-800"
                  }`}
                >
                  .PDF
                </button>
                <button
                  onClick={() => setDocFormat("docx")}
                  className={`px-2 py-0.5 rounded border transition-colors ${
                    docFormat === "docx" ? "bg-emerald-950 text-emerald-300 border-emerald-700" : "bg-zinc-900 text-zinc-400 border-zinc-800"
                  }`}
                >
                  .DOCX
                </button>
              </div>
            </div>

            <p className="text-xs md:text-sm text-zinc-400 leading-relaxed">
              For high matches, the LLM selects the optimal evidence IDs. Our static renderer injects the verified text into custom templates. No generative hallucination. Just verifiable facts.
            </p>

            {/* Split Screen Visual Component */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 font-mono text-xs">
              
              {/* Left: Validation Gate Code */}
              <div className="p-3 rounded-lg bg-zinc-950 border border-emerald-900/50 space-y-2 flex flex-col justify-between">
                <div className="flex items-center justify-between border-b border-zinc-800 pb-1 text-[10px] text-zinc-400">
                  <span>VALIDATION GATE</span>
                  <span className="text-emerald-400 font-bold">100% PASS</span>
                </div>

                <div className="text-[11px] text-zinc-300 leading-tight space-y-1">
                  <div className="text-zinc-500"># Set inclusion proof</div>
                  <div className="p-1.5 rounded bg-zinc-900/90 text-emerald-300 font-bold border border-zinc-800 text-[10px]">
                    assert selected_ids &sube; allowed_ids
                  </div>
                  <div className="text-[10px] text-zinc-400 pt-1 space-y-1">
                    <div className="flex items-center gap-1 text-emerald-400">
                      <Check className="h-3 w-3" /> EXP_001 &in; Verified Bank
                    </div>
                    <div className="flex items-center gap-1 text-emerald-400">
                      <Check className="h-3 w-3" /> SKILL_001 &in; Verified Bank
                    </div>
                  </div>
                </div>

                <div className="text-[9px] text-zinc-400 font-mono">
                  Zero LLM Text Generation
                </div>
              </div>

              {/* Right: Rendered Document Preview */}
              <div className="p-3 rounded-lg bg-zinc-900/90 border border-zinc-800 space-y-2 flex flex-col justify-between">
                <div className="flex items-center justify-between border-b border-zinc-800 pb-1 text-[10px] text-zinc-400">
                  <span>TEMPLATE RENDER</span>
                  <span className="text-blue-400 font-mono">{docFormat.toUpperCase()}</span>
                </div>

                <div className="p-2 rounded bg-zinc-950/90 border border-zinc-800/80 text-[10px] font-sans text-zinc-300 space-y-1.5 shadow-inner">
                  <div className="font-bold text-zinc-200 border-b border-zinc-800 pb-0.5 text-[11px]">
                    Tailored Application Asset
                  </div>
                  <p className="text-zinc-400 text-[10px] leading-snug">
                    <span className="text-blue-400 font-mono text-[9px] font-bold mr-1">[EXP_001]</span>
                    Architected event-driven streaming pipeline in Go & Kafka...
                  </p>
                  <p className="text-zinc-400 text-[10px] leading-snug">
                    <span className="text-purple-400 font-mono text-[9px] font-bold mr-1">[PROJ_001]</span>
                    Engineered distributed Raft consensus engine with zero loss...
                  </p>
                </div>

                <div className="flex items-center gap-1 text-[9px] text-emerald-400 font-mono">
                  <ShieldCheck className="h-3 w-3" /> Cryptographically Bound
                </div>
              </div>

            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-zinc-400 font-mono">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>Mathematical guarantee: 0 fabricated claims or hallucinated dates</span>
          </div>
        </div>

      </div>
    </section>
  );
}
