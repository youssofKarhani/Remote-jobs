"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Puzzle, 
  Filter, 
  Sparkles, 
  FileCheck2, 
  Check, 
  Sliders, 
  Layers, 
  ArrowDown, 
  CheckCircle2, 
  ShieldCheck, 
  ChevronRight,
  Search
} from "lucide-react";

interface StepData {
  id: number;
  label: string;
  copy: string;
  badge: string;
}

const STEPS: StepData[] = [
  {
    id: 1,
    label: "Extract",
    copy: "Your base CV is deconstructed into verified, reusable data points.",
    badge: "Step 01",
  },
  {
    id: 2,
    label: "Filter",
    copy: "Set your rules. We instantly filter out roles that don't match your non-negotiables.",
    badge: "Step 02",
  },
  {
    id: 3,
    label: "Match",
    copy: "Our AI scores the surviving jobs against your profile to find high-confidence fits.",
    badge: "Step 03",
  },
  {
    id: 4,
    label: "Generate",
    copy: "We select the perfect verified blocks to generate a tailored CV and cover letter with zero hallucinations.",
    badge: "Step 04",
  },
];

export function PipelineTimeline() {
  const [activeStep, setActiveStep] = useState<number>(1);
  const stepRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const handleScroll = () => {
      stepRefs.current.forEach((ref, index) => {
        if (!ref) return;
        const rect = ref.getBoundingClientRect();
        // If element is in middle of viewport
        if (rect.top <= window.innerHeight * 0.55 && rect.bottom >= window.innerHeight * 0.2) {
          setActiveStep(index + 1);
        }
      });
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <section className="relative w-full max-w-5xl mx-auto my-16 md:my-28 px-4">
      {/* Section Header */}
      <div className="text-center space-y-3 max-w-xl mx-auto mb-16 md:mb-24">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-sans font-medium bg-zinc-900 border border-zinc-800 text-zinc-400">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" />
          The Automated Pipeline
        </div>
        <h2 className="text-3xl md:text-4xl font-light tracking-tight text-zinc-100">
          Four steps. <span className="font-medium text-white">Zero hallucinations.</span>
        </h2>
        <p className="text-sm text-zinc-400 font-light leading-relaxed">
          Scroll through the deterministic pipeline powering verified job applications.
        </p>
      </div>

      {/* Central Timeline Container */}
      <div className="relative">
        
        {/* Central Vertical Line */}
        <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-px bg-zinc-800 -translate-x-1/2" />
        
        {/* Glowing Progress Line */}
        <div 
          className="absolute left-6 md:left-1/2 top-0 w-[2px] bg-gradient-to-b from-indigo-500 via-violet-500 to-indigo-400 -translate-x-1/2 transition-all duration-700 ease-out"
          style={{
            height: `${((activeStep - 1) / (STEPS.length - 1)) * 100}%`,
          }}
        />

        {/* Steps */}
        <div className="space-y-16 md:space-y-24">
          {STEPS.map((step, index) => {
            const isLeft = index % 2 === 0;
            const isActive = activeStep === step.id;
            const isPastOrActive = activeStep >= step.id;

            return (
              <div
                key={step.id}
                ref={(el) => { stepRefs.current[index] = el; }}
                onClick={() => setActiveStep(step.id)}
                className="relative grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 items-center cursor-pointer group"
              >
                {/* Center Node Indicator */}
                <div 
                  className={`absolute left-6 md:left-1/2 top-0 md:top-1/2 -translate-x-1/2 -translate-y-1/2 z-20 flex items-center justify-center w-9 h-9 rounded-full border-2 transition-all duration-500 ${
                    isActive
                      ? "bg-zinc-950 border-indigo-400 shadow-[0_0_20px_rgba(99,102,241,0.6)] scale-110"
                      : isPastOrActive
                      ? "bg-zinc-900 border-indigo-500/60 text-zinc-300"
                      : "bg-zinc-950 border-zinc-800 text-zinc-600"
                  }`}
                >
                  <span className={`text-xs font-mono font-medium transition-colors ${isActive ? "text-indigo-300" : isPastOrActive ? "text-zinc-300" : "text-zinc-600"}`}>
                    0{step.id}
                  </span>
                </div>

                {/* Left Column (Copy or Visual based on index) */}
                <div className={`pl-14 md:pl-0 ${isLeft ? "md:text-right md:pr-12 order-1" : "md:order-2 md:pl-12 order-1"}`}>
                  <div className={`transition-all duration-500 ${isActive ? "opacity-100 translate-y-0" : "opacity-70 group-hover:opacity-90"}`}>
                    <span className={`inline-block text-[11px] font-mono uppercase tracking-widest px-2.5 py-0.5 rounded-full border mb-2 transition-colors ${
                      isActive 
                        ? "bg-indigo-950/50 text-indigo-300 border-indigo-500/40" 
                        : "bg-zinc-900/60 text-zinc-400 border-zinc-800"
                    }`}>
                      {step.badge}
                    </span>

                    <h3 className="text-xl md:text-2xl font-light text-zinc-100 mb-2 tracking-tight">
                      {step.label}
                    </h3>

                    <p className="text-sm md:text-base text-zinc-400 font-light leading-relaxed max-w-md ml-auto mr-0 inline-block">
                      {step.copy}
                    </p>
                  </div>
                </div>

                {/* Right Column: Micro-Animation Visual */}
                <div className={`pl-14 md:pl-0 ${isLeft ? "md:order-2 md:pl-12 order-2" : "md:order-1 md:text-right md:pr-12 order-2"}`}>
                  <div className={`p-5 rounded-2xl border transition-all duration-500 ${
                    isActive 
                      ? "bg-zinc-900/80 border-indigo-500/40 shadow-xl shadow-indigo-950/30 scale-[1.02]" 
                      : "bg-zinc-950/60 border-zinc-800/80 hover:border-zinc-700"
                  }`}>
                    {step.id === 1 && <ExtractVisual isActive={isActive} />}
                    {step.id === 2 && <FilterVisual isActive={isActive} />}
                    {step.id === 3 && <MatchVisual isActive={isActive} />}
                    {step.id === 4 && <GenerateVisual isActive={isActive} />}
                  </div>
                </div>

              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}

// -------------------------------------------------------------
// STEP 1 MICRO-ANIMATION: Extract (Puzzle Piece Popping Out)
// -------------------------------------------------------------
function ExtractVisual({ isActive }: { isActive: boolean }) {
  return (
    <div className="relative h-44 flex items-center justify-center overflow-hidden">
      {/* Background document layout */}
      <div className="relative w-40 h-32 rounded-xl border border-zinc-800 bg-zinc-950/90 p-3 shadow-md flex flex-col justify-between">
        <div className="space-y-1.5">
          <div className="w-16 h-2 bg-zinc-700 rounded-full" />
          <div className="w-28 h-1 bg-zinc-800 rounded-full" />
          <div className="w-20 h-1 bg-zinc-800 rounded-full" />
        </div>

        {/* Puzzle extraction hole in the document */}
        <div className="my-1 p-2 rounded border border-dashed border-zinc-800 bg-zinc-900/40 flex items-center justify-center">
          <span className="text-[9px] font-mono text-zinc-400">extracted_slot</span>
        </div>

        <div className="space-y-1">
          <div className="w-24 h-1 bg-zinc-800 rounded-full" />
          <div className="w-16 h-1 bg-zinc-800 rounded-full" />
        </div>
      </div>

      {/* Floating Popping Puzzle Piece */}
      <div className={`absolute right-4 md:right-8 top-1/2 -translate-y-1/2 p-3 rounded-xl border bg-zinc-900/95 shadow-xl transition-all duration-700 flex items-center gap-2.5 ${
        isActive 
          ? "border-indigo-400/80 shadow-indigo-500/20 translate-x-0 scale-105" 
          : "border-zinc-700 translate-x-2 opacity-80"
      }`}>
        <div className="w-8 h-8 rounded-lg bg-indigo-950/80 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
          <Puzzle className={`w-4 h-4 transition-transform duration-500 ${isActive ? "rotate-12 scale-110" : ""}`} />
        </div>
        <div className="text-left space-y-0.5">
          <div className="text-[11px] font-mono font-bold text-indigo-300">EXP_001</div>
          <div className="text-[9px] text-zinc-400 font-sans">Verified Fact</div>
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// STEP 2 MICRO-ANIMATION: Filter (Minimalist Funnel with Dots)
// -------------------------------------------------------------
function FilterVisual({ isActive }: { isActive: boolean }) {
  return (
    <div className="relative h-44 flex flex-col items-center justify-center overflow-hidden">
      {/* Top Incoming abstract job dots */}
      <div className="flex items-center gap-2 pb-2">
        <div className="w-2 h-2 rounded-full bg-zinc-600 animate-pulse opacity-40" />
        <div className="w-2 h-2 rounded-full bg-zinc-500 animate-pulse opacity-40" />
        <div className="w-2.5 h-2.5 rounded-full bg-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.8)]" />
        <div className="w-2 h-2 rounded-full bg-zinc-600 animate-pulse opacity-40" />
        <div className="w-2.5 h-2.5 rounded-full bg-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.8)]" />
      </div>

      {/* Minimalist Funnel SVG Graphic */}
      <div className="relative w-28 h-16 flex items-center justify-center">
        <svg viewBox="0 0 100 60" className="w-full h-full text-zinc-700 overflow-visible">
          <polygon 
            points="10,5 90,5 60,40 60,55 40,55 40,40" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            className={`transition-colors duration-500 ${isActive ? "text-indigo-400" : "text-zinc-700"}`}
          />
          {/* Internal filter beam */}
          <line 
            x1="25" y1="20" x2="75" y2="20" 
            stroke={isActive ? "rgba(99, 102, 241, 0.6)" : "rgba(63, 63, 70, 0.6)"} 
            strokeDasharray="3 3"
            strokeWidth="1.5"
          />
        </svg>
      </div>

      {/* Filtered High-Confidence Dot Output */}
      <div className="pt-2 flex flex-col items-center space-y-1">
        <div className={`w-3 h-3 rounded-full bg-indigo-400 shadow-[0_0_12px_rgba(99,102,241,0.9)] transition-transform duration-500 ${
          isActive ? "scale-125" : "scale-100"
        }`} />
        <span className="text-[10px] font-mono text-indigo-300">
          Strict Remote &bull; Matched
        </span>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// STEP 3 MICRO-ANIMATION: Match (Two Interlocking Venn Circles)
// -------------------------------------------------------------
function MatchVisual({ isActive }: { isActive: boolean }) {
  return (
    <div className="relative h-44 flex items-center justify-center">
      {/* Venn Diagram Circles */}
      <div className="relative w-44 h-32 flex items-center justify-center">
        
        {/* Left Circle: Candidate Evidence Bank */}
        <div className={`absolute left-2 w-24 h-24 rounded-full border-2 transition-all duration-500 flex items-center justify-start pl-3 ${
          isActive 
            ? "border-indigo-500/80 bg-indigo-500/10 shadow-[0_0_25px_rgba(99,102,241,0.2)]" 
            : "border-zinc-700 bg-zinc-900/40"
        }`}>
          <span className="text-[9px] font-mono text-zinc-400">Profile</span>
        </div>

        {/* Right Circle: Job Requirements */}
        <div className={`absolute right-2 w-24 h-24 rounded-full border-2 transition-all duration-500 flex items-center justify-end pr-3 ${
          isActive 
            ? "border-violet-500/80 bg-violet-500/10 shadow-[0_0_25px_rgba(139,92,246,0.2)]" 
            : "border-zinc-700 bg-zinc-900/40"
        }`}>
          <span className="text-[9px] font-mono text-zinc-400">Role</span>
        </div>

        {/* Center Intersecting Glow Zone */}
        <div className={`relative z-10 px-2.5 py-1 rounded-full border transition-all duration-500 flex items-center gap-1 ${
          isActive 
            ? "bg-zinc-900 border-emerald-400/80 text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.3)] scale-110" 
            : "bg-zinc-950 border-zinc-800 text-zinc-500 scale-95"
        }`}>
          <Sparkles className="w-3 h-3 text-emerald-400" />
          <span className="text-[11px] font-mono font-bold">96% Fit</span>
        </div>

      </div>
    </div>
  );
}

// -------------------------------------------------------------
// STEP 4 MICRO-ANIMATION: Generate (Reassembled Polished Document)
// -------------------------------------------------------------
function GenerateVisual({ isActive }: { isActive: boolean }) {
  return (
    <div className="relative h-44 flex items-center justify-center">
      {/* Reassembled Document Card */}
      <div className={`relative w-44 aspect-[1/1.25] rounded-xl border p-3 shadow-xl transition-all duration-500 flex flex-col justify-between ${
        isActive 
          ? "border-indigo-400/60 bg-zinc-900/90 shadow-[0_0_25px_rgba(99,102,241,0.15)] scale-105" 
          : "border-zinc-800 bg-zinc-950/70"
      }`}>
        {/* Document Header with Verification Badge */}
        <div className="flex items-center justify-between border-b border-zinc-800/70 pb-2">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-[10px] font-mono text-zinc-300 font-medium">Tailored CV</span>
          </div>
          <FileCheck2 className="w-3.5 h-3.5 text-indigo-400" />
        </div>

        {/* Reassembled Puzzle Blocks */}
        <div className="space-y-1.5 py-1">
          <div className="p-1.5 rounded bg-zinc-800/60 border border-zinc-700/50 flex items-center justify-between">
            <span className="text-[9px] font-mono text-indigo-300">[EXP_001] Verified</span>
            <Check className="w-2.5 h-2.5 text-emerald-400" />
          </div>
          <div className="p-1.5 rounded bg-zinc-800/60 border border-zinc-700/50 flex items-center justify-between">
            <span className="text-[9px] font-mono text-purple-300">[SKILL_001] Verified</span>
            <Check className="w-2.5 h-2.5 text-emerald-400" />
          </div>
        </div>

        {/* Document Footer Guarantee */}
        <div className="pt-1.5 border-t border-zinc-800/70 flex items-center justify-between text-[8px] font-mono text-zinc-400">
          <span>0% Hallucination</span>
          <span className="text-emerald-400">Ready</span>
        </div>
      </div>
    </div>
  );
}
