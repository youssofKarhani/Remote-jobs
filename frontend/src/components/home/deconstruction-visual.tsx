"use client";

import React, { useState } from "react";
import { FileText, CheckCircle2, Sparkles, Briefcase, Wrench, FolderGit2, GraduationCap } from "lucide-react";

export function DeconstructionVisual() {
  const [activeHover, setActiveHover] = useState<string | null>(null);

  const blocks = [
    {
      id: "exp",
      title: "Experience",
      icon: Briefcase,
      count: "3 Roles • 8 Bullets",
      border: "border-indigo-500/30",
      tag: "Verified",
      delayClass: "animate-float-1",
    },
    {
      id: "skills",
      title: "Skills",
      icon: Wrench,
      count: "14 Canonical Skills",
      border: "border-violet-500/30",
      tag: "Verified",
      delayClass: "animate-float-2",
    },
    {
      id: "projects",
      title: "Projects",
      icon: FolderGit2,
      count: "4 Verified Builds",
      border: "border-blue-500/30",
      tag: "Verified",
      delayClass: "animate-float-3",
    },
    {
      id: "education",
      title: "Education",
      icon: GraduationCap,
      count: "B.S. & Certifications",
      border: "border-zinc-700/50",
      tag: "Verified",
      delayClass: "animate-float-1",
    },
  ];

  return (
    <section className="relative w-full max-w-5xl mx-auto my-12 md:my-20">
      {/* Background subtle glow */}
      <div className="absolute inset-0 -z-10 flex items-center justify-center">
        <div className="w-[500px] h-[300px] bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />
      </div>

      {/* Main Canvas Container */}
      <div className="relative rounded-3xl border border-zinc-800/80 bg-zinc-950/70 p-6 sm:p-10 md:p-12 shadow-2xl backdrop-blur-xl overflow-hidden">
        
        {/* Visual Stage: 3-column deconstruction */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-6 items-center">
          
          {/* Left Side: Static Resume Document */}
          <div className="md:col-span-4 flex flex-col items-center md:items-start space-y-3">
            <div className="relative w-full max-w-[240px] aspect-[1/1.3] rounded-2xl border border-zinc-800 bg-zinc-900/90 p-4 shadow-xl overflow-hidden group">
              
              {/* Document Header Minimalist Silhouette */}
              <div className="flex items-center gap-2.5 pb-3 border-b border-zinc-800/70">
                <div className="w-7 h-7 rounded-lg bg-zinc-800 flex items-center justify-center text-zinc-400">
                  <FileText className="w-3.5 h-3.5" />
                </div>
                <div className="space-y-1">
                  <div className="w-20 h-2 bg-zinc-300 rounded-full" />
                  <div className="w-14 h-1.5 bg-zinc-600 rounded-full" />
                </div>
              </div>

              {/* Document Content Skeleton Lines */}
              <div className="pt-3 space-y-2.5">
                <div className="space-y-1">
                  <div className="w-12 h-1.5 bg-indigo-400/80 rounded-full" />
                  <div className="w-full h-1.5 bg-zinc-700/60 rounded-full" />
                  <div className="w-5/6 h-1.5 bg-zinc-700/60 rounded-full" />
                </div>

                <div className="space-y-1 pt-1">
                  <div className="w-10 h-1.5 bg-indigo-400/80 rounded-full" />
                  <div className="w-full h-1.5 bg-zinc-700/60 rounded-full" />
                  <div className="w-4/5 h-1.5 bg-zinc-700/60 rounded-full" />
                  <div className="w-3/4 h-1.5 bg-zinc-700/60 rounded-full" />
                </div>

                <div className="space-y-1 pt-1">
                  <div className="w-14 h-1.5 bg-indigo-400/80 rounded-full" />
                  <div className="w-full h-1.5 bg-zinc-700/60 rounded-full" />
                  <div className="w-2/3 h-1.5 bg-zinc-700/60 rounded-full" />
                </div>
              </div>

              {/* Looping Laser AI Sweep Line */}
              <div className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-indigo-400 to-transparent shadow-[0_0_12px_2px_rgba(99,102,241,0.8)] animate-laser-sweep pointer-events-none" />

              {/* Format pill */}
              <div className="absolute bottom-2.5 right-2.5 text-[9px] font-sans tracking-wide text-zinc-400 px-1.5 py-0.5 rounded bg-zinc-800/80 border border-zinc-700/50">
                PDF / Word
              </div>
            </div>

            <span className="text-xs text-zinc-400 font-sans tracking-tight">
              Standard Static Resume
            </span>
          </div>

          {/* Center: Glowing AI Processing Bridge */}
          <div className="md:col-span-3 flex flex-col items-center justify-center relative py-2 md:py-0">
            {/* Horizontal / Vertical connecting beam */}
            <div className="relative flex items-center justify-center w-full">
              <div className="hidden md:block w-full h-[1px] bg-gradient-to-r from-zinc-800 via-indigo-500/50 to-zinc-800" />
              
              <div className="relative z-10 flex flex-col items-center gap-1.5 px-4 py-2 rounded-full bg-zinc-900 border border-indigo-500/30 text-indigo-300 text-xs shadow-lg shadow-indigo-950/50">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-spin" style={{ animationDuration: '6s' }} />
                <span className="text-[11px] font-sans font-medium">AI Extraction</span>
              </div>
            </div>
            <span className="text-[10px] text-zinc-400 mt-2 font-sans">
              Instant Deconstruction
            </span>
          </div>

          {/* Right Side: 4 Clean Floating Verifiable Building Blocks */}
          <div className="md:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
            {blocks.map((block) => {
              const Icon = block.icon;
              return (
                <div
                  key={block.id}
                  onMouseEnter={() => setActiveHover(block.id)}
                  onMouseLeave={() => setActiveHover(null)}
                  className={`relative p-3.5 rounded-xl border bg-zinc-900/80 backdrop-blur-md transition-all duration-300 ${block.delayClass} ${
                    activeHover === block.id
                      ? "border-indigo-400/80 bg-zinc-800/90 scale-105 shadow-lg shadow-indigo-500/10"
                      : `${block.border} hover:border-zinc-600`
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="p-1.5 rounded-lg bg-zinc-800/90 text-indigo-300 border border-zinc-700/40">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-sans font-medium bg-emerald-950/40 px-1.5 py-0.5 rounded-full border border-emerald-800/40">
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      {block.tag}
                    </span>
                  </div>

                  <div className="space-y-0.5">
                    <div className="text-xs font-semibold text-zinc-100 tracking-tight">
                      {block.title}
                    </div>
                    <div className="text-[11px] text-zinc-400 font-sans">
                      {block.count}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

        </div>

        {/* Supporting Copy */}
        <div className="mt-8 pt-6 border-t border-zinc-800/60 text-center">
          <p className="text-sm md:text-base text-zinc-300 font-light tracking-wide max-w-2xl mx-auto">
            &ldquo;We turn your static resume into dynamic, verifiable building blocks.&rdquo;
          </p>
        </div>

      </div>
    </section>
  );
}
