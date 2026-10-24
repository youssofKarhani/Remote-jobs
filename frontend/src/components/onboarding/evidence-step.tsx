"use client";

import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  Loader2,
  Sparkles,
  ShieldCheck,
  AlertCircle,
  FileCode,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cvApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ExtractionSummaryData } from "./evidence-bank-step";
import { vcopy } from "@/lib/verification-copy";

const SAMPLE_DEMO_CV = `Alex Rivera
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
  onComplete: (summary: ExtractionSummaryData) => void;
  onBack: () => void;
}

export function EvidenceStep({ targetRole, onComplete, onBack }: EvidenceStepProps) {
  const { isAuthenticated, loginAsDemo } = useAuth();
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"upload" | "paste">("upload");
  const [pastedText, setPastedText] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const executeExtraction = async (file?: File, text?: string, filename?: string) => {
    setIsProcessing(true);
    setErrorMessage(null);
    setStatusMessage("Initializing extraction pipeline...");

    try {
      // Ensure session is active so backend persists the evidence
      if (!isAuthenticated) {
        setStatusMessage("Establishing candidate session...");
        await loginAsDemo();
      }

      let res;
      if (file) {
        setStatusMessage(`Parsing document ${file.name}...`);
        res = await cvApi.uploadCV(file);
      } else if (text && text.trim()) {
        setStatusMessage("Analyzing resume text through AI Gateway...");
        res = await cvApi.parseText(text);
      } else {
        throw new Error("Please select a file or paste resume text.");
      }

      setStatusMessage(vcopy("cvUpload.persistingStep"));

      const summary = res?.summary || {
        experiences_extracted: 0,
        bullets_extracted: 0,
        skills_extracted: 0,
        projects_extracted: 0,
        education_extracted: 0,
        certifications_extracted: 0,
      };

      const finalData: ExtractionSummaryData = {
        experiencesCount: summary.experiences_extracted || 0,
        bulletsCount: summary.bullets_extracted || 0,
        skillsCount: summary.skills_extracted || 0,
        projectsCount: summary.projects_extracted || 0,
        educationCount: summary.education_extracted || 0,
        certificationsCount: summary.certifications_extracted || 0,
        sourceFilename: filename || (file ? file.name : "Pasted Resume Text"),
      };

      onComplete(finalData);
    } catch (err: any) {
      console.error("Extraction error:", err);
      setErrorMessage(
        err?.message || "Failed to parse document. Please check the file format and try again."
      );
      setIsProcessing(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      executeExtraction(file, undefined, file.name);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      executeExtraction(file, undefined, file.name);
    }
  };

  const handleSimulateSample = () => {
    executeExtraction(undefined, SAMPLE_DEMO_CV, "Alex_Rivera_Sample_CV.txt");
  };

  const handlePasteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!pastedText.trim()) {
      setErrorMessage("Please paste resume text before proceeding.");
      return;
    }
    executeExtraction(undefined, pastedText, "Pasted Technical Resume");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto w-full py-6 md:py-10 space-y-8"
    >
      {/* Top Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-zinc-900 border border-zinc-800 text-zinc-400">
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
          Step 02 &bull; Resume Ingestion
        </div>

        <h2 className="text-3xl sm:text-4xl md:text-5xl font-light tracking-tight text-zinc-100">
          Upload your existing CV or experience.
        </h2>

        <p className="text-sm md:text-base text-zinc-400 font-light max-w-2xl mx-auto leading-relaxed">
          {vcopy("onboarding.evidenceSubtitle")}

        </p>
      </div>

      {/* Error alert if any */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/30 flex items-center gap-3 text-destructive text-xs sm:text-sm max-w-2xl mx-auto">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Main Container */}
      <div className="relative">
        <AnimatePresence mode="wait">
          {!isProcessing ? (
            <motion.div
              key="input-stage"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="space-y-4"
            >
              {/* Tab Selector */}
              <div className="flex items-center justify-center gap-2 pb-2">
                <button
                  type="button"
                  onClick={() => setActiveTab("upload")}
                  className={`px-4 py-1.5 rounded-full text-xs font-mono transition-colors ${
                    activeTab === "upload"
                      ? "bg-violet-600 text-white font-medium"
                      : "bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800"
                  }`}
                >
                  File Upload (PDF / DOCX / TXT)
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("paste")}
                  className={`px-4 py-1.5 rounded-full text-xs font-mono transition-colors ${
                    activeTab === "paste"
                      ? "bg-violet-600 text-white font-medium"
                      : "bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800"
                  }`}
                >
                  Paste Plain Text
                </button>
              </div>

              {activeTab === "upload" ? (
                <div
                  onDragOver={(e) => {
                    e.preventDefault();
                    setIsDragging(true);
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`relative rounded-3xl border-2 border-dashed p-8 sm:p-12 md:p-14 text-center cursor-pointer transition-all duration-300 backdrop-blur-xl ${
                    isDragging
                      ? "border-violet-400 bg-violet-950/20 shadow-[0_0_40px_rgba(139,92,246,0.25)] scale-[1.01]"
                      : "border-zinc-800 bg-zinc-950/70 hover:border-zinc-700 hover:bg-zinc-900/40"
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.doc,.txt,.md"
                    onChange={handleFileChange}
                    className="hidden"
                  />

                  <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-violet-400 shadow-lg">
                      <UploadCloud className="w-8 h-8 text-violet-400" />
                    </div>

                    <div className="space-y-1">
                      <div className="text-base sm:text-lg font-normal text-zinc-200">
                        Drag and drop your resume here, or{" "}
                        <span className="text-violet-400 underline underline-offset-4 font-medium">
                          browse files
                        </span>
                      </div>
                      <p className="text-xs text-zinc-400 font-sans">
                        Supports PDF, DOCX, and TXT up to 15MB
                      </p>
                    </div>

                    <div className="pt-2 flex items-center gap-2 text-xs font-mono text-zinc-400 bg-zinc-900/60 px-3.5 py-1.5 rounded-full border border-zinc-800/80">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Targeting: {targetRole || "Software Engineer"}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <form
                  onSubmit={handlePasteSubmit}
                  className="rounded-3xl border border-zinc-800 bg-zinc-950/70 p-6 sm:p-8 space-y-4 backdrop-blur-xl"
                >
                  <div className="space-y-1">
                    <label className="text-xs font-mono text-zinc-400">
                      Paste Resume Content (Plain Text)
                    </label>
                    <textarea
                      value={pastedText}
                      onChange={(e) => setPastedText(e.target.value)}
                      placeholder="Paste your resume or CV text here..."
                      rows={10}
                      className="w-full bg-zinc-900/80 border border-zinc-800 rounded-xl p-4 text-xs font-mono text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-violet-500 transition-colors"
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button
                      type="submit"
                      disabled={!pastedText.trim()}
                      className="bg-violet-600 hover:bg-violet-500 text-white text-xs font-mono rounded-xl px-5 h-10 gap-2"
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      Extract Experience
                    </Button>
                  </div>
                </form>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="processing-stage"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="rounded-3xl border border-zinc-800 bg-zinc-950/90 p-8 sm:p-14 text-center space-y-6 shadow-2xl backdrop-blur-xl"
            >
              <div className="w-16 h-16 rounded-full bg-violet-600/10 flex items-center justify-center border border-violet-500/30 mx-auto">
                <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
              </div>

              <div className="space-y-2 max-w-md mx-auto">
                <h3 className="text-xl font-light text-zinc-100">
                  {statusMessage || vcopy("onboarding.extractStatus")}
                </h3>
                <p className="text-xs text-zinc-400 font-mono">
                  {vcopy("onboarding.deconstructStatus")}
                </p>
              </div>

              <div className="pt-2 flex items-center justify-center gap-2 text-xs font-mono text-zinc-400">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Deterministic Zero-Hallucination Pipeline</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Instant Testing Option for Demo / Quick Verification */}
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
            onClick={handleSimulateSample}
            className="h-10 px-5 text-xs font-mono border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white rounded-full gap-2 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-violet-400" />
            <span>Load Sample Technical Resume</span>
          </Button>
        </div>
      )}
    </motion.div>
  );
}
