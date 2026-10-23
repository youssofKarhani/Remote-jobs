import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CoreConceptAnimation } from "@/components/home/core-concept-animation";
import { PipelineTimeline } from "@/components/home/pipeline-timeline";
import { CoreGuaranteeBanner } from "@/components/home/core-guarantee-banner";
import { ArchitectureDialog } from "@/components/home/architecture-dialog";
import { FloatingPipelineSchedule } from "@/components/layout/pipeline-schedule-dialog";

export default function HomePage() {
  return (
    <div className="space-y-24 md:space-y-36 py-12 md:py-24">
      {/* 1. HERO SECTION (Dead-center alignment with massive surrounding whitespace) */}
      <section className="text-center space-y-10 max-w-4xl mx-auto pt-8 md:pt-16 px-4">
        {/* Anti-Hallucination Pill Tag */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-mono font-medium bg-violet-950/40 text-violet-400 border border-violet-800/40 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
          <span>Deterministic Anti-Hallucination Architecture</span>
        </div>

        {/* H1 Headline with subtle text gradient on "perfect application" */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-normal tracking-tight text-zinc-100 leading-[1.12]">
          Upload your raw experience.{" "}
          <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-indigo-300 to-purple-400">
            We engineer the perfect application.
          </span>
        </h1>

        {/* H2 Sub-Headline */}
        <p className="text-base sm:text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto font-sans font-normal leading-relaxed">
          Connect your profile to our automated pipeline to discover high-match roles and generate highly tailored, verifiable applications on autopilot.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          {/* Primary: Solid accent background, pill shape */}
          <Link href="/onboarding" className="w-full sm:w-auto">
            <Button
              size="lg"
              className="w-full sm:w-auto h-12 px-8 rounded-full bg-violet-600 hover:bg-violet-500 text-white font-medium shadow-[0_0_25px_rgba(139,92,246,0.35)] hover:shadow-[0_0_35px_rgba(139,92,246,0.5)] transition-all duration-300 gap-2.5 text-sm"
            >
              <Sparkles className="h-4 w-4" />
              <span>Initialize Platform</span>
            </Button>
          </Link>

          {/* Secondary: Ghost button with a right arrow icon */}
          <ArchitectureDialog>
            <Button
              size="lg"
              variant="ghost"
              className="w-full sm:w-auto h-12 px-7 rounded-full border border-zinc-800 bg-transparent hover:bg-zinc-900 text-zinc-300 hover:text-zinc-100 text-sm font-normal gap-2 transition-colors"
            >
              <span>Read the Architecture</span>
              <ArrowRight className="h-4 w-4 text-violet-400" />
            </Button>
          </ArchitectureDialog>
        </div>
      </section>

      {/* 2. CORE CONCEPT ANIMATION (Framer Motion looping micro-animation) */}
      <CoreConceptAnimation />

      {/* 3. ANIMATED "HOW IT WORKS" TIMELINE */}
      <PipelineTimeline />

      {/* 4. FOOTER CALLOUT (Sleek full-width Geist Mono banner) */}
      <CoreGuaranteeBanner />

      {/* Floating Next AI Batch Run Bubble */}
      <FloatingPipelineSchedule />
    </div>
  );
}
