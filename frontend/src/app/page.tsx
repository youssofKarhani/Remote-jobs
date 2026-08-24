import Link from "next/link";
import {
  ArrowRight,
  ShieldCheck,
  Database,
  Sliders,
  Briefcase,
  Sparkles,
  User,
  Terminal,
  CheckCircle2,
  Lock,
  Layers,
  FileCheck2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { HeroCodeGraphic } from "@/components/home/hero-code-graphic";
import { HowItWorksBento } from "@/components/home/how-it-works-bento";
import { ArchitectureDialog } from "@/components/home/architecture-dialog";

export default function HomePage() {
  return (
    <div className="space-y-16 md:space-y-24 py-4 md:py-8">
      {/* Hero Section */}
      <section className="text-center space-y-8 max-w-4xl mx-auto pt-4 md:pt-8">
        
        {/* Anti-Hallucination Tag */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-mono font-medium bg-blue-950/60 text-blue-400 border border-blue-800/40 shadow-sm">
          <ShieldCheck className="h-4 w-4 text-blue-400" />
          <span>Deterministic Anti-Hallucination Architecture</span>
        </div>

        {/* H1 Headline */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-zinc-100 leading-[1.1]">
          Upload your raw experience.{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400">
            We engineer the perfect application.
          </span>
        </h1>

        {/* H2 Sub-Headline */}
        <p className="text-base sm:text-lg md:text-xl text-zinc-400 max-w-3xl mx-auto font-sans leading-relaxed">
          Stop manually tweaking resumes. Connect your profile to our automated pipeline to discover high-match roles and generate highly tailored, verifiable application assets on autopilot.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <Link href="/cv-upload" className="w-full sm:w-auto">
            <Button
              size="lg"
              className="w-full sm:w-auto h-12 px-8 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all duration-300 gap-2.5 text-sm"
            >
              <Sparkles className="h-4 w-4" />
              Initialize Platform
              <ArrowRight className="h-4 w-4 ml-0.5" />
            </Button>
          </Link>

          <ArchitectureDialog>
            <Button
              size="lg"
              variant="outline"
              className="w-full sm:w-auto h-12 px-7 rounded-xl border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800/80 text-zinc-300 font-mono text-xs gap-2 transition-colors"
            >
              <Terminal className="h-4 w-4 text-blue-400" />
              Read the Architecture.md
            </Button>
          </ArchitectureDialog>
        </div>

        {/* Hero Code Window Visual */}
        <div className="pt-8 md:pt-12">
          <HeroCodeGraphic />
        </div>
      </section>

      {/* Bento Box: How It Works */}
      <HowItWorksBento />

      {/* Platform Navigation & Quick Action Grid */}
      <section className="space-y-6 pt-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div>
            <h3 className="text-xl font-bold text-zinc-100">Interactive Application Modules</h3>
            <p className="text-xs text-zinc-400">Direct endpoints into the live candidate pipeline</p>
          </div>
          <span className="text-xs font-mono text-zinc-500">PostgreSQL &bull; FastAPI &bull; Next.js</span>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href="/cv-upload" className="group">
            <Card className="h-full glass-card glass-card-hover border-zinc-800/80 bg-zinc-950/60 p-5 space-y-3">
              <div className="h-9 w-9 rounded-lg bg-blue-950/60 border border-blue-800/40 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                <Database className="h-4 w-4" />
              </div>
              <div>
                <CardTitle className="text-sm font-bold text-zinc-200 group-hover:text-blue-400 transition-colors">
                  1. CV Ingestion
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400 mt-1">
                  Upload PDF/DOCX or paste raw resume text for structured entity extraction.
                </CardDescription>
              </div>
              <div className="text-xs font-mono text-blue-400 flex items-center gap-1 pt-1">
                Upload Document &rarr;
              </div>
            </Card>
          </Link>

          <Link href="/profile" className="group">
            <Card className="h-full glass-card glass-card-hover border-zinc-800/80 bg-zinc-950/60 p-5 space-y-3">
              <div className="h-9 w-9 rounded-lg bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                <User className="h-4 w-4" />
              </div>
              <div>
                <CardTitle className="text-sm font-bold text-zinc-200 group-hover:text-emerald-400 transition-colors">
                  2. Evidence Bank
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400 mt-1">
                  Manage verifiable achievements, bullets, and skills with immutable stable IDs.
                </CardDescription>
              </div>
              <div className="text-xs font-mono text-emerald-400 flex items-center gap-1 pt-1">
                Verify Evidence &rarr;
              </div>
            </Card>
          </Link>

          <Link href="/preferences" className="group">
            <Card className="h-full glass-card glass-card-hover border-zinc-800/80 bg-zinc-950/60 p-5 space-y-3">
              <div className="h-9 w-9 rounded-lg bg-amber-950/60 border border-amber-800/40 flex items-center justify-center text-amber-400 group-hover:scale-110 transition-transform">
                <Sliders className="h-4 w-4" />
              </div>
              <div>
                <CardTitle className="text-sm font-bold text-zinc-200 group-hover:text-amber-400 transition-colors">
                  3. Preferences
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400 mt-1">
                  Configure deterministic zero-cost pre-filtering rules and role constraints.
                </CardDescription>
              </div>
              <div className="text-xs font-mono text-amber-400 flex items-center gap-1 pt-1">
                Set Non-Negotiables &rarr;
              </div>
            </Card>
          </Link>

          <Link href="/jobs" className="group">
            <Card className="h-full glass-card glass-card-hover border-zinc-800/80 bg-zinc-950/60 p-5 space-y-3">
              <div className="h-9 w-9 rounded-lg bg-purple-950/60 border border-purple-800/40 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                <Briefcase className="h-4 w-4" />
              </div>
              <div>
                <CardTitle className="text-sm font-bold text-zinc-200 group-hover:text-purple-400 transition-colors">
                  4. Jobs Feed
                </CardTitle>
                <CardDescription className="text-xs text-zinc-400 mt-1">
                  Explore deduplicated, normalized multi-source job postings in real time.
                </CardDescription>
              </div>
              <div className="text-xs font-mono text-purple-400 flex items-center gap-1 pt-1">
                Browse Feed &rarr;
              </div>
            </Card>
          </Link>
        </div>
      </section>

      {/* Architectural Invariant Banner */}
      <section className="rounded-2xl border border-zinc-800/90 bg-gradient-to-br from-zinc-900/80 via-zinc-950/90 to-blue-950/20 p-6 md:p-8 relative overflow-hidden glass-card">
        <div className="absolute -right-12 -bottom-12 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="space-y-4 relative z-10">
          <div className="flex items-center gap-2 text-xs font-mono font-semibold uppercase tracking-wider text-blue-400">
            <ShieldCheck className="h-4 w-4" />
            Core Architectural Invariant
          </div>

          <blockquote className="text-base md:text-lg font-medium text-zinc-200 italic border-l-2 border-blue-500 pl-4">
            &ldquo;LLMs may decide which verified evidence is relevant. They may never decide what evidence exists.&rdquo;
          </blockquote>

          <div className="flex flex-wrap items-center gap-4 md:gap-6 pt-2 text-xs font-mono text-zinc-400">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              12 Canonical Tables
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              Zero-Hallucination Set Gate
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              PostgreSQL &bull; FastAPI &bull; Next.js 16
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}
