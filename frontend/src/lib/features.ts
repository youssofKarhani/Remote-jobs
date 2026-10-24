/**
 * [HIDDEN:EVIDENCE_VERIFICATION]
 * Master client-side feature flag toggles.
 * When NEXT_PUBLIC_FEATURE_EVIDENCE_VERIFICATION is not set or not "true",
 * all evidence verification buttons, trust tiers, verified badges, and
 * "Evidence Bank" wording are replaced with neutral "Career Profile" presentation.
 * 
 * See docs/HIDDEN_FEATURES/evidence-verification.md for full details and reactivation steps.
 */
export const FEATURES = {
  evidenceVerification:
    process.env.NEXT_PUBLIC_FEATURE_EVIDENCE_VERIFICATION === "true",
} as const;
