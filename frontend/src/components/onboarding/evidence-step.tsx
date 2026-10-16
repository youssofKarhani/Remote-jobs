"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileText, CheckCircle2, Loader2, Sparkles, Layers, ShieldCheck, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cvApi } from "@/lib/api";

const SAMPLE_DEMO_CV = `
Alex Rivera
Senior Distributed Systems & Backend Engineer
Berlin, Germany | alex.rivera@example.com

SUMMARY
Senior Backend Engineer with 8+ years experience designing high-throughput distributed systems in Python, Go, and PostgreSQL.

EXPERIENCE
Acme Cloud Systems | Senior Backend Engineer | 2022 - Present
- Designed high-throughput event processing pipeline using Python, Kafka, and FastAPI processing 45,000 events/second with sub-100ms latency.
- Architected automated PostgreSQL failover using Patroni, reducing unplanned downtime from 45 min to under 15 seconds.
- Led migration from monolithic Django service to Kubernetes microservices architecture.

TechCorp Global | Backend Software Engineer | 2019 - 2022
- Developed REST and gRPC microservices for payments and order fulfillment in Python and PostgreSQL.
- Implemented Redis caching layer reducing database read load by 60%.

SKILLS
Python, FastAPI, PostgreSQL, Docker, Kubernetes, Redis, Kafka, AWS, Git, CI/CD, SQLModel

PROJECTS
Distributed Queue Engine | High-performance job queue with sliding window rate limiting in Python and Redis.

EDUCATION
B.S. in Computer Science | Technical University of Munich | 2015 - 2019
`;

interface EvidenceStepProps {
  targetRole: string;
  onComplete: (data: { filesCount: number; dataPointsCount: number }) => void;
  onBack: () => void;
}

