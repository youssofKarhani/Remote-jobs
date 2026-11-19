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
import { ExtractionSummaryData } from "./evidence-bank-step";
import { CvExtractionPreview } from "@/components/cv/cv-extraction-preview";
import { useGatedCvExtraction, CvSource, sourceLabel } from "@/lib/use-gated-cv-extraction";
import { vcopy } from "@/lib/verification-copy";

interface EvidenceStepProps {
  targetRole: string;
  onComplete: (summary: ExtractionSummaryData) => void;
  onBack: () => void;
}

export function EvidenceStep({ targetRole, onComplete, onBack }: EvidenceStepProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [activeTab, setActiveTab] = useState<"upload" | "paste">("upload");
  const [pastedText, setPastedText] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const extraction = useGatedCvExtraction((summary, source) => {
    onComplete({
      experiencesCount: summary.experiences_extracted || 0,
      bulletsCount: summary.bullets_extracted || 0,
      skillsCount: summary.skills_extracted || 0,
      projectsCount: summary.projects_extracted || 0,
      educationCount: summary.education_extracted || 0,
      certificationsCount: summary.certifications_extracted || 0,
      sourceFilename: sourceLabel(source),
    });
  });
  const isProcessing = extraction.isBusy && !extraction.preview;
  const errorMessage = extraction.preview ? null : extraction.error;
  const statusMessage =
    extraction.phase === "saving" ? "Saving your CV to your profile..." : "Reading your CV...";

  const executeExtraction = (source: CvSource) => {
    void extraction.extract(source);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      executeExtraction({ kind: "file", file });
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      executeExtraction({ kind: "file", file });
    }
  };

  const handlePasteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!pastedText.trim()) {
      extraction.setError("Please paste resume text before proceeding.");
      return;
    }
    executeExtraction({ kind: "text", text: pastedText, label: "Pasted resume text" });
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
          {extraction.preview ? (
            <motion.div
              key="preview-stage"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <CvExtractionPreview
                result={extraction.preview}
                phase={extraction.phase}
                error={extraction.error}
                onDiscard={extraction.discard}
                onRetrySave={extraction.retrySave}
              />
            </motion.div>
          ) : !isProcessing ? (
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

      {!isProcessing && !extraction.preview && (
        <div className="flex items-center pt-2 border-t border-zinc-900">
          <button
            type="button"
            onClick={onBack}
            className="text-xs font-mono text-zinc-400 hover:text-zinc-300 transition-colors"
          >
            &larr; Back to Target Role
          </button>
        </div>
      )}
    </motion.div>
  );
}
