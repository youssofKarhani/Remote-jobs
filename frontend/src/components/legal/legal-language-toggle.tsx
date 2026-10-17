"use client";

import React from "react";
import { Globe } from "lucide-react";
import { useLegalLanguage } from "./legal-context";
import { cn } from "@/lib/utils";

interface LegalLanguageToggleProps {
  className?: string;
  compact?: boolean;
}

export function LegalLanguageToggle({ className, compact = false }: LegalLanguageToggleProps) {
  const { language, setLanguage } = useLegalLanguage();

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 p-1 rounded-xl bg-zinc-900/90 border border-zinc-800 shadow-inner backdrop-blur-sm",
        className
      )}
    >
      <div className="flex items-center gap-1.5 pl-2 pr-1 text-zinc-400 text-xs font-mono">
        <Globe className="h-3.5 w-3.5 text-violet-400" />
        {!compact && <span className="text-[11px] uppercase tracking-wider text-zinc-400 font-semibold">Language</span>}
      </div>

      <div className="inline-flex rounded-lg bg-zinc-950/80 p-0.5 border border-zinc-800/80">
        <button
          type="button"
          onClick={() => setLanguage("en")}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all duration-200",
            language === "en"
              ? "bg-violet-600 text-white font-semibold shadow-sm shadow-violet-600/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
          )}
          aria-pressed={language === "en"}
        >
          <span className="font-mono text-[11px] font-bold">EN</span>
          <span>English</span>
          <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-black/20 text-violet-200 border border-violet-400/20">
            Default
          </span>
        </button>

        <button
          type="button"
          onClick={() => setLanguage("de")}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all duration-200",
            language === "de"
              ? "bg-violet-600 text-white font-semibold shadow-sm shadow-violet-600/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
          )}
          aria-pressed={language === "de"}
        >
          <span className="font-mono text-[11px] font-bold">DE</span>
          <span>Deutsch</span>
        </button>
      </div>
    </div>
  );
}
