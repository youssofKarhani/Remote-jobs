"use client";

import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { coverLetterApi } from "@/lib/api";
import {
  Copy,
  Check,
  Sparkles,
  Save,
  Loader2,
  AlertCircle,
  ShieldCheck,
  Compass,
  FileText,
} from "lucide-react";
import { vcopy } from "@/lib/verification-copy";

interface CoverLetterDrawerProps {
  jobId: string;
  jobTitle: string;
  companyName: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (letter: any) => void;
}

const CANONICAL_STRATEGIES = [
  { id: "Technical Depth", name: "Technical Depth", tagline: "Algorithmic & Systems", desc: "Emphasizes deep technical competence and backend mastery." },
  { id: "Systems Architecture", name: "Systems Architecture", tagline: "Scalability & Distributed", desc: "Focuses on designing resilient distributed cloud architectures." },
  { id: "Execution & Velocity", name: "Execution & Velocity", tagline: "Shipping & High Output", desc: "Highlights rapid delivery, pragmatic tradeoffs, and high momentum." },
  { id: "Leadership & Mentorship", name: "Leadership & Mentorship", tagline: "Team Catalyst", desc: "Focuses on unblocking peers, design reviews, and hiring." },
  { id: "Problem Solving", name: "Problem Solving", tagline: "Debugging & RCA", desc: "Emphasizes untangling ambiguous distributed failures." },
  { id: "Product-Minded Engineering", name: "Product-Minded Engineering", tagline: "Customer Impact", desc: "Bridges user outcomes with rock-solid engineering solutions." },
  { id: "Scale & High Throughput", name: "Scale & High Throughput", tagline: "Concurrency & Data", desc: "Focuses on high-volume pipelines, caching, and low latency." },
  { id: "Pragmatic Generalist", name: "Pragmatic Generalist", tagline: "Versatile Adaptability", desc: "Thrives across frontend, backend, devops, and infrastructure." },
  { id: "Modernization & Refactoring", name: "Modernization & Refactoring", tagline: "Legacy Migration", desc: "Specializes in replacing legacy debt with modern microservices." },
  { id: "Reliability & Resilience", name: "Reliability & Resilience", tagline: "SRE & Fault-Tolerance", desc: "Focuses on 99.99% uptime, alerting, and automated failover." },
];

