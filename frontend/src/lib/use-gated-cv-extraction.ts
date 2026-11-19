"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { cvApi, CVPreviewResponse } from "./api";
import { useAuth } from "./auth-context";

/**
 * CV extraction that anyone can start, but only signed-in users can finish.
 *
 * - Signed-out visitors get a real preview from the public `/cv/preview*` endpoints
 *   (nothing is stored), then are stopped at the `awaiting_auth` phase.
 * - As soon as they sign in or register, the same file/text is sent to the
 *   authenticated endpoint and saved to *their* profile.
 * - Signed-in users skip the preview and save directly.
 */

export type CvSource =
  | { kind: "file"; file: File }
  | { kind: "text"; text: string; label: string };

export type CvExtractionPhase =
  | "idle"
  | "extracting"
  | "awaiting_auth"
  | "saving"
  | "save_failed";

export interface CvSaveSummary {
  experiences_extracted: number;
  bullets_extracted: number;
  skills_extracted: number;
  projects_extracted: number;
  certifications_extracted: number;
  education_extracted: number;
}

const EMPTY_SUMMARY: CvSaveSummary = {
  experiences_extracted: 0,
  bullets_extracted: 0,
  skills_extracted: 0,
  projects_extracted: 0,
  certifications_extracted: 0,
  education_extracted: 0,
};

export function sourceLabel(source: CvSource): string {
  return source.kind === "file" ? source.file.name : source.label;
}

function friendlyError(err: unknown, fallback: string): string {
  const message = err instanceof Error ? err.message : "";
  if (!message) return fallback;
  return message.replace(/^API Error \[\d+\]:\s*/, "");
}

export function useGatedCvExtraction(onSaved: (summary: CvSaveSummary, source: CvSource) => void) {
  const { isAuthenticated } = useAuth();
  const [phase, setPhase] = useState<CvExtractionPhase>("idle");
  const [source, setSource] = useState<CvSource | null>(null);
  const [preview, setPreview] = useState<CVPreviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSavedRef = useRef(onSaved);
  useEffect(() => {
    onSavedRef.current = onSaved;
  }, [onSaved]);

  const save = useCallback(async (src: CvSource) => {
    setPhase("saving");
    setError(null);
    try {
      const res =
        src.kind === "file" ? await cvApi.uploadCV(src.file) : await cvApi.parseText(src.text);
      const summary = { ...EMPTY_SUMMARY, ...(res.summary ?? {}) };
      setPhase("idle");
      setPreview(null);
      setSource(null);
      onSavedRef.current(summary, src);
    } catch (err) {
      setError(friendlyError(err, "We couldn't save your CV. Please try again."));
      setPhase("save_failed");
    }
  }, []);

  const extract = useCallback(
    async (src: CvSource) => {
      setError(null);
      setSource(src);
      if (isAuthenticated) {
        await save(src);
        return;
      }
      setPhase("extracting");
      try {
        const res =
          src.kind === "file" ? await cvApi.previewCV(src.file) : await cvApi.previewText(src.text);
        setPreview(res);
        setPhase("awaiting_auth");
      } catch (err) {
        setError(
          friendlyError(err, "Failed to read your CV. Please check the file format and try again.")
        );
        setSource(null);
        setPhase("idle");
      }
    },
    [isAuthenticated, save]
  );

  // The gate: once the visitor signs in or registers, save the CV they already extracted.
  useEffect(() => {
    if (phase === "awaiting_auth" && isAuthenticated && source) {
      void save(source);
    }
  }, [phase, isAuthenticated, source, save]);

  const discard = useCallback(() => {
    setPhase("idle");
    setSource(null);
    setPreview(null);
    setError(null);
  }, []);

  const retrySave = useCallback(() => {
    if (source) void save(source);
  }, [source, save]);

  return {
    phase,
    source,
    preview,
    error,
    setError,
    extract,
    discard,
    retrySave,
    isBusy: phase === "extracting" || phase === "saving",
  };
}