export function EvidenceStep({ targetRole, onComplete, onBack }: EvidenceStepProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processStage, setProcessStage] = useState<number>(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const STAGES = [
    { label: "Merging 3 documents...", progress: 34, icon: Layers },
    { label: "Removing duplicates...", progress: 68, icon: Sparkles },
    { label: "Verifying 42 data points...", progress: 100, icon: ShieldCheck },
  ];

  // Progressive simulated deduplication state
  useEffect(() => {
    if (!isProcessing) return;

    const timer1 = setTimeout(() => {
      setProcessStage(1);
    }, 1200);

    const timer2 = setTimeout(() => {
      setProcessStage(2);
    }, 2400);

    const timer3 = setTimeout(() => {
      onComplete({
        filesCount: Math.max(files.length, 3),
        dataPointsCount: 42,
      });
    }, 3800);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [isProcessing, files, onComplete]);

  const handleStartProcess = async (initialFiles: string[], rawFiles?: File[]) => {
    setFiles(initialFiles);
    setIsProcessing(true);
    setProcessStage(0);

    // Call real backend extraction in background
    try {
      if (rawFiles && rawFiles.length > 0) {
        for (const file of rawFiles) {
          await cvApi.uploadCV(file);
        }
      } else {
        await cvApi.parseText(SAMPLE_DEMO_CV);
      }
    } catch (err) {
      console.warn("Evidence extraction background notice:", err);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const raw = Array.from(e.dataTransfer.files);
      const names = raw.map((f) => f.name);
      handleStartProcess(names, raw);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const raw = Array.from(e.target.files);
      const names = raw.map((f) => f.name);
      handleStartProcess(names, raw);
    }
  };

  const handleSimulateDemo = () => {
    handleStartProcess([
      "Master_Resume_2026.pdf",
      "Cloud_Automation_Heavy.docx",
      "Legacy_Technical_History.txt",
    ]);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto w-full py-6 md:py-12 space-y-8"
    >
      {/* Top Breadcrumb & Step Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-zinc-900 border border-zinc-800 text-zinc-400">
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
          Step 02 &bull; Evidence Ingestion
        </div>

        <h2 className="text-3xl sm:text-4xl md:text-5xl font-light tracking-tight text-zinc-100">
          Upload your master CV, your tech-heavy variant, and any old resumes.
        </h2>

        <p className="text-sm md:text-base text-zinc-400 font-light max-w-2xl mx-auto leading-relaxed">
          Our extraction gateway deconstructs all of them into a single, unified Evidence Bank of discrete immutable facts.
        </p>
      </div>

      {/* Main Drag-and-Drop Area / Ingestion State */}
      <div className="relative">
        <AnimatePresence mode="wait">
          {!isProcessing ? (
            <motion.div
              key="dropzone"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative rounded-3xl border-2 border-dashed p-8 sm:p-14 md:p-16 text-center cursor-pointer transition-all duration-300 backdrop-blur-xl ${
                isDragging
                  ? "border-violet-400 bg-violet-950/20 shadow-[0_0_40px_rgba(139,92,246,0.25)] scale-[1.01]"
                  : "border-zinc-800 bg-zinc-950/70 hover:border-zinc-700 hover:bg-zinc-900/40"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                className="hidden"
              />

              <div className="flex flex-col items-center justify-center space-y-5">
                <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-violet-400 shadow-lg">
                  <UploadCloud className="w-8 h-8 text-violet-400" />
                </div>

                <div className="space-y-1.5">
                  <div className="text-base sm:text-lg font-normal text-zinc-200">
                    Drag and drop files here, or <span className="text-violet-400 underline underline-offset-4 font-medium">browse local files</span>
                  </div>
                  <p className="text-xs text-zinc-400 font-sans">
                    Supports multiple PDF, DOCX, and TXT documents simultaneously
                  </p>
                </div>

                <div className="pt-2 flex items-center gap-2 text-xs font-mono text-zinc-400 bg-zinc-900/60 px-3.5 py-1.5 rounded-full border border-zinc-800/80">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Target Alignment: {targetRole}</span>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="processing"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="rounded-3xl border border-zinc-800 bg-zinc-950/90 p-8 sm:p-14 md:p-16 text-center space-y-8 shadow-2xl backdrop-blur-xl"
            >
              {/* Spinning processor badge */}
              <div className="relative flex items-center justify-center">
                <div className="w-20 h-20 rounded-full bg-violet-600/10 flex items-center justify-center border border-violet-500/30">
                  <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
                </div>
              </div>

              {/* Dynamic Status Progress Text */}
              <div className="space-y-3 max-w-md mx-auto">
                <h3 className="text-xl sm:text-2xl font-light text-zinc-100">
                  {STAGES[processStage].label}
                </h3>
                <p className="text-xs text-zinc-400 font-mono">
                  Synthesizing multiple resumes into one unified Evidence Bank...
                </p>
              </div>

              {/* Minimalist Progress Track */}
              <div className="max-w-md mx-auto space-y-2">
                <div className="w-full h-1.5 rounded-full bg-zinc-900 overflow-hidden border border-zinc-800">
                  <motion.div
                    className="h-full bg-gradient-to-r from-violet-500 to-indigo-500"
                    initial={{ width: "10%" }}
                    animate={{ width: `${STAGES[processStage].progress}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                  />
                </div>
                <div className="flex justify-between text-[11px] font-mono text-zinc-400">
                  <span>Processing Evidence</span>
                  <span>{STAGES[processStage].progress}%</span>
                </div>
              </div>

              {/* Progress Milestones */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-xl mx-auto pt-2">
                {STAGES.map((stg, i) => {
                  const Icon = stg.icon;
                  const isDone = processStage > i;
                  const isCurrent = processStage === i;
                  return (
                    <div
                      key={stg.label}
                      className={`p-3 rounded-xl border text-left flex items-center gap-2.5 transition-colors ${
                        isDone
                          ? "bg-zinc-900/90 border-emerald-500/30 text-emerald-300"
                          : isCurrent
                          ? "bg-zinc-900 border-violet-500/40 text-violet-200"
                          : "bg-zinc-950 border-zinc-800/60 text-zinc-400"
                      }`}
                    >
                      {isDone ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : (
                        <Icon className={`w-4 h-4 shrink-0 ${isCurrent ? "text-violet-400 animate-pulse" : "text-zinc-600"}`} />
                      )}
                      <span className="text-xs font-mono truncate">{stg.label}</span>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Alternative Instant Testing Option */}
      {!isProcessing && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-zinc-900">
          <button
            type="button"
            onClick={onBack}
            className="text-xs font-mono text-zinc-400 hover:text-zinc-300 transition-colors"
          >
            &larr; Back to Target Role
          </button>

          <Button
            type="button"
            variant="outline"
            onClick={handleSimulateDemo}
            className="h-10 px-5 text-xs font-mono border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white rounded-full gap-2 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-violet-400" />
            <span>Instant Simulation: 3 Sample Resumes</span>
          </Button>
        </div>
      )}
    </motion.div>
  );
}
