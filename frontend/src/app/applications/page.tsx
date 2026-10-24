"use client";

import { useEffect, useState, useCallback } from "react";
import {
  FolderKanban,
  Building,
  MapPin,
  ExternalLink,
  FileDown,
  FileText,
  Clock,
  Trash2,
  ChevronRight,
  Sparkles,
  CheckCircle2,
  Loader2,
  DollarSign,
  Calendar,
  AlertCircle,
  Plus,
} from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { vcopy } from "@/lib/verification-copy";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { atsApi, tailoringApi, coverLetterApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { AuthDialog } from "@/components/auth/auth-dialog";
import { Application, ApplicationStage } from "@/types/application";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

const STAGES: { id: ApplicationStage; label: string; color: string; bg: string; border: string }[] = [
  { id: "Saved", label: "Saved", color: "text-zinc-400", bg: "bg-zinc-900/40", border: "border-zinc-800" },
  { id: "Applying", label: "Drafting / Applying", color: "text-blue-400", bg: "bg-blue-950/20", border: "border-blue-800/40" },
  { id: "Applied", label: "Applied", color: "text-violet-400", bg: "bg-violet-950/20", border: "border-violet-800/40" },
  { id: "Interview", label: "Interviewing", color: "text-amber-400", bg: "bg-amber-950/20", border: "border-amber-800/40" },
  { id: "Offer", label: "Offer Received", color: "text-emerald-400", bg: "bg-emerald-950/20", border: "border-emerald-800/40" },
  { id: "Rejected", label: "Archived / Rejected", color: "text-rose-400", bg: "bg-rose-950/20", border: "border-rose-800/40" },
];

export default function ApplicationsPage() {
  const { isAuthenticated, loginAsDemo } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  // Cover Letter View Dialog
  const [selectedLetter, setSelectedLetter] = useState<{ title: string; content: string } | null>(null);

  const loadApplications = useCallback(async () => {
    if (!isAuthenticated) {
      setApplications([]);
      return;
    }
    setIsLoading(true);
    try {
      const res = await atsApi.getApplications();
      if (Array.isArray(res)) {
        setApplications(res);
      }
    } catch (err: any) {
      console.warn("Could not load applications:", err?.message);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadApplications();
  }, [loadApplications]);

  const handleUpdateStage = async (appId: string, nextStage: ApplicationStage) => {
    setUpdatingId(appId);
    try {
      await atsApi.updateStatus(appId, nextStage);
      setApplications((prev) =>
        prev.map((app) => (app.id === appId ? { ...app, status: nextStage } : app))
      );
    } catch (err) {
      console.error("Failed to update status:", err);
      loadApplications();
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDelete = async (appId: string) => {
    try {
      await atsApi.deleteApplication(appId);
      setApplications((prev) => prev.filter((app) => app.id !== appId));
    } catch (err) {
      console.error("Failed to delete application:", err);
    }
  };

  const handleViewCoverLetter = async (jobId: string, title: string) => {
    try {
      const res = await coverLetterApi.getCoverLetter(jobId);
      if (res && res.content) {
        setSelectedLetter({ title, content: res.content });
      } else {
        setSelectedLetter({
          title,
          content:
            vcopy("applications.emptyCoverLetter"),
        });
      }
    } catch (err) {
      console.warn("No cover letter found:", err);
      setSelectedLetter({
        title,
        content:
          vcopy("applications.emptyCoverLetter"),
      });
    }
  };

  const filteredApps = applications.filter((app) => {
    const title = app.job?.title?.toLowerCase() || "";
    const company = app.job?.company_name?.toLowerCase() || "";
    const q = searchTerm.toLowerCase();
    return title.includes(q) || company.includes(q);
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Application Tracking System (ATS)"
        subtitle="Manage your job pipeline across deterministic stages with attached tailored CVs and generated cover letters."
      >
        <Link href="/jobs">
          <Button size="sm" className="gap-1.5 text-xs bg-violet-600 hover:bg-violet-500 text-white">
            <Plus className="h-3.5 w-3.5" />
            Discover &amp; Track Jobs
          </Button>
        </Link>
      </PageHeader>

      {!isAuthenticated && (
        <Card className="p-8 text-center glass-card border-dashed border-zinc-800 bg-zinc-950/40 space-y-4">
          <div className="h-10 w-10 rounded-xl bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400 mx-auto">
            <FolderKanban className="h-5 w-5" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-semibold text-zinc-200">Sign in to Access Your ATS Pipeline</h3>
            <p className="text-xs text-zinc-400 max-w-md mx-auto">
              Track multi-stage candidate submissions, download tailored Word (.docx) documents, and review engineering cover letters.
            </p>
          </div>
          <div className="flex items-center justify-center gap-3 pt-2">
            <Button size="sm" onClick={loginAsDemo} className="text-xs gap-1.5 bg-violet-600 hover:bg-violet-500 text-white">
              <Sparkles className="h-3.5 w-3.5" />
              One-Click Demo Mode
            </Button>
            <AuthDialog>
              <Button size="sm" variant="outline" className="text-xs border-zinc-800 bg-zinc-900/60 text-zinc-300">
                Sign In / Register
              </Button>
            </AuthDialog>
          </div>
        </Card>
      )}

      {isAuthenticated && (
        <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
          <Input
            placeholder="Search tracked applications by job title or company..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md text-xs bg-zinc-950/60 border-zinc-800 text-zinc-200"
          />
          <div className="text-xs font-mono text-zinc-400">
            Total Active Applications: <span className="font-semibold text-zinc-200">{applications.length}</span>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="p-16 text-center text-zinc-400 flex flex-col items-center gap-2">
          <Loader2 className="h-6 w-6 animate-spin text-violet-400" />
          <span className="text-xs font-mono">Loading Kanban board...</span>
        </div>
      ) : isAuthenticated && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3.5 items-start">
          {STAGES.map((stage) => {
            const stageApps = filteredApps.filter((a) => a.status === stage.id);
            return (
              <div
                key={stage.id}
                className={`rounded-2xl border ${stage.border} ${stage.bg} p-3 min-h-[480px] flex flex-col backdrop-blur-sm`}
              >
                {/* Column Header */}
                <div className="flex items-center justify-between pb-3 border-b border-zinc-800/60 mb-3">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-semibold uppercase tracking-wider font-mono ${stage.color}`}>
                      {stage.label}
                    </span>
                  </div>
                  <Badge variant="outline" className="text-[10px] font-mono border-zinc-800 text-zinc-300">
                    {stageApps.length}
                  </Badge>
                </div>

                {/* Cards in column */}
                <div className="space-y-3 flex-1 overflow-y-auto">
                  {stageApps.length === 0 ? (
                    <div className="h-28 flex items-center justify-center text-zinc-600 text-[11px] font-mono border border-dashed border-zinc-800/50 rounded-xl">
                      No applications
                    </div>
                  ) : (
                    stageApps.map((app) => (
                      <Card
                        key={app.id}
                        className="glass-card border-zinc-800/80 bg-zinc-950/90 shadow-md p-3 space-y-2.5 transition-all hover:border-zinc-700"
                      >
                        <div className="space-y-1">
                          <h4 className="text-xs font-semibold text-zinc-100 line-clamp-1">
                            {app.job?.title || "Untargeted Position"}
                          </h4>
                          <div className="flex items-center gap-1.5 text-[11px] text-zinc-400 truncate">
                            <Building className="h-3 w-3 shrink-0" />
                            <span className="truncate">{app.job?.company_name || "Unknown Company"}</span>
                          </div>
                          {app.job?.location && (
                            <div className="flex items-center gap-1 text-[10px] text-zinc-500 truncate">
                              <MapPin className="h-2.5 w-2.5 shrink-0" />
                              <span className="truncate">{app.job?.location}</span>
                            </div>
                          )}
                        </div>

                        {app.salary_offered && (
                          <div className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                            <DollarSign className="h-3 w-3" />
                            <span>{app.salary_offered.toLocaleString()}</span>
                          </div>
                        )}

                        {/* Artifact attachments */}
                        <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-zinc-900">
                          {app.tailored_cv_id && (
                            <a
                              href={tailoringApi.getDownloadUrl(app.tailored_cv_id)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-1.5 py-0.5 rounded hover:bg-emerald-900/40 transition-colors"
                            >
                              <FileDown className="h-2.5 w-2.5" />
                              <span>Tailored CV</span>
                            </a>
                          )}

                          {app.job_id && (
                            <button
                              type="button"
                              onClick={() => handleViewCoverLetter(app.job_id, app.job?.title || "Job")}
                              className="inline-flex items-center gap-1 text-[10px] font-mono text-indigo-400 bg-indigo-950/40 border border-indigo-800/40 px-1.5 py-0.5 rounded hover:bg-indigo-900/40 transition-colors"
                            >
                              <FileText className="h-2.5 w-2.5" />
                              <span>Cover Letter</span>
                            </button>
                          )}
                        </div>

                        {/* Stage Mover Controls */}
                        <div className="pt-2 border-t border-zinc-900 flex items-center justify-between">
                          <select
                            value={app.status}
                            disabled={updatingId === app.id}
                            onChange={(e) => handleUpdateStage(app.id, e.target.value as ApplicationStage)}
                            className="text-[10px] font-mono bg-zinc-900 border border-zinc-800 text-zinc-300 rounded px-1.5 py-0.5 focus:outline-none"
                          >
                            {STAGES.map((s) => (
                              <option key={s.id} value={s.id}>
                                {s.label}
                              </option>
                            ))}
                          </select>

                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDelete(app.id)}
                            title="Delete tracked application"
                            className="h-6 w-6 p-0 text-zinc-500 hover:text-red-400 hover:bg-red-950/30"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </Card>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* View Cover Letter Dialog */}
      <Dialog open={Boolean(selectedLetter)} onOpenChange={(open) => (!open ? setSelectedLetter(null) : null)}>
        <DialogContent className="sm:max-w-[600px] glass-card border-zinc-800 bg-zinc-950/95 text-zinc-100">
          <DialogHeader>
            <DialogTitle className="text-base text-zinc-100">
              Attached Cover Letter: {selectedLetter?.title}
            </DialogTitle>
            <DialogDescription className="text-xs text-zinc-400">
              Deterministic, grounded engineering cover letter stored for this application.
            </DialogDescription>
          </DialogHeader>
          <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/60 text-xs text-zinc-200 whitespace-pre-wrap leading-relaxed max-h-[60vh] overflow-y-auto">
            {selectedLetter?.content}
          </div>
          <div className="flex justify-end pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedLetter(null)}
              className="text-xs border-zinc-800 text-zinc-300"
            >
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
