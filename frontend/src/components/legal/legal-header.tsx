"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Scale, Lock, FileText, ShieldCheck, AlertCircle, ExternalLink } from "lucide-react";
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
    labelEn: "Legal Notice (Imprint)",
    labelDe: "Impressum (§ 5 DDG)",
    icon: Scale,
  },
  {
    href: "/privacy",
    labelEn: "Privacy Policy",
    labelDe: "Datenschutz (DSGVO)",
    icon: Lock,
  },
  {
    href: "/terms",
    labelEn: "Terms of Service",
    labelDe: "Nutzungsbedingungen (AGB)",
    icon: FileText,
  },
  {
    href: "/ethics",
    labelEn: "Ethics & Compliance",
    labelDe: "Ethik & EU AI Act",
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
  lawReferences = [],
}: LegalHeaderProps) {
  const pathname = usePathname();
  const { language } = useLegalLanguage();

  const isEn = language === "en";

  return (
    <div className="space-y-6 border-b border-zinc-800 pb-8">
      {/* Top Bar with Navigation Tabs and Language Switcher */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-2">
        {/* Navigation Tabs */}
        <nav className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-zinc-900/60 border border-zinc-800/80">
          {LEGAL_PAGES.map((page) => {
            const Icon = page.icon;
            const isActive = pathname === page.href;
            return (
              <Link
                key={page.href}
                href={page.href}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200",
                  isActive
                    ? "bg-violet-600 text-white shadow-sm font-semibold"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
                )}
              >
                <Icon className={cn("h-3.5 w-3.5", isActive ? "text-white" : "text-violet-400")} />
                <span>{isEn ? page.labelEn : page.labelDe}</span>
              </Link>
            );
          })}
        </nav>

        {/* Language Toggle */}
        <LegalLanguageToggle />
      </div>

      {/* Title & Description */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-violet-950/40 text-violet-400 border border-violet-800/40">
          <Scale className="h-3.5 w-3.5" />
          <span>{isEn ? badgeTextEn : badgeTextDe}</span>
        </div>

        <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-zinc-100">
          {isEn ? titleEn : titleDe}
        </h1>

        <p className="text-sm md:text-base text-zinc-400 max-w-3xl leading-relaxed">
          {isEn ? descriptionEn : descriptionDe}
        </p>
      </div>

      {/* Statutory Jurisdiction & Official Language Notice */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-zinc-900/50 border border-zinc-800 text-xs">
        <div className="flex items-start sm:items-center gap-2 text-zinc-300">
          <AlertCircle className="h-4 w-4 text-violet-400 shrink-0 mt-0.5 sm:mt-0" />
          <span>
            {isEn ? (
              <>
                <strong className="text-zinc-200">Legal Jurisdiction:</strong> Hesse, Germany (EU). This English text is provided for international accessibility. In the event of legal proceedings under German law, the official German statutory wording is authoritative.
              </>
            ) : (
              <>
                <strong className="text-zinc-200">Rechtsstand &amp; Geltungsbereich:</strong> Hessen, Bundesrepublik Deutschland (EU). Die deutsche Fassung stellt den amtlichen, rechtlich verbindlichen Text dar.
              </>
            )}
          </span>
        </div>

        <div className="text-[11px] font-mono text-zinc-400 whitespace-nowrap self-end sm:self-auto">
          {isEn ? "Jurisdiction: Hesse, Germany" : "Gerichtsstand: Hessen, DE"}
        </div>
      </div>

      {/* Quick Law Reference Badges if provided */}
      {lawReferences.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span className="text-zinc-400 text-[11px] font-mono uppercase tracking-wider">
            {isEn ? "Public Law References:" : "Gesetzliche Grundlagen:"}
          </span>
          {lawReferences.map((ref) => (
            <a
              key={ref.code}
              href={ref.url}
              target="_blank"
              rel="noopener noreferrer"
              title={ref.title}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-violet-300 hover:text-white hover:border-violet-500/50 transition-colors"
            >
              <span>{ref.code}</span>
              <ExternalLink className="h-3 w-3 text-violet-400" />
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
