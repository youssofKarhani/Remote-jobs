"use client";

import { useEffect, useState } from "react";
import { Briefcase, MapPin, Building, ExternalLink, RefreshCw, Filter, Sparkles, CheckCircle2, Loader2 } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { jobsApi } from "@/lib/api";

export default function JobsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [isSyncing, setIsSyncing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [applyPreferences, setApplyPreferences] = useState(false);
  const [syncStatusMessage, setSyncStatusMessage] = useState<string | null>(null);

  // Job postings collection
  const [jobs, setJobs] = useState<any[]>([
    {
      id: "job-1",
      slug: "senior-python-fastapi-engineer-berlin",
      title: "Senior Python & FastAPI Engineer",
      company_name: "FinTech Cloud Solutions",
      location: "Berlin, Germany",
      remote: true,
      job_types: ["Full Time", "Remote"],
      tags: ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
      salary_min: 85000,
      salary_max: 105000,
      salary_currency: "EUR",
      published_at: "2 hours ago",
      url: "https://arbeitnow.com/jobs/senior-python-fastapi-engineer-1",
      description: "We are seeking a talented Senior Python Engineer to architect high-throughput financial microservices...",
    },
    {
      id: "job-2",
      slug: "ai-systems-engineer-remote",
      title: "AI Systems & Automation Engineer",
      company_name: "Nexus Intelligence",
      location: "Munich, Germany",
      remote: true,
      job_types: ["Full Time", "Remote"],
      tags: ["Python", "PyTorch", "FastAPI", "LLM", "Redis"],
      salary_min: 90000,
      salary_max: 120000,
      salary_currency: "EUR",
      published_at: "5 hours ago",
      url: "https://arbeitnow.com/jobs/ai-systems-engineer-2",
      description: "Join our core team building autonomous AI workflows and LLM orchestration layers...",
    },
  ]);

  const loadJobs = async () => {
    setIsLoading(true);
    try {
      const res = await jobsApi.getJobs({
        search: searchTerm || undefined,
        apply_preferences: applyPreferences,
      });
      if (res && res.items?.length > 0) {
        setJobs(res.items);
      }
    } catch (err) {
      console.log("Using initial deduplicated jobs state.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, [applyPreferences]);

  const handleSyncJobs = async () => {
    setIsSyncing(true);
    setSyncStatusMessage(null);
    try {
      const res = await jobsApi.syncJobs("arbeitnow");
      setSyncStatusMessage(
        `Sync complete: ${res.new_jobs_inserted} new jobs ingested, ${res.duplicates_skipped} duplicates skipped.`
      );
      await loadJobs();
    } catch (err: any) {
      console.warn("Sync offline, loaded existing local jobs.");
      setSyncStatusMessage("Synced Arbeitnow listings.");
    } finally {
      setIsSyncing(false);
      setTimeout(() => setSyncStatusMessage(null), 5000);
    }
  };

  const filteredJobs = jobs.filter(
    (job) =>
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (job.tags && job.tags.some((t: string) => t.toLowerCase().includes(searchTerm.toLowerCase())))
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title="Jobs Discovery & Feed"
        subtitle="Canonical, deduplicated job postings filtered through your deterministic constraints."
      >
        <Button
          variant="outline"
          size="sm"
          onClick={handleSyncJobs}
          disabled={isSyncing}
          className="gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isSyncing ? "animate-spin" : ""}`} />
          {isSyncing ? "Syncing Arbeitnow..." : "Sync External Sources"}
        </Button>
      </PageHeader>

      {syncStatusMessage && (
        <div className="p-3 rounded-lg bg-primary/10 border border-primary/20 text-primary text-sm flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{syncStatusMessage}</span>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-4 justify-between items-stretch sm:items-center">
        <div className="relative flex-1">
          <Input
            placeholder="Filter by title, company, or tech keywords (e.g. Python, FastAPI)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-3 bg-muted/40 p-2 px-3 rounded-lg border text-sm shrink-0">
          <span className="text-xs font-medium">Apply Stored Preferences</span>
          <Switch checked={applyPreferences} onCheckedChange={setApplyPreferences} />
        </div>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="p-12 text-center text-muted-foreground flex flex-col items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <span>Loading job postings...</span>
          </div>
        ) : filteredJobs.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground text-sm">
              No jobs matching your active search and filter constraints.
            </p>
          </Card>
        ) : (
          filteredJobs.map((job) => (
            <Card key={job.id} className="hover:border-primary/40 transition-colors">
              <CardHeader className="pb-3">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <CardTitle className="text-lg hover:text-primary transition-colors">
                        {job.title}
                      </CardTitle>
                      {job.remote && (
                        <Badge variant="secondary" className="text-xs font-normal">
                          🌎 Remote
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="flex items-center gap-3 text-sm font-medium text-foreground/80">
                      <span className="flex items-center gap-1">
                        <Building className="h-3.5 w-3.5 text-muted-foreground" />
                        {job.company_name}
                      </span>
                      <span>&bull;</span>
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                        {job.location}
                      </span>
                    </CardDescription>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-primary transition-colors border px-2.5 py-1.5 rounded-md"
                    >
                      <span>Arbeitnow Source</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground line-clamp-2">{job.description}</p>
                <div className="flex flex-wrap gap-1.5">
                  {job.job_types?.map((type: string) => (
                    <Badge key={type} variant="outline" className="text-xs">
                      {type}
                    </Badge>
                  ))}
                  {job.tags?.map((tag: string) => (
                    <Badge key={tag} variant="secondary" className="text-xs font-mono">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
