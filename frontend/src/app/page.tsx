import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DeconstructionVisual } from "@/components/home/deconstruction-visual";
import { PipelineTimeline } from "@/components/home/pipeline-timeline";
import { CoreGuaranteeBanner } from "@/components/home/core-guarantee-banner";
import { ArchitectureDialog } from "@/components/home/architecture-dialog";

export default function HomePage() {
  return (
    <div className="space-y-16 md:space-y-24 py-8 md:py-16">
      
      {/* SECTION 1: THE HERO (Maximal Impact, Minimal Text) */}
      <section className="text-center space-y-8 max-w-4xl mx-auto pt-6 md:pt-12 px-4">
        
        {/* H1 Headline */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-light tracking-tight text-zinc-100 leading-[1.15]">
          Upload your raw experience.{" "}
          <span className="font-normal text-white">
            We engineer the perfect application.
          </span>
        </h1>

        {/* H2 Sub-Headline */}
        <p className="text-base sm:text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto font-light leading-relaxed">
          Connect your profile to our automated pipeline to discover high-match roles and generate highly tailored, verifiable applications on autopilot.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link href="/cv-upload" className="w-full sm:w-auto">
            <Button
              size="lg"
              className="w-full sm:w-auto h-12 px-8 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-lg shadow-indigo-600/20 hover:shadow-indigo-600/30 transition-all duration-300 gap-2 text-sm"
            >
              <Sparkles className="h-4 w-4" />
              Initialize Platform
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>

          <ArchitectureDialog>
            <Button
              size="lg"
              variant="ghost"
              className="w-full sm:w-auto h-12 px-6 rounded-full text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/60 font-light text-sm transition-colors"
            >
              Read the Architecture
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

