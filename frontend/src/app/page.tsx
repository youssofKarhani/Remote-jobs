import Link from "next/link";
import { ArrowRight, CheckCircle2, ShieldCheck, Database, Sliders, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div className="text-center space-y-4 py-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary mb-2">
          <ShieldCheck className="h-4 w-4" />
          Deterministic Anti-Hallucination Architecture
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
          AI Job Application & Discovery Platform
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Canonical candidate profiles with immutable evidence identifiers, deterministic job filtering, and multi-source job ingestion.
        </p>
        <div className="flex flex-wrap justify-center gap-4 pt-4">
          <Link href="/cv-upload">
            <Button size="lg" className="gap-2">
              Upload CV & Ingest Evidence
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/jobs">
            <Button size="lg" variant="outline" className="gap-2">
              Browse Normalized Jobs
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 pt-6">
        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader className="space-y-1">
            <Database className="h-8 w-8 text-primary mb-2" />
            <CardTitle className="text-lg">1. CV Ingestion</CardTitle>
            <CardDescription>
              Extract structured profile data from PDF/DOCX or plain text.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/cv-upload" className="text-sm font-medium text-primary hover:underline flex items-center gap-1">
              Start Ingestion &rarr;
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader className="space-y-1">
            <ShieldCheck className="h-8 w-8 text-emerald-500 mb-2" />
            <CardTitle className="text-lg">2. Evidence Bank</CardTitle>
            <CardDescription>
              Manage verified achievements with immutable stable IDs (e.g. EXP_001).
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/profile" className="text-sm font-medium text-primary hover:underline flex items-center gap-1">
              Manage Evidence &rarr;
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader className="space-y-1">
            <Sliders className="h-8 w-8 text-amber-500 mb-2" />
            <CardTitle className="text-lg">3. Preferences</CardTitle>
            <CardDescription>
              Configure zero-cost deterministic filters before LLM evaluation.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/preferences" className="text-sm font-medium text-primary hover:underline flex items-center gap-1">
              Configure Rules &rarr;
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader className="space-y-1">
            <Briefcase className="h-8 w-8 text-indigo-500 mb-2" />
            <CardTitle className="text-lg">4. Jobs Discovery</CardTitle>
            <CardDescription>
              Deduplicated job postings normalized from multiple sources.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/jobs" className="text-sm font-medium text-primary hover:underline flex items-center gap-1">
              View Feed &rarr;
            </Link>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-muted/40 border-dashed">
        <CardContent className="pt-6 space-y-2">
          <h3 className="font-semibold text-sm uppercase tracking-wide text-muted-foreground">Architectural Invariant</h3>
          <p className="text-sm text-foreground italic">
            &ldquo;LLMs may decide which verified evidence is relevant. They may not decide what evidence exists.&rdquo;
          </p>
          <div className="flex items-center gap-4 pt-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> 12 Canonical Tables</span>
            <span className="flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> PostgreSQL & Alembic</span>
            <span className="flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> Next.js App Router</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
