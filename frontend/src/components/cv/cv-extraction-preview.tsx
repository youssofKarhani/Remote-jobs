"use client";

import React from "react";
import {
  AlertCircle,
  Award,
  Briefcase,
  FolderGit2,
  GraduationCap,
  Languages,
  Loader2,
  Lock,
  LogIn,
  RotateCcw,
  UserPlus,
  Wrench,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { AuthDialog } from "@/components/auth/auth-dialog";
import type { CVPreviewResponse } from "@/lib/api";
import type { CvExtractionPhase } from "@/lib/use-gated-cv-extraction";

interface CvExtractionPreviewProps {
  result: CVPreviewResponse;
  phase: CvExtractionPhase;
  error: string | null;
  onDiscard: () => void;
  onRetrySave: () => void;
}

const MAX_BULLETS_SHOWN = 3;
const MAX_SKILLS_SHOWN = 30;

function joinParts(parts: (string | null | undefined)[], sep = " · ") {
  return parts.filter((p) => p && p.trim()).join(sep);
}

function dateRange(start: string | null, end: string | null, isCurrent: boolean) {
  const endLabel = isCurrent ? "Present" : end;
  if (start && endLabel && !start.includes(endLabel)) return `${start} – ${endLabel}`;
  return start || endLabel || "";
}

function Section({
  icon: Icon,
  title,
  count,
  children,
}: {
  icon: React.ElementType;
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  if (count === 0) return null;
  return (
    <section className="space-y-3">
      <h4 className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-zinc-400">
        <Icon className="h-3.5 w-3.5 text-violet-400" />
        {title}
        <span className="text-zinc-600">({count})</span>
      </h4>
      {children}
    </section>
  );
}

export function CvExtractionPreview({
  result,
  phase,
  error,
  onDiscard,
  onRetrySave,
}: CvExtractionPreviewProps) {
  const { preview, counts } = result;
  const totalRecords =
    counts.experiences + counts.skills + counts.projects + counts.education + counts.certifications;

  return (
    <div className="space-y-6 text-left">
      {/* What we found */}
      <div className="rounded-3xl border border-zinc-800 bg-zinc-950/80 p-5 sm:p-8 space-y-6 backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-zinc-800/80 pb-4">
          <div className="space-y-1 min-w-0">
            <h3 className="text-lg font-medium text-zinc-100">
              {totalRecords > 0
                ? `We found ${totalRecords} records in your CV`
                : "We couldn't recognise structured sections in this CV"}
            </h3>
            <p className="text-xs text-zinc-400 truncate">Source: {result.filename === "plain_text_input.txt" ? "Pasted text" : result.filename}</p>
          </div>
          {(preview.headline || preview.location) && (
            <p className="text-xs text-zinc-300 sm:text-right">
              {joinParts([preview.headline, preview.location])}
            </p>
          )}
        </div>

        {result.degraded && totalRecords > 0 && (
          <p className="text-xs text-zinc-400 leading-relaxed">
            Read with our fast layout parser. You can review and correct every record from your profile
            after saving.
          </p>
        )}

        <div className="grid gap-6">
          <Section icon={Briefcase} title="Experience" count={preview.experiences.length}>
            <ul className="space-y-3">
              {preview.experiences.map((exp, i) => (
                <li key={i} className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 space-y-2">
                  <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-1">
                    <span className="text-sm font-medium text-zinc-100 break-words">
                      {joinParts([exp.role_title, exp.company_name], " at ") || "Untitled role"}
                    </span>
                    <span className="text-xs font-mono text-zinc-400 shrink-0">
                      {dateRange(exp.start_date, exp.end_date, exp.is_current)}
                    </span>
                  </div>
                  {exp.bullets.length > 0 && (
                    <ul className="space-y-1 text-xs text-zinc-400 list-disc pl-4">
                      {exp.bullets.slice(0, MAX_BULLETS_SHOWN).map((b, j) => (
                        <li key={j} className="break-words">
                          {b.replace(/^[-•*]\s*/, "")}
                        </li>
                      ))}
                      {exp.bullets.length > MAX_BULLETS_SHOWN && (
                        <li className="list-none text-zinc-500">
                          +{exp.bullets.length - MAX_BULLETS_SHOWN} more
                        </li>
                      )}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </Section>

          <Section icon={Wrench} title="Skills" count={preview.skills.length}>
            <div className="flex flex-wrap gap-1.5">
              {preview.skills.slice(0, MAX_SKILLS_SHOWN).map((s, i) => (
                <span
                  key={`${s}-${i}`}
                  className="px-2.5 py-1 rounded-full text-xs bg-zinc-900 border border-zinc-800 text-zinc-300"
                >
                  {s}
                </span>
              ))}
              {preview.skills.length > MAX_SKILLS_SHOWN && (
                <span className="px-2.5 py-1 text-xs text-zinc-500">
                  +{preview.skills.length - MAX_SKILLS_SHOWN} more
                </span>
              )}
            </div>
          </Section>

          <Section icon={GraduationCap} title="Education" count={preview.education.length}>
            <ul className="space-y-2">
              {preview.education.map((edu, i) => (
                <li key={i} className="text-sm text-zinc-200 break-words">
                  {joinParts([edu.degree, edu.field_of_study]) || edu.institution}
                  {edu.institution && edu.degree && edu.institution !== edu.degree && (
                    <span className="text-zinc-400"> — {edu.institution}</span>
                  )}
                  {(edu.start_date || edu.end_date) && (
                    <span className="ml-2 text-xs font-mono text-zinc-500">
                      {dateRange(edu.start_date, edu.end_date, false)}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </Section>

          <Section icon={Award} title="Certifications" count={preview.certifications.length}>
            <ul className="space-y-1.5">
              {preview.certifications.map((c, i) => (
                <li key={i} className="text-sm text-zinc-200 break-words">
                  {c.name}
                  {c.issuing_organization && <span className="text-zinc-400"> — {c.issuing_organization}</span>}
                </li>
              ))}
            </ul>
          </Section>

          <Section icon={FolderGit2} title="Projects" count={preview.projects.length}>
            <ul className="space-y-1.5">
              {preview.projects.map((p, i) => (
                <li key={i} className="text-sm text-zinc-200 break-words">
                  {p.title}
                </li>
              ))}
            </ul>
          </Section>

          <Section icon={Languages} title="Languages" count={preview.languages.length}>
            <p className="text-sm text-zinc-200">{preview.languages.join(", ")}</p>
          </Section>
        </div>
      </div>

      {/* The gate */}
      <div className="rounded-3xl border border-violet-500/40 bg-violet-950/20 p-5 sm:p-7 space-y-4">
        {phase === "saving" ? (
          <div className="flex items-center gap-3 text-sm text-zinc-200">
            <Loader2 className="h-5 w-5 animate-spin text-violet-400" />
            Saving your CV to your profile…
          </div>
        ) : phase === "save_failed" ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm text-red-300">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error || "We couldn't save your CV."}</span>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button onClick={onRetrySave} className="bg-violet-600 hover:bg-violet-500 text-white text-xs">
                Try saving again
              </Button>
              <Button variant="ghost" onClick={onDiscard} className="text-xs text-zinc-400">
                Start over
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-violet-950/80 border border-violet-800/40 text-violet-300 shrink-0">
                <Lock className="h-4 w-4" />
              </div>
              <div className="space-y-1">
                <h4 className="text-sm font-semibold text-zinc-100">Sign in to save your profile and continue</h4>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Nothing has been saved yet. Create a free account or sign in, and we&apos;ll save these
                  records to your profile so you can match jobs and generate tailored CVs.
                </p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
              <AuthDialog defaultTab="register">
                <Button className="bg-violet-600 hover:bg-violet-500 text-white text-xs gap-1.5 w-full sm:w-auto">
                  <UserPlus className="h-3.5 w-3.5" />
                  Create account &amp; save
                </Button>
              </AuthDialog>
              <AuthDialog defaultTab="login">
                <Button
                  variant="outline"
                  className="border-zinc-700 bg-zinc-900/60 text-zinc-200 text-xs gap-1.5 w-full sm:w-auto"
                >
                  <LogIn className="h-3.5 w-3.5" />
                  I already have an account
                </Button>
              </AuthDialog>
              <Button
                variant="ghost"
                onClick={onDiscard}
                className="text-xs text-zinc-400 hover:text-zinc-200 gap-1.5 sm:ml-auto"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Start over
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
