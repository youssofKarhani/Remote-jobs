"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, CheckCircle2, Briefcase, Wrench, FolderGit2, Cpu } from "lucide-react";
import { vcopy } from "@/lib/verification-copy";

export function CoreConceptAnimation() {
  // Loop cycle states: 0 = Docs slide in, 1 = Processing in node, 2 = Uniform blocks emerge, 3 = Rest / loop reset
  const [cycleStage, setCycleStage] = useState<number>(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCycleStage((prev) => (prev + 1) % 4);
    }, 2800);

    return () => clearInterval(timer);
  }, []);

  const documents = [
    { label: "resume_v1.pdf", format: "PDF", color: "text-rose-400", border: "border-rose-500/20" },
    { label: "senior_dev.docx", format: "DOCX", color: "text-blue-400", border: "border-blue-500/20" },
    { label: "experience.txt", format: "TXT", color: "text-amber-400", border: "border-amber-500/20" },
  ];

  const uniformBlocks = [
    { label: "Experience", count: vcopy("visual.rolesCount"), icon: Briefcase, tag: vcopy("visual.rolesTag") },
    { label: "Skills", count: "18 Canonical Tags", icon: Wrench, tag: vcopy("visual.skillsTag") },
    { label: "Projects", count: vcopy("visual.buildsCount"), icon: FolderGit2, tag: vcopy("visual.buildsTag") },
  ];

  return (
    <div className="relative w-full max-w-5xl mx-auto my-12 md:my-20 px-4">
      {/* Outer ambient blur */}
      <div className="absolute inset-0 -z-10 flex items-center justify-center">
        <div className="w-[600px] h-[320px] bg-violet-600/10 rounded-full blur-[110px] pointer-events-none" />
      </div>

      {/* Main minimal dark canvas */}
      <div className="relative rounded-2xl border border-zinc-800 bg-zinc-950/80 p-6 sm:p-10 md:p-12 shadow-2xl backdrop-blur-xl overflow-hidden">
        
        {/* Subtle grid background */}
        <div className="absolute inset-0 bg-grid-pattern opacity-25 pointer-events-none" />

        {/* Top Header Badge */}
        <div className="relative z-10 flex items-center justify-between pb-8 mb-6 border-b border-zinc-800/80">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
            <span className="text-xs font-mono uppercase tracking-wider text-zinc-400">
              Canonical Ingestion Gateway
            </span>
          </div>
          <div className="text-[11px] font-mono text-zinc-400 bg-zinc-900 px-2.5 py-1 rounded-md border border-zinc-800">
            Phase: {cycleStage === 0 ? "Multi-Format Ingestion" : cycleStage === 1 ? "Deterministic Deduplication" : "Canonical Synthesis"}
          </div>
        </div>

        {/* Interactive 3-Stage Stage */}
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-11 gap-6 items-center min-h-[220px]">
          
          {/* Left Stage: 3 Raw Documents */}
          <div className="md:col-span-4 flex flex-col gap-3">
            <div className="text-xs font-medium text-zinc-400 mb-1 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
              Raw Input Documents
            </div>
            
            <div className="space-y-2.5">
              {documents.map((doc, idx) => (
                <motion.div
                  key={doc.label}
                  initial={{ opacity: 0, x: -30 }}
                  animate={
                    cycleStage === 0 || cycleStage === 3
                      ? { opacity: 1, x: 0, scale: 1 }
                      : cycleStage === 1
                      ? { opacity: 0.15, x: 40, scale: 0.85 }
                      : { opacity: 0.05, x: 50, scale: 0.8 }
                  }
                  transition={{ duration: 0.6, delay: idx * 0.12 }}
                  className={`flex items-center justify-between p-3 rounded-xl border ${doc.border} bg-zinc-900/80 backdrop-blur-sm`}
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-zinc-800/80 text-zinc-300">
                      <FileText className="w-4 h-4 text-zinc-400" />
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-mono text-zinc-200">{doc.label}</span>
                      <span className="text-[10px] text-zinc-400">Unstructured resume stream</span>
                    </div>
                  </div>
                  <span className={`text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700/60 ${doc.color}`}>
                    {doc.format}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Central Stage: Softly Glowing Node */}
          <div className="md:col-span-3 flex flex-col items-center justify-center relative py-4 md:py-0">
            <div className="relative flex items-center justify-center">
              
              {/* Outer soft glowing rings */}
              <motion.div
                animate={{
                  scale: cycleStage === 1 ? [1, 1.25, 1.1] : [1, 1.05, 1],
                  opacity: cycleStage === 1 ? 0.9 : 0.35,
                }}
                transition={{ duration: 1.8, repeat: Infinity }}
                className="absolute w-28 h-28 rounded-full bg-violet-600/25 blur-xl pointer-events-none"
              />

              {/* Central Engine Node */}
              <motion.div
                animate={{
                  borderColor: cycleStage === 1 ? "rgba(167, 139, 250, 0.8)" : "rgba(63, 63, 70, 0.8)",
                  boxShadow: cycleStage === 1 ? "0 0 35px rgba(139, 92, 246, 0.45)" : "0 0 15px rgba(0, 0, 0, 0.5)",
                  scale: cycleStage === 1 ? 1.08 : 1,
                }}
                transition={{ duration: 0.5 }}
                className="relative z-10 w-20 h-20 rounded-2xl bg-zinc-900 border border-zinc-700/80 flex flex-col items-center justify-center p-3 text-center"
              >
                <Cpu className={`w-6 h-6 transition-colors duration-500 ${cycleStage === 1 ? "text-violet-400 animate-spin" : "text-zinc-400"}`} style={{ animationDuration: '8s' }} />
                <span className="text-[9px] font-mono mt-1 text-zinc-400">
                  {cycleStage === 1 ? "Deduplicating" : "Engine Core"}
                </span>
              </motion.div>
            </div>

            {/* Connecting Flow Indicator */}
            <div className="mt-3 flex items-center gap-1.5 text-[11px] font-mono text-zinc-400">
              <span className={`w-1.5 h-1.5 rounded-full ${cycleStage === 1 ? "bg-violet-400 animate-ping" : "bg-zinc-600"}`} />
              <span>Immutable Extraction</span>
            </div>
          </div>

          {/* Right Stage: 3 Clean Uniform Verified Blocks */}
          <div className="md:col-span-4 flex flex-col gap-3">
            <div className="text-xs font-medium text-zinc-400 mb-1 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                {vcopy("visual.bankTitle")}
              </div>
              <span className="text-[10px] font-mono text-emerald-400">100% Fact-Checked</span>
            </div>

            <div className="space-y-2.5">
              {uniformBlocks.map((block, idx) => {
                const Icon = block.icon;
                return (
                  <motion.div
                    key={block.label}
                    initial={{ opacity: 0, x: 20 }}
                    animate={
                      cycleStage >= 2
                        ? { opacity: 1, x: 0, scale: 1 }
                        : { opacity: 0.2, x: -15, scale: 0.95 }
                    }
                    transition={{ duration: 0.5, delay: idx * 0.1 }}
                    className="flex items-center justify-between p-3 rounded-xl border border-zinc-800 bg-zinc-900/90 hover:border-violet-500/40 transition-colors shadow-sm"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-zinc-800 text-violet-400 border border-zinc-700/60">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs font-semibold text-zinc-100">{block.label}</span>
                        <span className="text-[10px] text-zinc-400">{block.count}</span>
                      </div>
                    </div>
                    <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      {block.tag}
                    </span>
                  </motion.div>
                );
              })}
            </div>
          </div>

        </div>

        {/* Bottom Caption Banner */}
        <div className="mt-8 pt-6 border-t border-zinc-800/80 text-center">
          <p className="text-xs sm:text-sm text-zinc-300 font-sans tracking-wide">
            {vcopy("visual.bankQuote")}
          </p>
        </div>

      </div>
    </div>
  );
}
