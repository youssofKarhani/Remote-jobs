"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Briefcase,
  MapPin,
  Building,
  ExternalLink,
  RefreshCw,
  Sparkles,
  CheckCircle2,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Filter,
  SlidersHorizontal,
} from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { jobsApi, matchingApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { AuthDialog } from "@/components/auth/auth-dialog";
import { JobDetailDialog } from "@/components/jobs/job-detail-dialog";
import { Job } from "@/types/job";

export default function JobsPage() {
  const { isAuthenticated, loginAsDemo } = useAuth();
  const [searchTerm, setSearchTerm] = useState("");
  const [isSyncing, setIsSyncing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [applyPreferences, setApplyPreferences] = useState(false);
  const [syncStatusMessage, setSyncStatusMessage] = useState<string | null>(null);

  // Pagination State
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalItems, setTotalItems] = useState<number>(0);
  const limit = 10;

  // Selected job for detail dialog
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  // Job postings collection
  const [jobs, setJobs] = useState<Job[]>([]);

  // Cached match scores by jobId
  const [matchScores, setMatchScores] = useState<Record<string, { score: number; recommendation: string }>>({});
  const [minScoreFilter, setMinScoreFilter] = useState<number>(0);

  const loadMatches = useCallback(async () => {
    if (!isAuthenticated) {
      setMatchScores({});
      return;
    }
    try {
      const res = await matchingApi.getMatches({ limit: 100 });
      if (res && res.items) {
        const scoreMap: Record<string, { score: number; recommendation: string }> = {};
        for (const m of res.items) {
          scoreMap[m.job_id] = { score: m.overall_score, recommendation: m.recommendation };
        }
        setMatchScores(scoreMap);
      }
    } catch (err: any) {
      console.warn("Could not load match scores:", err?.message);
    }
  }, [isAuthenticated]);

  const loadJobs = useCallback(async () => {
    if (!isAuthenticated) {
      setJobs([]);
      return;
    }
    setIsLoading(true);
    try {
      const res = await jobsApi.getJobs({
        page: currentPage,
        limit,
        search: searchTerm || undefined,
        apply_preferences: applyPreferences,
      });
      if (res && res.items) {
        setJobs(res.items);
        if (res.pagination) {
          setTotalPages(res.pagination.total_pages || 1);
          setTotalItems(res.pagination.total_items || 0);
        }
      }
    } catch (err: any) {
      console.log("No jobs fetched from API yet:", err?.message);
    } finally {
      setIsLoading(false);
    }
  }, [applyPreferences, currentPage, limit, searchTerm, isAuthenticated]);

  useEffect(() => {
    loadJobs();
    loadMatches();
  }, [loadJobs, loadMatches]);

  const handleSyncJobs = async () => {
    if (!isAuthenticated) {
      setSyncStatusMessage("Please sign in or use Demo Mode to trigger external job sync.");
      setTimeout(() => setSyncStatusMessage(null), 5000);
      return;
    }
    setIsSyncing(true);
    setSyncStatusMessage(null);
    try {
      const res = await jobsApi.syncJobs("arbeitnow");
      setSyncStatusMessage(
        `Sync complete: ${res.new_jobs_inserted} new jobs ingested, ${res.duplicates_skipped} duplicates skipped.`
      );
      setCurrentPage(1);
      await loadJobs();
      await loadMatches();
    } catch (err: any) {
      console.error("Sync error:", err);
      setSyncStatusMessage(err.message || "Failed to sync external jobs from Arbeitnow.");
    } finally {
      setIsSyncing(false);
      setTimeout(() => setSyncStatusMessage(null), 5000);
    }
  };

  const handleOpenDetail = (job: Job) => {
    setSelectedJob(job);
    setIsDetailOpen(true);
  };

  const filteredJobs = jobs.filter((job) => {
    if (minScoreFilter > 0) {
      const match = matchScores[job.id];
      if (!match || match.score < minScoreFilter) return false;
    }
    return (
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (job.tags && job.tags.some((t: string) => t.toLowerCase().includes(searchTerm.toLowerCase())))
    );
  });

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Jobs Discovery & Feed"
        subtitle="Canonical, deduplicated job postings filtered through your deterministic constraints and AI match engine."
      >
        <Button
          variant="outline"
          size="sm"
          onClick={handleSyncJobs}
          disabled={isSyncing}
          className="gap-2 border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300"
        >
          <RefreshCw className={`h-4 w-4 ${isSyncing ? "animate-spin text-violet-400" : ""}`} />
          {isSyncing ? "Syncing Arbeitnow..." : "Sync External Sources"}
        </Button>
      </PageHeader>

      {syncStatusMessage && (
        <div className="p-3 rounded-lg bg-violet-950/40 border border-violet-800/40 text-violet-200 text-xs flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-violet-400" />
          <span>{syncStatusMessage}</span>
        </div>
      )}

      {/* Filter and Preferences Bar */}
      <div className="flex flex-col sm:flex-row gap-3 justify-between items-stretch sm:items-center">
        <div className="relative flex-1">
          <Input
            placeholder="Filter by title, company, or tech keywords (e.g. Python, FastAPI, React)..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="border-zinc-800 bg-zinc-950/60 text-zinc-200 text-xs sm:text-sm"
          />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 bg-zinc-900/60 p-2 px-3 rounded-lg border border-zinc-800 text-xs shrink-0">
            <SlidersHorizontal className="h-3.5 w-3.5 text-zinc-400" />
            <span className="font-medium text-zinc-400">Min Match:</span>
            <select
              value={minScoreFilter}
              onChange={(e) => {
                setMinScoreFilter(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="bg-transparent font-mono text-zinc-200 text-xs focus:outline-none cursor-pointer"
            >
              <option value={0} className="bg-zinc-950">All Scores</option>
              <option value={60} className="bg-zinc-950">&ge; 60%</option>
              <option value={75} className="bg-zinc-950">&ge; 75%</option>
              <option value={85} className="bg-zinc-950">&ge; 85%</option>
            </select>
          </div>
          <div className="flex items-center gap-3 bg-zinc-900/60 p-2 px-3 rounded-lg border border-zinc-800 text-xs shrink-0">
            <span className="font-medium text-zinc-300">Apply Stored Preferences</span>
            <Switch
              checked={applyPreferences}
              onCheckedChange={(checked) => {
                setApplyPreferences(checked);
                setCurrentPage(1);
              }}
            />
          </div>
        </div>
      </div>

      {/* Jobs Collection */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="p-12 text-center text-zinc-400 flex flex-col items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin text-violet-400" />
            <span className="text-xs font-mono">Loading paginated job postings...</span>
          </div>
        ) : !isAuthenticated ? (
          <Card className="p-8 text-center glass-card border-dashed border-zinc-800 bg-zinc-950/40 space-y-4">
            <div className="h-10 w-10 rounded-xl bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400 mx-auto">
              <Briefcase className="h-5 w-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-zinc-200">Candidate Session Required</h3>
              <p className="text-xs text-zinc-400 max-w-md mx-auto">
                Sign in with your candidate account or launch One-Click Demo Mode to view deduplicated jobs, apply deterministic filtering, and run AI compatibility assessments.
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
        ) : filteredJobs.length === 0 ? (
          <Card className="p-8 text-center glass-card border-dashed border-zinc-800 bg-zinc-950/40 space-y-3">
            <div className="h-10 w-10 rounded-xl bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400 mx-auto">
              <Briefcase className="h-5 w-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-zinc-200">No Job Postings Available</h3>
              <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                {searchTerm
                  ? `No jobs match "${searchTerm}". Try broadening your search or clear filters.`
                  : "No postings found in database. Click 'Sync External Sources' to ingest normalized jobs from Arbeitnow."}
              </p>
            </div>
            {!searchTerm && (
              <Button size="sm" variant="outline" onClick={handleSyncJobs} disabled={isSyncing} className="text-xs gap-1.5 mt-2 border-zinc-800 bg-zinc-900 text-zinc-300">
                <RefreshCw className={`h-3.5 w-3.5 ${isSyncing ? "animate-spin" : ""}`} />
                Sync External Postings
              </Button>
            )}
          </Card>
        ) : (
          filteredJobs.map((job) => (
            <Card
              key={job.id}
              className="glass-card border-zinc-800/80 bg-zinc-950/70 hover:border-violet-500/40 transition-all duration-200 cursor-pointer group"
              onClick={() => handleOpenDetail(job)}
            >
              <CardHeader className="pb-3">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <CardTitle className="text-base font-semibold text-zinc-100 group-hover:text-violet-300 transition-colors">
                        {job.title}
                      </CardTitle>
                      {job.remote && (
                        <Badge variant="secondary" className="text-[11px] font-normal bg-zinc-900 text-zinc-300 border border-zinc-800">
                          🌎 Remote
                        </Badge>
                      )}
                      {matchScores[job.id] && (
                        <Badge
                          variant="outline"
                          className={`text-[11px] font-mono font-medium ${
                            matchScores[job.id].score >= 80
                              ? "border-emerald-500/40 text-emerald-400 bg-emerald-950/40"
                              : matchScores[job.id].score >= 60
                              ? "border-amber-500/40 text-amber-400 bg-amber-950/40"
                              : "border-zinc-700 text-zinc-400 bg-zinc-900/40"
                          }`}
                        >
                          <Sparkles className="h-3 w-3 mr-1 inline text-violet-400" />
                          {matchScores[job.id].score}% Match
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="flex items-center gap-3 text-xs font-medium text-zinc-400">
                      <span className="flex items-center gap-1 text-zinc-300">
                        <Building className="h-3.5 w-3.5 text-zinc-400" />
                        {job.company_name}
                      </span>
                      <span>&bull;</span>
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-zinc-400" />
                        {job.location}
                      </span>
                    </CardDescription>
                  </div>

                  <div className="flex items-center gap-2 shrink-0" onClick={(e) => e.stopPropagation()}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleOpenDetail(job)}
                      className="text-xs border-zinc-800 bg-zinc-900/80 hover:bg-violet-950/40 hover:border-violet-500/40 text-zinc-200 gap-1.5 h-8"
                    >
                      <Sparkles className="h-3.5 w-3.5 text-violet-400" />
                      <span>Assess & Tailor</span>
                    </Button>

                    {job.url && (
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-200 transition-colors border border-zinc-800 px-2.5 py-1.5 rounded-md h-8"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-xs text-zinc-400 line-clamp-2 leading-relaxed">{job.description}</p>
                <div className="flex flex-wrap gap-1.5">
                  {job.job_types?.map((type: string) => (
                    <Badge key={type} variant="outline" className="text-[11px] border-zinc-800 text-zinc-300">
                      {type}
                    </Badge>
                  ))}
                  {job.tags?.map((tag: string) => (
                    <Badge key={tag} variant="secondary" className="text-[11px] font-mono bg-zinc-900 text-zinc-400 border border-zinc-800/60">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between p-3 rounded-xl border border-zinc-800 bg-zinc-950/60 text-xs font-mono text-zinc-400">
          <div>
            Showing Page <span className="font-semibold text-zinc-200">{currentPage}</span> of{" "}
            <span className="font-semibold text-zinc-200">{totalPages}</span> ({totalItems} total postings)
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage <= 1 || isLoading}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="h-8 px-2.5 text-xs border-zinc-800 bg-zinc-900 text-zinc-300 disabled:opacity-40"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Previous</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              disabled={currentPage >= totalPages || isLoading}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="h-8 px-2.5 text-xs border-zinc-800 bg-zinc-900 text-zinc-300 disabled:opacity-40"
            >
              <span>Next</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      )}

      {/* Full Detail & Actions Dialog */}
      <JobDetailDialog
        job={selectedJob}
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        onMatchUpdated={(jobId, match) => {
          if (match) {
            setMatchScores((prev) => ({
              ...prev,
              [jobId]: { score: match.overall_score, recommendation: match.recommendation },
            }));
          }
        }}
      />
    </div>
  );
}
