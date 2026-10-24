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
import { Progress } from "@/components/ui/progress";
import { Job } from "@/types/job";
import { matchingApi, atsApi } from "@/lib/api";
import { TailorCVModal } from "./tailor-cv-modal";
import { CoverLetterDrawer } from "./cover-letter-drawer";
import { vcopy } from "@/lib/verification-copy";
import {
  Building,
  MapPin,
  ExternalLink,
  Sparkles,
  FileText,
  FileDown,
  BookmarkPlus,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Check,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

interface JobDetailDialogProps {
  job: Job | null;
  isOpen: boolean;
  onClose: () => void;
  onApplicationCreated?: () => void;
  onMatchUpdated?: (jobId: string, match: any) => void;
}

export function JobDetailDialog({
  job,
  isOpen,
  onClose,
  onApplicationCreated,
  onMatchUpdated,
}: JobDetailDialogProps) {
  const [matchData, setMatchData] = useState<any | null>(null);
  const [isLoadingMatch, setIsLoadingMatch] = useState(false);
  const [isSavingToATS, setIsSavingToATS] = useState(false);
  const [savedToATS, setSavedToATS] = useState(false);
  const [atsMessage, setAtsMessage] = useState<string | null>(null);

  // Modals state
  const [showTailorModal, setShowTailorModal] = useState(false);
  const [showCoverLetterDrawer, setShowCoverLetterDrawer] = useState(false);

  useEffect(() => {
    if (job && isOpen) {
      setSavedToATS(false);
      setAtsMessage(null);
      setIsLoadingMatch(true);

      // Fetch or compute real match
      matchingApi
        .matchJob(job.id)
        .then((res) => {
          setMatchData(res);
          if (onMatchUpdated) onMatchUpdated(job.id, res);
        })
        .catch((err) => {
          console.warn("Could not calculate match:", err?.message);
          setMatchData(null);
        })
        .finally(() => {
          setIsLoadingMatch(false);
        });
    }
  }, [job, isOpen]);

  if (!job) return null;

  const handleSaveToATS = async () => {
    setIsSavingToATS(true);
    setAtsMessage(null);
    try {
      await atsApi.createApplication({
        job_id: job.id,
        status: "Saved",
      });
      setSavedToATS(true);
      setAtsMessage("Saved to ATS pipeline under 'Saved' stage.");
      if (onApplicationCreated) onApplicationCreated();
    } catch (err: any) {
      setAtsMessage(err?.message || "Failed to save job to ATS.");
    } finally {
      setIsSavingToATS(false);
      setTimeout(() => setAtsMessage(null), 4000);
    }
  };

  const assessment = matchData?.assessment;
  const overallScore = matchData?.overall_score ?? null;

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400 border-emerald-500/40 bg-emerald-950/40";
    if (score >= 60) return "text-amber-400 border-amber-500/40 bg-amber-950/40";
    return "text-rose-400 border-rose-500/40 bg-rose-950/40";
  };

  return (
    <>
      <Dialog open={isOpen} onOpenChange={(open) => (!open ? onClose() : null)}>
        <DialogContent className="sm:max-w-[800px] max-h-[90vh] flex flex-col glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100 overflow-hidden">
          <DialogHeader className="shrink-0 pb-3 border-b border-zinc-800/80">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <DialogTitle className="text-xl font-bold text-zinc-100">
                    {job.title}
                  </DialogTitle>
                  {job.remote && (
                    <Badge variant="secondary" className="text-xs bg-zinc-800 text-zinc-200">
                      🌎 Remote
                    </Badge>
                  )}
                </div>

                <DialogDescription className="flex items-center gap-3 text-xs font-medium text-zinc-400">
                  <span className="flex items-center gap-1">
                    <Building className="h-3.5 w-3.5 text-zinc-400" />
                    {job.company_name}
                  </span>
                  <span>&bull;</span>
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5 text-zinc-400" />
                    {job.location}
                  </span>
                </DialogDescription>
              </div>

              {job.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors border border-zinc-800 bg-zinc-900/60 px-3 py-1.5 rounded-lg shrink-0"
                >
                  <span>Original Post</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto space-y-5 py-3 pr-1 text-xs">
            {atsMessage && (
              <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-200 flex items-center gap-2">
                <Check className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>{atsMessage}</span>
              </div>
            )}

            {/* AI Compatibility & Match Score Section */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-violet-950/80 border border-violet-800/40 text-violet-400">
                    <TrendingUp className="h-4 w-4" />
                  </span>
                  <div>
                    <h4 className="text-sm font-semibold text-zinc-100">
                      AI Compatibility Assessment
                    </h4>
                    <p className="text-[11px] text-zinc-400">
                      {vcopy("job.matchScoreTooltip")}
                    </p>
                  </div>
                </div>

                {isLoadingMatch ? (
                  <div className="flex items-center gap-1.5 font-mono text-zinc-400 text-xs">
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-violet-400" />
                    <span>Analyzing...</span>
                  </div>
                ) : overallScore !== null ? (
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-sm font-bold font-mono px-3 py-1 rounded-full border ${getScoreColor(
                        overallScore
                      )}`}
                    >
                      {overallScore}% Match
                    </span>
                    <Badge
                      variant="outline"
                      className="capitalize text-xs font-mono border-zinc-700 text-zinc-300"
                    >
                      {matchData.recommendation || "Consider"}
                    </Badge>
                    {assessment?.evaluation_mode === "heuristic" ? (
                      <Badge variant="outline" className="text-[10px] font-mono border-amber-800/60 bg-amber-950/40 text-amber-300">
                        Heuristic
                      </Badge>
                    ) : assessment?.evaluation_mode === "prescreen_filtered" ? (
                      <Badge variant="outline" className="text-[10px] font-mono border-zinc-800 bg-zinc-900/60 text-zinc-400">
                        Pre-Screened
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] font-mono border-violet-800/60 bg-violet-950/40 text-violet-300">
                        AI Mode
                      </Badge>
                    )}
                  </div>
                ) : (
                  <Badge variant="outline" className="text-xs font-mono text-zinc-400">
                    No Assessment Available
                  </Badge>
                )}
              </div>

              {assessment && (
                <div className="space-y-3 pt-2 border-t border-zinc-800/60">
                  {/* Subscore metrics */}
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-[11px] font-mono">
                    <div className="p-2 rounded bg-zinc-950/60 border border-zinc-800/60">
                      <span className="text-zinc-400 block text-[10px]">Skills</span>
                      <span className="text-zinc-100 font-bold">{assessment.skills_score}%</span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950/60 border border-zinc-800/60">
                      <span className="text-zinc-400 block text-[10px]">Experience</span>
                      <span className="text-zinc-100 font-bold">{assessment.experience_score}%</span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950/60 border border-zinc-800/60">
                      <span className="text-zinc-400 block text-[10px]">Seniority</span>
                      <span className="text-zinc-100 font-bold">{assessment.seniority_score}%</span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950/60 border border-zinc-800/60">
                      <span className="text-zinc-400 block text-[10px]">Location</span>
                      <span className="text-zinc-100 font-bold">{assessment.location_score}%</span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950/60 border border-zinc-800/60">
                      <span className="text-zinc-400 block text-[10px]">Language</span>
                      <span className="text-zinc-100 font-bold">{assessment.language_score}%</span>
                    </div>
                  </div>

                  {/* Strengths & Gaps */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                    {assessment.strengths && assessment.strengths.length > 0 && (
                      <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/30 space-y-1.5">
                        <span className="font-semibold text-emerald-400 flex items-center gap-1.5 text-[11px] uppercase tracking-wider font-mono">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          Matched Strengths
                        </span>
                        <ul className="space-y-1 text-zinc-300">
                          {assessment.strengths.map((s: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-1.5">
                              <span className="text-emerald-400 shrink-0">&bull;</span>
                              <span>{s}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {assessment.missing_requirements && assessment.missing_requirements.length > 0 && (
                      <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/30 space-y-1.5">
                        <span className="font-semibold text-amber-400 flex items-center gap-1.5 text-[11px] uppercase tracking-wider font-mono">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          Missing or Discrepant Requirements
                        </span>
                        <ul className="space-y-1 text-zinc-300">
                          {assessment.missing_requirements.map((g: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-1.5">
                              <span className="text-amber-400 shrink-0">&bull;</span>
                              <span>{g}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Tags & Metadata */}
            <div className="flex flex-wrap gap-1.5">
              {job.job_types?.map((t) => (
                <Badge key={t} variant="outline" className="text-zinc-300 border-zinc-800">
                  {t}
                </Badge>
              ))}
              {job.tags?.map((tag) => (
                <Badge key={tag} variant="secondary" className="font-mono text-zinc-300 bg-zinc-900 border border-zinc-800">
                  {tag}
                </Badge>
              ))}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider font-mono">
                Job Description
              </h4>
              <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 text-zinc-300 whitespace-pre-wrap leading-relaxed text-xs max-h-72 overflow-y-auto">
                {job.description}
              </div>
            </div>
          </div>

          <DialogFooter className="shrink-0 pt-3 border-t border-zinc-800/80 flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSaveToATS}
                disabled={isSavingToATS || savedToATS}
                className={`text-xs gap-1.5 border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white ${
                  savedToATS ? "border-emerald-500/40 text-emerald-400" : ""
                }`}
              >
                {savedToATS ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-400" />
                    <span>Saved in ATS</span>
                  </>
                ) : (
                  <>
                    <BookmarkPlus className="h-3.5 w-3.5" />
                    <span>Track in ATS</span>
                  </>
                )}
              </Button>
            </div>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                onClick={() => setShowCoverLetterDrawer(true)}
                className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white gap-1.5"
              >
                <FileText className="h-3.5 w-3.5" />
                <span>Cover Letter</span>
              </Button>

              <Button
                size="sm"
                onClick={() => setShowTailorModal(true)}
                className="text-xs bg-violet-600 hover:bg-violet-500 text-white gap-1.5"
              >
                <Sparkles className="h-3.5 w-3.5" />
                <span>Tailor CV (.docx)</span>
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Tailor CV Modal */}
      <TailorCVModal
        jobId={job.id}
        jobTitle={job.title}
        companyName={job.company_name}
        isOpen={showTailorModal}
        onClose={() => setShowTailorModal(false)}
      />

      {/* Cover Letter Drawer */}
      <CoverLetterDrawer
        jobId={job.id}
        jobTitle={job.title}
        companyName={job.company_name}
        isOpen={showCoverLetterDrawer}
        onClose={() => setShowCoverLetterDrawer(false)}
      />
    </>
  );
}
