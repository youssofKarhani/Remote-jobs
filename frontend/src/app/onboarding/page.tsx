"use client";

import React, { useState } from "react";
import { AnimatePresence } from "framer-motion";
import Link from "next/link";
import { ArrowLeft, Check, Sparkles } from "lucide-react";
import { TargetStep } from "@/components/onboarding/target-step";
import { EvidenceStep } from "@/components/onboarding/evidence-step";
import { EvidenceBankStep, ExtractionSummaryData } from "@/components/onboarding/evidence-bank-step";

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [targetRole, setTargetRole] = useState<string>("Staff Backend Engineer");
  const [extractionSummary, setExtractionSummary] = useState<ExtractionSummaryData>({
    experiencesCount: 0,
    bulletsCount: 0,
    skillsCount: 0,
    projectsCount: 0,
    educationCount: 0,
    certificationsCount: 0,
  });

  const STEPS_META = [
    { id: 1, label: "Target Role" },
    { id: 2, label: "CV Ingestion" },
    { id: 3, label: "Evidence Bank" },
  ];

  return (
    <div className="min-h-[85vh] flex flex-col justify-between py-6 md:py-10 max-w-5xl mx-auto px-4">
      {/* Top Wizard Navigation Bar */}
      <div className="w-full flex items-center justify-between pb-8 mb-4 border-b border-zinc-900">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-mono text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Exit Onboarding</span>
        </Link>

        {/* Step Progression Indicators */}
        <div className="flex items-center gap-2 sm:gap-3">
          {STEPS_META.map((step) => {
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;

            return (
              <div key={step.id} className="flex items-center gap-2 sm:gap-3">
                <button
                  type="button"
                  onClick={() => {
                    // Allow jumping back to earlier completed steps
                    if (isCompleted) setCurrentStep(step.id);
                  }}
                  disabled={!isCompleted}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono transition-all ${
                    isCurrent
                      ? "bg-violet-950/60 text-violet-300 border border-violet-500/40 shadow-sm"
                      : isCompleted
                      ? "bg-zinc-900 text-zinc-300 hover:text-white cursor-pointer border border-zinc-800"
                      : "bg-zinc-950 text-zinc-600 border border-zinc-900 cursor-not-allowed"
                  }`}
                >
                  <span
                    className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${
                      isCurrent
                        ? "bg-violet-500 text-white"
                        : isCompleted
                        ? "bg-emerald-500 text-black"
                        : "bg-zinc-800 text-zinc-500"
                    }`}
                  >
                    {isCompleted ? <Check className="w-2.5 h-2.5" /> : step.id}
                  </span>
                  <span className="hidden sm:inline">{step.label}</span>
                </button>

                {step.id < STEPS_META.length && (
                  <div
                    className={`w-4 sm:w-6 h-[1px] transition-colors ${
                      currentStep > step.id ? "bg-violet-500/60" : "bg-zinc-800"
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>

        <div className="hidden md:flex items-center gap-1.5 text-[11px] font-mono text-zinc-400">
          <Sparkles className="w-3 h-3 text-violet-400" />
          <span>Verified Ingestion</span>
        </div>
      </div>

      {/* Main Step Container with Framer Motion AnimatePresence */}
      <div className="flex-1 flex items-center justify-center">
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <TargetStep
              key="step-1"
              initialValue={targetRole}
              onComplete={(selectedRole) => {
                setTargetRole(selectedRole);
                setCurrentStep(2);
              }}
            />
          )}

          {currentStep === 2 && (
            <EvidenceStep
              key="step-2"
              targetRole={targetRole}
              onBack={() => setCurrentStep(1)}
              onComplete={(result) => {
                setExtractionSummary(result);
                setCurrentStep(3);
              }}
            />
          )}

          {currentStep === 3 && (
            <EvidenceBankStep
              key="step-3"
              targetRole={targetRole}
              summary={extractionSummary}
              onUploadAnother={() => setCurrentStep(2)}
            />
          )}
        </AnimatePresence>
      </div>

      {/* Bottom System Integrity Watermark */}
      <div className="pt-8 text-center text-xs font-mono text-zinc-400 border-t border-zinc-900 mt-8">
        Deterministic Anti-Hallucination Architecture &bull; 100% Verified Profile Evidence
      </div>
    </div>
  );
}