export function CoverLetterDrawer({
  jobId,
  jobTitle,
  companyName,
  isOpen,
  onClose,
  onSuccess,
}: CoverLetterDrawerProps) {
  const [strategies, setStrategies] = useState(CANONICAL_STRATEGIES);
  const [selectedStrategy, setSelectedStrategy] = useState("Technical Depth");
  const [content, setContent] = useState("");
  const [referencedEvidenceIds, setReferencedEvidenceIds] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Fetch dynamic strategies if available
      coverLetterApi.getStrategies().then((res) => {
        if (Array.isArray(res) && res.length > 0) {
          setStrategies(res.map((s) => ({
            id: s.id || s.name,
            name: s.name,
            tagline: s.tagline || s.name,
            desc: s.description || "",
          })));
        }
      }).catch(() => {
        // Fallback to CANONICAL_STRATEGIES
      });

      // Check if existing cover letter exists for this job
      coverLetterApi.getCoverLetter(jobId).then((existing) => {
        if (existing && existing.content) {
          setContent(existing.content);
          setSelectedStrategy(existing.strategy || "Technical Depth");
          setReferencedEvidenceIds(existing.referenced_evidence_ids || []);
        }
      }).catch(() => {
        // No existing letter, ready for generation
      });
    }
  }, [isOpen, jobId]);

  const handleGenerate = async (strat?: string) => {
    const stratToUse = strat || selectedStrategy;
    setIsGenerating(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const res = await coverLetterApi.generateCoverLetter(jobId, stratToUse);
      setContent(res.content);
      setSelectedStrategy(res.strategy || stratToUse);
      setReferencedEvidenceIds(res.referenced_evidence_ids || []);
      setSuccessMessage(`Cover letter generated using "${stratToUse}" strategy.`);
      if (onSuccess) onSuccess(res);
    } catch (err: any) {
      console.error("Cover letter generation error:", err);
      setError(err?.message || "Failed to generate grounded cover letter.");
    } finally {
      setIsGenerating(false);
      setTimeout(() => setSuccessMessage(null), 4000);
    }
  };

  const handleSaveEdits = async () => {
    if (!content.trim()) return;
    setIsSaving(true);
    setError(null);
    try {
      const res = await coverLetterApi.updateCoverLetter(jobId, content);
      setSuccessMessage("Changes saved successfully to application records.");
      if (onSuccess) onSuccess(res);
    } catch (err: any) {
      setError(err?.message || "Failed to save cover letter updates.");
    } finally {
      setIsSaving(false);
      setTimeout(() => setSuccessMessage(null), 4000);
    }
  };

  const handleCopy = async () => {
    if (!content) return;
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Clipboard copy error:", err);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
      <DialogContent className="sm:max-w-[750px] max-h-[90vh] flex flex-col glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100 overflow-hidden">
        <DialogHeader className="shrink-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-indigo-950/80 border border-indigo-800/40 text-indigo-400">
              <Compass className="h-4 w-4" />
            </span>
            <DialogTitle className="text-lg font-semibold text-zinc-100">
              Engineering Positioning & Cover Letter Generator
            </DialogTitle>
          </div>
          <DialogDescription className="text-xs text-zinc-400">
            Generate a targeted, hallucination-free cover letter for{" "}
            <span className="text-zinc-200 font-medium">{jobTitle}</span> at{" "}
            <span className="text-zinc-200 font-medium">{companyName}</span> {vcopy("coverLetter.dialogSubtitle")}
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-4 py-2 pr-1">
          {error && (
            <div className="p-3 rounded-lg bg-red-950/40 border border-red-800/50 text-red-300 text-xs flex items-start gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-400" />
              <p>{error}</p>
            </div>
          )}

          {successMessage && (
            <div className="p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 text-xs flex items-center gap-2 font-mono">
              <Check className="h-4 w-4 text-emerald-400 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          {/* Strategy Selection Grid */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-zinc-300 uppercase tracking-wider font-mono">
              10 Canonical Engineering Positioning Strategies
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              {strategies.map((strat) => {
                const isSelected = selectedStrategy === strat.id || selectedStrategy === strat.name;
                return (
                  <button
                    key={strat.id}
                    type="button"
                    onClick={() => {
                      setSelectedStrategy(strat.id || strat.name);
                      handleGenerate(strat.id || strat.name);
                    }}
                    className={`p-2 rounded-lg border text-left transition-all text-xs flex flex-col justify-between ${
                      isSelected
                        ? "border-indigo-500 bg-indigo-950/40 text-zinc-100 shadow-sm"
                        : "border-zinc-800/80 bg-zinc-900/40 text-zinc-400 hover:border-zinc-700 hover:text-zinc-300"
                    }`}
                  >
                    <span className="font-semibold truncate w-full text-[11px] text-zinc-200">
                      {strat.name}
                    </span>
                    <span className="text-[10px] text-zinc-400 truncate w-full font-mono mt-0.5">
                      {strat.tagline}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Live Cover Letter Editor */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-zinc-300 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <FileText className="h-3.5 w-3.5 text-indigo-400" />
                <span>Generated Letter (Live Editable)</span>
              </label>

              {content && (
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleCopy}
                    className="h-7 px-2.5 text-xs gap-1 border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white"
                  >
                    {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{copied ? "Copied" : "Copy"}</span>
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSaveEdits}
                    disabled={isSaving}
                    className="h-7 px-2.5 text-xs gap-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700"
                  >
                    {isSaving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                    <span>Save Edits</span>
                  </Button>
                </div>
              )}
            </div>

            {isGenerating ? (
              <div className="h-64 rounded-xl border border-zinc-800 bg-zinc-900/40 flex flex-col items-center justify-center gap-3 text-zinc-400">
                <Loader2 className="h-6 w-6 animate-spin text-indigo-400" />
                <span className="text-xs font-mono">Synthesizing letter via &ldquo;{selectedStrategy}&rdquo; strategy...</span>
              </div>
            ) : (
              <Textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder={vcopy("coverLetter.placeholder")}
                className="h-64 font-sans text-xs sm:text-sm leading-relaxed bg-zinc-900/60 border-zinc-800 text-zinc-200 resize-none p-3.5"
              />
            )}
          </div>

          {/* Grounding & Evidence Proof */}
          {referencedEvidenceIds && referencedEvidenceIds.length > 0 && (
            <div className="p-3 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-2">
              <div className="flex items-center gap-1.5 text-xs font-mono text-zinc-300 font-medium">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                <span>{vcopy("coverLetter.groundedProof")}</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {referencedEvidenceIds.map((id) => (
                  <Badge key={id} variant="secondary" className="font-mono text-[10px] text-indigo-300 bg-indigo-950/60 border border-indigo-800/40">
                    {id}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="shrink-0 pt-2 border-t border-zinc-800/80 gap-2 sm:gap-0">
          <Button
            variant="outline"
            size="sm"
            onClick={onClose}
            className="text-xs border-zinc-800 bg-zinc-900 text-zinc-300"
          >
            Close
          </Button>

          <Button
            size="sm"
            onClick={() => handleGenerate()}
            disabled={isGenerating}
            className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white gap-1.5"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-3.5 w-3.5" />
                <span>Regenerate ({selectedStrategy})</span>
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
