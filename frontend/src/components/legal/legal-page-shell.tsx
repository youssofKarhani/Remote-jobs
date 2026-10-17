"use client";

import React from "react";
import { LegalLanguageProvider, useLegalLanguage } from "./legal-context";
import { LegalHeader } from "./legal-header";
import { PublicLawRedirects } from "./public-law-redirects";

interface LegalPageShellProps {
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
  childrenEn: React.ReactNode;
  childrenDe: React.ReactNode;
}

function LegalPageContent({
  badgeTextEn,
  badgeTextDe,
  titleEn,
  titleDe,
  descriptionEn,
  descriptionDe,
  lawReferences,
  childrenEn,
  childrenDe,
}: LegalPageShellProps) {
  const { language } = useLegalLanguage();

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-10">
      <LegalHeader
        badgeTextEn={badgeTextEn}
        badgeTextDe={badgeTextDe}
        titleEn={titleEn}
        titleDe={titleDe}
        descriptionEn={descriptionEn}
        descriptionDe={descriptionDe}
        lawReferences={lawReferences}
      />

      {/* Render selected language */}
      <div className="space-y-8 animate-in fade-in duration-150">
        {language === "en" ? childrenEn : childrenDe}
      </div>

      {/* Statutory Public Law Redirects Directory */}
      <PublicLawRedirects className="mt-12" />
    </div>
  );
}

export function LegalPageShell(props: LegalPageShellProps) {
  return (
    <LegalLanguageProvider>
      <LegalPageContent {...props} />
    </LegalLanguageProvider>
  );
}
