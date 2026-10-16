"use client";

import React, { useState } from "react";
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
import { tailoringApi } from "@/lib/api";
import { FileDown, FileText, CheckCircle2, Loader2, Sparkles, AlertCircle, ShieldCheck } from "lucide-react";

interface TailorCVModalProps {
  jobId: string;
  jobTitle: string;
  companyName: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (doc: any) => void;
}

export function TailorCVModal({
  jobId,
  jobTitle,
  companyName,
  isOpen,
  onClose,
  onSuccess,
}: TailorCVModalProps) {
  const [maxBullets, setMaxBullets] = useState<number>(4);
  const [templateName, setTemplateName] = useState<string>("modern_template");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const doc = await tailoringApi.tailorCV(jobId, {
        max_bullets_per_role: maxBullets,
        template_name: templateName,
      });
      setGeneratedDoc(doc);
      if (onSuccess) onSuccess(doc);
    } catch (err: any) {
      console.error("CV Tailoring error:", err);
      setError(err?.message || "Failed to generate tailored CV. Please ensure you have verified evidence in your profile.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleReset = () => {
    setGeneratedDoc(null);
    setError(null);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? handleReset() : null)}>
      <DialogContent className="sm:max-w-[560px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 rounded-lg bg-violet-950/80 border border-violet-800/40 text-violet-400">
              <Sparkles className="h-4 w-4" />
            </span>
            <DialogTitle className="text-lg font-semibold text-zinc-100">
              Deterministic CV Tailoring Pipeline
            </DialogTitle>
          </div>
          <DialogDescription className="text-xs text-zinc-400">
            Tailor your verified Evidence Bank into a production Word (.docx) document optimized for{" "}
            <span className="text-zinc-200 font-medium">{jobTitle}</span> at{" "}
            <span className="text-zinc-200 font-medium">{companyName}</span>.
          </DialogDescription>
        </DialogHeader>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/40 border border-red-800/50 text-red-300 text-xs flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-400" />
            <div className="space-y-1">
              <span className="font-semibold">Tailoring Issue</span>
              <p>{error}</p>
            </div>
          </div>
        )}

        {!generatedDoc ? (
          <div className="space-y-4 py-2">
            <div className="space-y-2 p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-900/50">
              <label className="text-xs font-medium text-zinc-300 flex items-center justify-between">
                <span>Maximum Bullets per Role</span>
                <span className="font-mono text-violet-400 font-semibold">{maxBullets} bullets</span>
              </label>
              <div className="grid grid-cols-5 gap-2">
                {[2, 3, 4, 5, 6].map((num) => (
                  <Button
                    key={num}
                    type="button"
                    variant={maxBullets === num ? "default" : "outline"}
                    size="sm"
                    onClick={() => setMaxBullets(num)}
                    className={`h-8 text-xs font-mono ${
                      maxBullets === num
                        ? "bg-violet-600 hover:bg-violet-500 text-white"
                        : "border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:text-zinc-200"
                    }`}
                  >
                    {num}
                  </Button>
                ))}
              </div>
              <p className="text-[11px] text-zinc-400">
                Determines how many high-relevance achievement bullets are selected for each work experience record.
              </p>
            </div>

            <div className="space-y-2 p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-900/50">
              <label className="text-xs font-medium text-zinc-300">
                Word Document (.docx) Template
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setTemplateName("modern_template")}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    templateName === "modern_template"
                      ? "border-violet-500/80 bg-violet-950/30 text-zinc-100"
                      : "border-zinc-800 bg-zinc-900/40 text-zinc-400 hover:text-zinc-300"
                  }`}
                >
                  <div className="text-xs font-semibold text-zinc-200 flex items-center gap-1.5">
                    <FileText className="h-3.5 w-3.5 text-violet-400" />
                    <span>Modern Executive</span>
                  </div>
                  <p className="text-[10px] text-zinc-400 mt-1 font-mono">
                    Clean typography, skills badges, structured timeline.
                  </p>
                </button>

                <button
                  type="button"
                  onClick={() => setTemplateName("minimal_template")}
                  className={`p-3 rounded-lg border text-left transition-all opacity-60 cursor-not-allowed ${
                    templateName === "minimal_template"
                      ? "border-violet-500/80 bg-violet-950/30 text-zinc-100"
                      : "border-zinc-800 bg-zinc-900/40 text-zinc-400"
                  }`}
                  disabled
                >
                  <div className="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
                    <FileText className="h-3.5 w-3.5 text-zinc-500" />
                    <span>Academic Plain</span>
                  </div>
                  <p className="text-[10px] text-zinc-400 mt-1 font-mono">
                    Minimalist serif layout (Coming soon).
                  </p>
                </button>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-zinc-900/80 border border-zinc-800 text-[11px] text-zinc-400 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0" />
              <span>
                Zero Hallucination Guarantee: All statements are sourced verbatim from your verified Evidence Bank.
              </span>
            </div>
          </div>
        ) : (
          <div className="space-y-4 py-3">
            <div className="p-5 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 text-center space-y-3">
              <div className="h-10 w-10 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 mx-auto">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <h4 className="text-sm font-semibold text-zinc-100">Tailored CV Generated Successfully</h4>
                <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                  Your customized .docx resume has been rendered using verified evidence points tailored to {jobTitle}.
                </p>
              </div>

              <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
                <Badge variant="outline" className="text-xs font-mono text-zinc-300">
                  Format: {generatedDoc.format?.toUpperCase() || "DOCX"}
                </Badge>
                {generatedDoc.selected_evidence_ids && (
                  <Badge variant="secondary" className="text-xs font-mono text-emerald-400 bg-emerald-950/50">
                    {generatedDoc.selected_evidence_ids.length} Evidence Bullets Grounded
                  </Badge>
                )}
              </div>
            </div>

            <div className="flex justify-center pt-2">
              <a
                href={tailoringApi.getDownloadUrl(generatedDoc.id)}
                download
                target="_blank"
                rel="noopener noreferrer"
                className="w-full"
              >
                <Button className="w-full gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs h-10 shadow-lg shadow-emerald-600/20">
                  <FileDown className="h-4 w-4" />
                  Download Tailored Document (.docx)
                </Button>
              </a>
            </div>
          </div>
        )}

        <DialogFooter className="gap-2 sm:gap-0">
          {!generatedDoc ? (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={onClose}
                disabled={isGenerating}
                className="text-xs border-zinc-800 bg-zinc-900 text-zinc-300"
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleGenerate}
                disabled={isGenerating}
                className="text-xs bg-violet-600 hover:bg-violet-500 text-white gap-1.5"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Generating .docx...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Generate Tailored CV</span>
                  </>
                )}
              </Button>
            </>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              className="text-xs border-zinc-800 bg-zinc-900 text-zinc-300"
            >
              Done
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
