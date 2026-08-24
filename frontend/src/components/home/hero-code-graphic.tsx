"use client";

import React, { useState } from "react";
import { Terminal, ArrowRight, Check, Copy, Sparkles, Activity, FileText, Braces, Cpu } from "lucide-react";

export function HeroCodeGraphic() {
  const [copied, setCopied] = useState(false);

  const handleCopyJson = () => {
    const jsonText = JSON.stringify(
      {
        candidate_profile: {
          full_name: "Alex Rivera",
          headline: "Staff Distributed Systems Engineer",
        },
        evidence_bank: {
          experiences: [
            {
              role: "Staff Backend Engineer",
              bullets: [
                { id: "EXP_001", verified: true, text: "Architected event-driven streaming pipeline in Go & Kafka" },
                { id: "EXP_002", verified: true, text: "Engineered zero-downtime distributed consensus layer" }
              ]
            }
          ],
          skills: ["SKILL_001: Go", "SKILL_002: Rust", "SKILL_003: PostgreSQL", "SKILL_004: Kubernetes"]
        }
      },
      null,
      2
    );
    navigator.clipboard.writeText(jsonText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative w-full rounded-2xl border border-zinc-800/80 bg-zinc-950/90 shadow-2xl overflow-hidden glass-card">
      {/* Glow backgrounds */}
      <div className="absolute -top-24 -left-24 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Terminal Title Bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/80 bg-zinc-900/60 backdrop-blur-md">
        <div className="flex items-center space-x-2">
          <div className="h-3 w-3 rounded-full bg-red-500/80 border border-red-600/40" />
          <div className="h-3 w-3 rounded-full bg-amber-500/80 border border-amber-600/40" />
          <div className="h-3 w-3 rounded-full bg-emerald-500/80 border border-emerald-600/40" />
          <span className="text-[11px] font-mono text-zinc-400 ml-2 font-medium flex items-center gap-1.5">
            <Terminal className="h-3.5 w-3.5 text-blue-400" />
            pipeline.fastapi.remotejobs &bull; ingestion_stream
          </span>
        </div>

        <div className="flex items-center space-x-3">
          <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/50">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            POST /api/v1/cv/extract: 200 OK (320ms)
          </span>
          <button
            onClick={handleCopyJson}
            className="text-zinc-400 hover:text-zinc-200 transition-colors text-xs flex items-center gap-1 bg-zinc-800/50 px-2 py-1 rounded border border-zinc-700/50"
            title="Copy structured JSON"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            <span className="text-[11px] font-mono">{copied ? "Copied" : "JSON"}</span>
          </button>
        </div>
      </div>

      {/* 3-Column Code Window Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 divide-y lg:divide-y-0 lg:divide-x divide-zinc-800/80 text-xs font-mono">
        
        {/* Left Column: Raw Text Snippet */}
        <div className="lg:col-span-4 p-4 sm:p-5 bg-zinc-950/50 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-zinc-400 border-b border-zinc-800/60 pb-2">
              <span className="flex items-center gap-1.5 text-[11px] font-semibold text-zinc-300">
                <FileText className="h-3.5 w-3.5 text-zinc-400" />
                Raw Experience (CV Input)
              </span>
              <span className="text-[10px] text-zinc-400 px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">
                UTF-8 .txt / .pdf
              </span>
            </div>

            <div className="text-zinc-300 space-y-2 leading-relaxed text-[11px]">
              <p className="text-zinc-400"># Alex Rivera - Staff Distributed Systems Engineer</p>
              <p className="p-2 rounded bg-zinc-900/60 border border-zinc-800/80 text-zinc-200">
                <span className="text-blue-400">&gt;</span> Architected high-throughput event streaming pipeline processing 250k events/sec with Go & Kafka.
              </p>
              <p className="p-2 rounded bg-zinc-900/60 border border-zinc-800/80 text-zinc-200">
                <span className="text-blue-400">&gt;</span> Engineered zero-downtime distributed consensus layer and high-availability PostgreSQL clusters.
              </p>
              <div className="flex flex-wrap gap-1 pt-1 text-[10px] text-zinc-400">
                <span className="px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">Go</span>
                <span className="px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">Kafka</span>
                <span className="px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">PostgreSQL</span>
              </div>
            </div>
          </div>

          <div className="pt-2 text-[10px] text-zinc-400 flex items-center gap-1.5">
            <Sparkles className="h-3 w-3 text-blue-400 shrink-0" />
            <span>Parsed into discrete immutable facts</span>
          </div>
        </div>

        {/* Middle Column: API Processing Pipeline */}
        <div className="lg:col-span-3 p-4 sm:p-5 bg-zinc-900/20 flex flex-col justify-center items-center space-y-4 text-center">
          <div className="space-y-1">
            <span className="text-[10px] text-zinc-400 uppercase tracking-widest font-semibold block">
              FastAPI Extraction Gateway
            </span>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-950/40 border border-blue-800/40 text-blue-400 text-xs font-semibold">
              <Cpu className="h-3.5 w-3.5" />
              AIService Deconstruction
            </div>
          </div>

          {/* Interactive animated pipeline visual */}
          <div className="w-full space-y-2 py-2">
            <div className="p-2.5 rounded-lg bg-zinc-900/90 border border-zinc-800 text-left space-y-1.5 shadow-sm">
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-zinc-400">Pydantic Validation</span>
                <span className="text-emerald-400 font-bold">PASS</span>
              </div>
              <div className="w-full bg-zinc-800 h-1 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-full w-full animate-pulse" />
              </div>
            </div>

            <div className="flex justify-center text-zinc-400">
              <ArrowRight className="h-4 w-4 rotate-90 lg:rotate-0 text-blue-400 animate-bounce" />
            </div>

            <div className="p-2.5 rounded-lg bg-zinc-900/90 border border-zinc-800 text-left space-y-1.5 shadow-sm">
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-zinc-400">Stable ID Generation</span>
                <span className="text-purple-400 font-bold">EXP_001</span>
              </div>
              <div className="w-full bg-zinc-800 h-1 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-purple-500 to-emerald-500 h-full w-full" />
              </div>
            </div>
          </div>

          <div className="text-[10px] text-zinc-400 font-mono">
            Zero hallucinations &bull; 100% Verifiable
          </div>
        </div>

        {/* Right Column: Structured JSON Output */}
        <div className="lg:col-span-5 p-4 sm:p-5 bg-zinc-950/80 flex flex-col justify-between space-y-3">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-zinc-400 border-b border-zinc-800/60 pb-2">
              <span className="flex items-center gap-1.5 text-[11px] font-semibold text-zinc-300">
                <Braces className="h-3.5 w-3.5 text-purple-400" />
                CandidateProfile & EvidenceBank
              </span>
              <span className="text-[10px] text-emerald-400 font-bold px-1.5 py-0.5 rounded bg-emerald-950/50 border border-emerald-800/40">
                IMMUTABLE JSON
              </span>
            </div>

            {/* Syntax Highlighted JSON display */}
            <div className="text-[11px] leading-relaxed overflow-x-auto text-zinc-300 font-mono max-h-[260px] scrollbar-thin">
              <pre>
                <span className="text-zinc-400">&#123;</span>{"\n"}
                {"  "}<span className="text-blue-400">&quot;candidate_profile&quot;</span>: &#123;{"\n"}
                {"    "}<span className="text-purple-300">&quot;full_name&quot;</span>: <span className="text-emerald-300">&quot;Alex Rivera&quot;</span>,{"\n"}
                {"    "}<span className="text-purple-300">&quot;headline&quot;</span>: <span className="text-emerald-300">&quot;Staff Distributed Systems Engineer&quot;</span>{"\n"}
                {"  "}&#125;,{"\n"}
                {"  "}<span className="text-blue-400">&quot;evidence_bank&quot;</span>: &#123;{"\n"}
                {"    "}<span className="text-purple-300">&quot;experiences&quot;</span>: [&#123;{"\n"}
                {"      "}<span className="text-zinc-400">&quot;bullets&quot;</span>: [&#123;{"\n"}
                {"        "}<span className="text-amber-300">&quot;stable_id&quot;</span>: <span className="text-amber-400 font-bold">&quot;EXP_001&quot;</span>,{"\n"}
                {"        "}<span className="text-zinc-400">&quot;verified&quot;</span>: <span className="text-emerald-400 font-bold">true</span>,{"\n"}
                {"        "}<span className="text-zinc-400">&quot;raw_text&quot;</span>: <span className="text-emerald-300">&quot;Architected streaming pipeline...&quot;</span>{"\n"}
                {"      "}&#125;]{"\n"}
                {"    "}&#125;],{"\n"}
                {"    "}<span className="text-purple-300">&quot;skills&quot;</span>: [&#123; <span className="text-amber-300">&quot;stable_id&quot;</span>: <span className="text-amber-400">&quot;SKILL_001&quot;</span>, <span className="text-zinc-400">&quot;name&quot;</span>: <span className="text-emerald-300">&quot;Go&quot;</span> &#125;]{"\n"}
                {"  "}&#125;{"\n"}
                <span className="text-zinc-400">&#125;</span>
              </pre>
            </div>
          </div>

          <div className="pt-2 border-t border-zinc-800/60 flex items-center justify-between text-[10px] text-zinc-400">
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <Check className="h-3 w-3" /> Ready for Tailored Generation
            </span>
            <span className="font-mono">schema: pydantic_v2</span>
          </div>
        </div>

      </div>
    </div>
  );
}

