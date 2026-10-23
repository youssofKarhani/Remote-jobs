"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { ArrowRight, CornerDownLeft, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TargetStepProps {
  initialValue: string;
  onComplete: (role: string) => void;
}

const SUGGESTED_ROLES = [
  "Automation Engineer",
  "Staff Backend Engineer",
  "AI Platform Engineer",
  "Full Stack Architect",
  "DevOps & Infrastructure Lead",
];

export function TargetStep({ initialValue, onComplete }: TargetStepProps) {
  const [role, setRole] = useState(initialValue || "");
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Autofocus input on step mount
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = role.trim();
    if (!trimmed) {
      setError("Please specify your target role to proceed.");
      return;
    }
    setError(null);
    onComplete(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-3xl mx-auto w-full py-8 md:py-16 text-center space-y-12"
    >
      {/* Step Badge */}
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-zinc-900 border border-zinc-800 text-zinc-400">
        <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
        Step 01 &bull; Intent Discovery
      </div>

      {/* Massive Headline Prompt */}
      <div className="space-y-3">
        <h2 className="text-3xl sm:text-4xl md:text-5xl font-light tracking-tight text-zinc-100">
          What is your target role?
        </h2>
        <p className="text-sm md:text-base text-zinc-400 font-light max-w-lg mx-auto">
          We will align your verified experience to curate tailored applications specifically for this domain.
        </p>
      </div>

      {/* Massive Autofocus Input */}
      <form onSubmit={handleSubmit} className="relative max-w-2xl mx-auto space-y-4">
        <div className="relative group">
          <input
            ref={inputRef}
            type="text"
            value={role}
            onChange={(e) => {
              setRole(e.target.value);
              if (error) setError(null);
            }}
            onKeyDown={handleKeyDown}
            placeholder="e.g. Automation Engineer"
            className="w-full text-2xl sm:text-3xl md:text-4xl text-center bg-transparent border-b-2 border-zinc-800 focus:border-violet-500 outline-none pb-4 text-zinc-100 placeholder:text-zinc-700 transition-colors font-light selection:bg-violet-600/30"
          />
          {/* Subtle bottom glow line on focus */}
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-violet-500 to-transparent opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />
        </div>

        {error && (
          <p className="text-xs text-rose-400 font-sans text-center animate-fade-in">
            {error}
          </p>
        )}

        {/* Enter key shortcut helper */}
        <div className="flex items-center justify-center gap-2 text-xs text-zinc-400 font-mono pt-2">
          <span>Press</span>
          <kbd className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-300 flex items-center gap-1 text-[11px]">
            <span>Enter</span>
            <CornerDownLeft className="w-3 h-3 text-violet-400" />
          </kbd>
          <span>to continue</span>
        </div>
      </form>

      {/* Quick Suggested Role Chips */}
      <div className="pt-4 space-y-3">
        <span className="text-xs font-mono uppercase tracking-wider text-zinc-400 block">
          Quick Suggestions
        </span>
        <div className="flex flex-wrap justify-center gap-2">
          {SUGGESTED_ROLES.map((suggested) => (
            <button
              key={suggested}
              type="button"
              onClick={() => {
                setRole(suggested);
                setError(null);
              }}
              className={`px-3.5 py-1.5 rounded-full text-xs font-sans transition-all duration-200 border ${
                role === suggested
                  ? "bg-violet-950/60 border-violet-500/60 text-violet-200 shadow-sm"
                  : "bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
              }`}
            >
              {suggested}
            </button>
          ))}
        </div>
      </div>

      {/* Action CTA */}
      <div className="pt-6">
        <Button
          size="lg"
          onClick={() => handleSubmit()}
          disabled={!role.trim()}
          className="h-12 px-8 rounded-full bg-violet-600 hover:bg-violet-500 text-white font-medium shadow-[0_0_25px_rgba(139,92,246,0.35)] disabled:opacity-40 disabled:pointer-events-none transition-all duration-300 gap-2 text-sm"
        >
          <span>Continue to CV Ingestion</span>
          <ArrowRight className="w-4 h-4" />
        </Button>
      </div>

    </motion.div>
  );
}
