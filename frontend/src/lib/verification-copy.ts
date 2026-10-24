import { FEATURES } from "./features";

/**
 * [HIDDEN:EVIDENCE_VERIFICATION]
 * Central copy dictionary mapping keys to both their original (verified/evidence)
 * text and neutral (career profile/records) text.
 *
 * All original wording is preserved in this file so that toggling
 * NEXT_PUBLIC_FEATURE_EVIDENCE_VERIFICATION="true" restores the exact original presentation.
 *
 * See docs/HIDDEN_FEATURES/evidence-verification.md
 */
export const VERIFICATION_COPY = {
  // Navigation & General branding
  "bank.name": {
    verified: "Evidence Bank",
    neutral: "Career Profile",
  },
  "bank.navShort": {
    verified: "Evidence",
    neutral: "Profile",
  },
  "meta.description": {
    verified:
      "Upload your raw experience. We engineer the perfect application with zero hallucination and deterministic verifiable evidence.",
    neutral:
      "Upload your raw experience. We engineer the perfect application with zero hallucination and deterministic career grounding.",
  },
  "home.heroSubtitle": {
    verified:
      "Connect your profile to our automated pipeline to discover high-match roles and generate highly tailored, verifiable applications on autopilot.",
    neutral:
      "Connect your profile to our automated pipeline to discover high-match roles and generate highly tailored applications on autopilot.",
  },
  "footer.guarantee": {
    verified:
      "Artificial intelligence selects relevant credentials but never invents them. All documents are strictly derived from verified experience IDs (EXP_xxx).",
    neutral:
      "Artificial intelligence selects relevant credentials but never invents them. All documents are strictly derived from your source career IDs (EXP_xxx).",
  },

  // Auth Dialogs
  "auth.dialogDescription": {
    verified:
      "Authenticate to sync external jobs, manage your verified Evidence Bank, and customize deterministic filters.",
    neutral:
      "Authenticate to sync external jobs, manage your Career Profile, and customize deterministic filters.",
  },
  "signOut.dialogDescription": {
    verified:
      "Your verified Evidence Bank records, matching preferences, and tailored ATS applications remain saved. You can sign back in at any time.",
    neutral:
      "Your Career Profile records, matching preferences, and tailored ATS applications remain saved. You can sign back in at any time.",
  },

  // Architecture Dialog
  "arch.stage1Title": {
    verified: "1. Canonical Evidence Bank",
    neutral: "1. Canonical Career Profile",
  },
  "arch.stage1Body": {
    verified:
      "Raw resumes are decomposed into immutable data points assigned permanent verification IDs. Only verified items from your past experience can be used in downstream applications.",
    neutral:
      "Raw resumes are decomposed into immutable data points assigned permanent record IDs. Only source items from your past experience can be used in downstream applications.",
  },
  "arch.stage2Scores": {
    verified: "explainable, verifiable match scores.",
    neutral: "explainable match scores.",
  },
  "arch.stage3Proof": {
    verified:
      "Before document synthesis, a strict mathematical proof guarantees that every single claim in your tailored CV is an exact subset of your verified profile facts.",
    neutral:
      "Before document synthesis, a strict mathematical proof guarantees that every single claim in your tailored CV is an exact subset of your profile facts.",
  },
  "arch.dataStoreLabel": {
    verified: "Immutable Verified Data Store",
    neutral: "Immutable Profile Data Store",
  },
  "arch.bulletsLabel": {
    verified: "Verified Bullets",
    neutral: "Achievement Bullets",
  },

  // Home Animation & Visuals
  "visual.rolesCount": {
    verified: "3 Verified Roles",
    neutral: "3 Career Roles",
  },
  "visual.rolesTag": {
    verified: "Verified",
    neutral: "Structured",
  },
  "visual.skillsTag": {
    verified: "Verified",
    neutral: "Indexed",
  },
  "visual.buildsCount": {
    verified: "4 Verified Builds",
    neutral: "4 Tracked Builds",
  },
  "visual.buildsTag": {
    verified: "Verified",
    neutral: "Structured",
  },
  "visual.certsTag": {
    verified: "Verified",
    neutral: "Documented",
  },
  "visual.bankTitle": {
    verified: "Verified Evidence Bank",
    neutral: "Career Profile Records",
  },
  "visual.bankQuote": {
    verified:
      "“Feed the engine everything. We deduplicate your history into one verified, canonical profile.”",
    neutral:
      "“Feed the engine everything. We deduplicate your history into one canonical profile.”",
  },
  "visual.guaranteeBanner": {
    verified: "Verified Set Inclusion",
    neutral: "Strict Set Inclusion",
  },
  "visual.buildingBlocksQuote": {
    verified:
      "“We turn your static resume into dynamic, verifiable building blocks.”",
    neutral:
      "“We turn your static resume into dynamic, structured building blocks.”",
  },

  // Timeline
  "timeline.step1Copy": {
    verified: "Your base CVs are deconstructed into verified, reusable data points.",
    neutral: "Your base CVs are deconstructed into reusable, structured data points.",
  },
  "timeline.step2Copy": {
    verified:
      "We select the perfect verified blocks to generate a tailored CV and cover letter with zero hallucinations.",
    neutral:
      "We select the perfect profile blocks to generate a tailored CV and cover letter with zero hallucinations.",
  },
  "timeline.subtitle": {
    verified: "Scroll through the deterministic pipeline powering verified job applications.",
    neutral: "Scroll through the deterministic pipeline powering tailored job applications.",
  },
  "timeline.factLabel": {
    verified: "Verified Fact",
    neutral: "Profile Fact",
  },
  "timeline.bankCircle": {
    verified: "Candidate Evidence Bank",
    neutral: "Candidate Career Profile",
  },
  "timeline.expBadge": {
    verified: "[EXP_001] Verified",
    neutral: "[EXP_001] Sourced",
  },
  "timeline.skillBadge": {
    verified: "[SKILL_001] Verified",
    neutral: "[SKILL_001] Sourced",
  },

  // Onboarding
  "onboarding.step3Label": {
    verified: "Evidence Bank",
    neutral: "Career Profile",
  },
  "onboarding.verifiedIngestion": {
    verified: "Verified Ingestion",
    neutral: "Profile Ingestion",
  },
  "onboarding.footerBanner": {
    verified: "Deterministic Anti-Hallucination Architecture • 100% Verified Profile Evidence",
    neutral: "Deterministic Anti-Hallucination Architecture • 100% Grounded Profile Records",
  },
  "onboarding.targetAlign": {
    verified:
      "We will align your verified experience to curate tailored applications specifically for this domain.",
    neutral:
      "We will align your experience to curate tailored applications specifically for this domain.",
  },
  "onboarding.extractStatus": {
    verified: "Extracting Evidence...",
    neutral: "Extracting Profile Records...",
  },
  "onboarding.deconstructStatus": {
    verified: "Deconstructing resume into immutable, verified entities...",
    neutral: "Deconstructing resume into immutable, structured entities...",
  },
  "onboarding.evidenceSubtitle": {
    verified:
      "We deconstruct your resume into discrete, verifiable records in your Evidence Bank. No fake compatibility numbers — you can tailor and curate this evidence for any job.",
    neutral:
      "We deconstruct your resume into discrete, structured records in your Career Profile. No fake compatibility numbers — you can tailor and curate these records for any job.",
  },
  "onboarding.bankReady": {
    verified: "Step 03 • Candidate Evidence Bank Ready",
    neutral: "Step 03 • Career Profile Ready",
  },
  "onboarding.achievementsLabel": {
    verified: "Verified Achievements",
    neutral: "Captured Achievements",
  },
  "onboarding.bankSubtitle": {
    verified:
      "Your raw resume has been deconstructed into verified, immutable facts ready to curate applications on demand.",
    neutral:
      "Your raw resume has been deconstructed into structured, immutable facts ready to curate applications on demand.",
  },
  "onboarding.recordsIngested": {
    verified: "Verified Records Ingested",
    neutral: "Captured Records Ingested",
  },
  "onboarding.reviewBank": {
    verified: "Review Evidence Bank",
    neutral: "Review Career Profile",
  },
  "onboarding.canonicalTag": {
    verified: "Canonical Evidence • Zero Hallucination",
    neutral: "Canonical Profile • Zero Hallucination",
  },

  // CV Upload Page
  "cvUpload.authRequired": {
    verified: "Please sign in or use Demo Mode to extract and persist resume evidence.",
    neutral: "Please sign in or use Demo Mode to extract and persist resume records.",
  },
  "cvUpload.persistingStep": {
    verified: "Assigning immutable stable IDs and persisting to Evidence Bank...",
    neutral: "Assigning immutable stable IDs and persisting to Career Profile...",
  },
  "cvUpload.pageSubtitle": {
    verified:
      "Upload your resume (PDF/DOCX) or paste text to initialize your canonical Candidate Evidence Bank.",
    neutral:
      "Upload your resume (PDF/DOCX) or paste text to initialize your canonical Career Profile.",
  },
  "cvUpload.signInTitle": {
    verified: "Sign in to Ingest & Persist Evidence",
    neutral: "Sign in to Ingest & Persist Profile",
  },
  "cvUpload.signInDescription": {
    verified:
      "Structured extraction transforms your raw CV into immutable, stable-identified records in your private Candidate Evidence Bank.",
    neutral:
      "Structured extraction transforms your raw CV into immutable, stable-identified records in your private Career Profile.",
  },
  "cvUpload.streamlinedSetup": {
    verified:
      "Set your target role and initialize your Evidence Bank in a streamlined 3-step setup.",
    neutral:
      "Set your target role and initialize your Career Profile in a streamlined 3-step setup.",
  },
  "cvUpload.reviewBankButton": {
    verified: "Review Evidence Bank",
    neutral: "Review Career Profile",
  },

  // Profile Page
  "profile.pageTitle": {
    verified: "Candidate Evidence Bank",
    neutral: "Career Profile",
  },
  "profile.pageSubtitle": {
    verified:
      "Manage your canonical profile and immutable evidence items (stable IDs). Items can be used immediately for standard exports or verified for the Partner-Verified trust tier.",
    neutral:
      "Manage your canonical profile and immutable career records (stable IDs), ready to use in every tailored application.",
  },
  "profile.verifyAllButton": {
    verified: "Verify All Evidence",
    neutral: "Verify All Evidence",
  },
  "profile.signInTitle": {
    verified: "Sign in to Access Your Evidence Bank",
    neutral: "Sign in to Access Your Career Profile",
  },
  "profile.signInDescription": {
    verified:
      "Your canonical Candidate Evidence Bank stores immutable, verified experience bullets, skills, and projects with stable IDs. Sign in or initialize a demo candidate profile to view and verify evidence.",
    neutral:
      "Your canonical Career Profile stores immutable experience bullets, skills, and projects with stable IDs. Sign in or initialize a demo candidate profile to view and edit records.",
  },
  "profile.loadingBank": {
    verified: "Loading Candidate Evidence Bank...",
    neutral: "Loading Career Profile...",
  },
  "profile.emptyBank": {
    verified: "No Evidence Bank Entries Found",
    neutral: "No Career Profile Entries Found",
  },
  "profile.verifiableAchievements": {
    verified: "Verifiable Achievement Bullets",
    neutral: "Achievement Bullets",
  },
  "profile.verifiedSkillsDesc": {
    verified: "Verified skills indexed with immutable stable IDs for semantic matching.",
    neutral: "Skills indexed with immutable stable IDs for semantic matching.",
  },

  // Jobs & Documents
  "job.matchScoreTooltip": {
    verified: "Deterministic match score evaluated against your verified Evidence Bank",
    neutral: "Deterministic match score evaluated against your Career Profile",
  },
  "tailor.dialogSubtitle": {
    verified: "Tailor your verified Evidence Bank into a production Word (.docx) document optimized for",
    neutral: "Tailor your Career Profile into a production Word (.docx) document optimized for",
  },
  "tailor.zeroHallucination": {
    verified:
      "Zero Hallucination Guarantee: All statements are sourced verbatim from your verified Evidence Bank.",
    neutral:
      "Zero Hallucination Guarantee: All statements are sourced verbatim from your Career Profile.",
  },
  "tailor.renderedSuccess": {
    verified: "Your customized .docx resume has been rendered using verified evidence points tailored to",
    neutral: "Your customized .docx resume has been rendered using profile records tailored to",
  },
  "tailor.bulletsGrounded": {
    verified: "Evidence Bullets Grounded",
    neutral: "Career Records Grounded",
  },
  "coverLetter.dialogSubtitle": {
    verified: "grounded in verified Evidence Bank facts.",
    neutral: "grounded in your Career Profile facts.",
  },
  "coverLetter.placeholder": {
    verified:
      "Click any strategy above or 'Generate' to create a targeted engineering cover letter based on your verified Evidence Bank...",
    neutral:
      "Click any strategy above or 'Generate' to create a targeted engineering cover letter based on your Career Profile...",
  },
  "coverLetter.groundedProof": {
    verified: "Grounded Evidence IDs (Zero Hallucination Proof):",
    neutral: "Referenced Record IDs (Zero Hallucination Proof):",
  },
  "applications.emptyCoverLetter": {
    verified:
      "No cover letter has been generated yet for this job.\n\nTo generate an evidence-grounded cover letter, open this job posting from the Jobs Feed and select 'Cover Letter' to choose one of the 10 engineering positioning strategies.",
    neutral:
      "No cover letter has been generated yet for this job.\n\nTo generate a tailored cover letter, open this job posting from the Jobs Feed and select 'Cover Letter' to choose one of the 10 engineering positioning strategies.",
  },

  // Pipeline Schedule Dialog
  "schedule.noEvidenceTitle": {
    verified: "No CV evidence uploaded yet",
    neutral: "No CV records uploaded yet",
  },
  "schedule.noEvidenceDesc": {
    verified: "Upload a CV to initialize your Evidence Bank before the batch.",
    neutral: "Upload a CV to initialize your Career Profile before the batch.",
  },
  "schedule.reviewEvidence": {
    verified: "Review Evidence",
    neutral: "Review Profile",
  },
  "schedule.evidenceAudit": {
    verified: "Evidence audit",
    neutral: "Profile audit",
  },
  "schedule.checkingBank": {
    verified: "Checking evidence bank & preferences...",
    neutral: "Checking profile & preferences...",
  },
  "schedule.auditRecommend": {
    verified:
      "Connect your account before the 06:00 UTC batch so our AI can check your evidence bank, flag missing metrics, and recommend role adjustments.",
    neutral:
      "Connect your account before the 06:00 UTC batch so our AI can check your profile, flag missing metrics, and recommend role adjustments.",
  },

  // Legal & Compliance
  "ethics.tailoredBoundary": {
    verified:
      "FindJobFit enforces strict factual boundaries. Tailored resumes and cover letters are constructed solely from verified evidence and career history explicitly provided by the user. The platform does not invent credentials, fabricate dates, or generate fictitious claims.",
    neutral:
      "FindJobFit enforces strict factual boundaries. Tailored resumes and cover letters are constructed solely from career history and records explicitly provided by the user. The platform does not invent credentials, fabricate dates, or generate fictitious claims.",
  },
  "ethics.objectiveEvaluation": {
    verified:
      "The matching algorithm evaluates jobs exclusively against objective parameters, such as documented technical skills, verified work experience, and user-defined location preferences.",
    neutral:
      "The matching algorithm evaluates jobs exclusively against objective parameters, such as documented technical skills, work experience, and user-defined location preferences.",
  },
  "privacy.careerInfo": {
    verified:
      "When you submit resume documents or career details, the data is processed to structure your verified experience and match you with relevant job opportunities.",
    neutral:
      "When you submit resume documents or career details, the data is processed to structure your experience and match you with relevant job opportunities.",
  },
  "privacy.mlModels": {
    verified:
      "FindJobFit uses machine learning models to analyze job descriptions and align them with your verified qualifications.",
    neutral:
      "FindJobFit uses machine learning models to analyze job descriptions and align them with your qualifications.",
  },
} as const;

export type VerificationCopyKey = keyof typeof VERIFICATION_COPY;

/**
 * Returns the copy string corresponding to the key, depending on whether
 * evidence verification is active.
 */
export function vcopy(key: VerificationCopyKey): string {
  const item = VERIFICATION_COPY[key];
  if (!item) {
    return "";
  }
  return FEATURES.evidenceVerification ? item.verified : item.neutral;
}
