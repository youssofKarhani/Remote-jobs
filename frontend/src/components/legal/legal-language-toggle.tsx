"use client";

import React from "react";
import { useLegalLanguage } from "./legal-context";
import { cn } from "@/lib/utils";

interface LegalLanguageToggleProps {
  className?: string;
}

export function LegalLanguageToggle({ className }: LegalLanguageToggleProps) {
  const { language, setLanguage } = useLegalLanguage();

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-lg bg-zinc-900/90 border border-zinc-800/90 p-0.5 text-xs font-mono shrink-0",
        className
      )}
    >
      <button
        type="button"
        onClick={() => setLanguage("en")}
        className={cn(
          "px-2.5 py-1 rounded-md transition-all text-xs font-medium",
          language === "en"
            ? "bg-violet-600 text-white font-semibold shadow-sm"
            : "text-zinc-400 hover:text-zinc-200"
        )}
        aria-pressed={language === "en"}
        title="English"
      >
        EN
      </button>

      <button
        type="button"
        onClick={() => setLanguage("de")}
        className={cn(
          "px-2.5 py-1 rounded-md transition-all text-xs font-medium",
          language === "de"
            ? "bg-violet-600 text-white font-semibold shadow-sm"
            : "text-zinc-400 hover:text-zinc-200"
        )}
        aria-pressed={language === "de"}
        title="Deutsch"
      >
        DE
      </button>
    </div>
  );
}
