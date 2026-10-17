"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Scale, Lock, FileText, ShieldCheck } from "lucide-react";
import { LegalLanguageToggle } from "./legal-language-toggle";
import { useLegalLanguage } from "./legal-context";
import { cn } from "@/lib/utils";

interface LegalHeaderProps {
  badgeTextEn: string;
  badgeTextDe: string;
  titleEn: string;
  titleDe: string;
  descriptionEn: string;
  descriptionDe: string;
  lawReferences?: Array<{
    code: string;
    url: string;
    title: string;
  }>;
}

const LEGAL_PAGES = [
  {
    href: "/impressum",
    labelEn: "Imprint",
    labelDe: "Impressum",
    icon: Scale,
  },
  {
    href: "/privacy",
    labelEn: "Privacy",
    labelDe: "Datenschutz",
    icon: Lock,
  },
  {
    href: "/terms",
    labelEn: "Terms",
    labelDe: "AGB",
    icon: FileText,
  },
  {
    href: "/ethics",
    labelEn: "AI Ethics",
    labelDe: "KI-Ethik",
    icon: ShieldCheck,
  },
];

export function LegalHeader({
  badgeTextEn,
  badgeTextDe,
  titleEn,
  titleDe,
  descriptionEn,
  descriptionDe,
}: LegalHeaderProps) {
  const pathname = usePathname();
  const { language } = useLegalLanguage();

  const isEn = language === "en";

  return (
    <div className="space-y-6 border-b border-zinc-800/80 pb-6">
      {/* Top Bar with Navigation Tabs and Language Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Navigation Tabs */}
        <nav className="inline-flex items-center gap-1 p-1 rounded-lg bg-zinc-900/80 border border-zinc-800/80 overflow-x-auto max-w-full">
          {LEGAL_PAGES.map((page) => {
            const Icon = page.icon;
            const isActive = pathname === page.href;
            return (
              <Link
                key={page.href}
                href={page.href}
                className={cn(
                  "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all whitespace-nowrap",
                  isActive
                    ? "bg-violet-600 text-white font-semibold shadow-sm"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
                )}
              >
                <Icon className={cn("h-3.5 w-3.5", isActive ? "text-white" : "text-violet-400")} />
                <span>{isEn ? page.labelEn : page.labelDe}</span>
              </Link>
            );
          })}
        </nav>

        {/* Compact Language Toggle */}
        <LegalLanguageToggle />
      </div>

      {/* Title & Description */}
      <div className="space-y-2 pt-1">
        <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full text-xs font-mono bg-violet-950/40 text-violet-400 border border-violet-800/40">
          <span>{isEn ? badgeTextEn : badgeTextDe}</span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-zinc-100">
          {isEn ? titleEn : titleDe}
        </h1>

        <p className="text-sm text-zinc-400 max-w-3xl leading-relaxed">
          {isEn ? descriptionEn : descriptionDe}
        </p>
      </div>

      {/* Serious Jurisdiction Bar */}
      <div className="flex items-center justify-between text-xs text-zinc-500 font-mono pt-1 border-t border-zinc-800/40">
        <span>
          {isEn
            ? "Jurisdiction: Kirchhain, Hesse, Germany (EU)"
            : "Gerichtsstand: Kirchhain, Hessen, Deutschland (EU)"}
        </span>
        <span>
          {isEn ? "Authoritative text: German" : "Rechtsverbindliche Fassung: Deutsch"}
        </span>
      </div>
    </div>
  );
}
