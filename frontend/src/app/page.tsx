import Link from "next/link";
import { ArrowRight, Sparkles, ShieldCheck, Terminal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DeconstructionVisual } from "@/components/home/deconstruction-visual";
import { PipelineTimeline } from "@/components/home/pipeline-timeline";
import { CoreGuaranteeBanner } from "@/components/home/core-guarantee-banner";
import { ArchitectureDialog } from "@/components/home/architecture-dialog";

export default function HomePage() {
  return (
    <div className="space-y-16 md:space-y-24 py-6 md:py-12">
      
      {/* PREVIOUS HERO SECTION (Bold Gradient Title, Anti-Hallucination Tag & Glowing CTAs) */}
      <section className="text-center space-y-8 max-w-4xl mx-auto pt-4 md:pt-8 px-4">
        
        {/* Anti-Hallucination Tag */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-mono font-medium bg-blue-950/60 text-blue-400 border border-blue-800/40 shadow-sm">
          <ShieldCheck className="h-4 w-4 text-blue-400" />
          <span>Deterministic Anti-Hallucination Architecture</span>
        </div>

        {/* H1 Headline with Vibrant Gradient */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-zinc-100 leading-[1.1]">
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
      </section>

      {/* SECTION 2: THE CORE CONCEPT VISUAL ("The Deconstruction") */}
      <DeconstructionVisual />

      {/* SECTION 3: THE AUTOMATED PIPELINE (Step-by-Step Animated Timeline) */}
      <PipelineTimeline />

      {/* SECTION 4: THE CORE GUARANTEE (Footer Callout Banner) */}
      <CoreGuaranteeBanner />

    </div>
  );
}
