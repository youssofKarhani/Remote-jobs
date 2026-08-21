export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const JOB_TYPES = [
  "Full Time",
  "Part Time",
  "Working Student",
  "Internship",
  "Contract",
] as const;

export const SKILL_CATEGORIES = [
  "programming",
  "backend",
  "frontend",
  "data_engineering",
  "ai_ml",
  "devops",
  "tools",
  "soft_skill",
] as const;

export const EVIDENCE_CATEGORIES = [
  "experience",
  "achievement",
  "metric",
  "leadership",
] as const;
