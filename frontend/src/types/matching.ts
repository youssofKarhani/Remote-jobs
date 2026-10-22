import { Job } from "./job";

export interface JobAssessment {
  id: string;
  job_match_id: string;
  skills_score: number;
  experience_score: number;
  seniority_score: number;
  location_score: number;
  language_score: number;
  confidence: number;
  evaluation_mode?: "ai" | "heuristic" | "prescreen_filtered" | string;
  strengths: string[];
  missing_requirements: string[];
  matching_evidence_ids: string[];
}

export interface JobMatch {
  id: string;
  user_id: string;
  job_id: string;
  overall_score: number;
  recommendation: "apply" | "consider" | "skip" | string;
  status: "new" | "viewed" | "dismissed" | "saved" | string;
  matched_at: string;
  job?: Job;
  assessment?: JobAssessment;
}

export interface PaginatedMatches {
  items: JobMatch[];
  total_items: number;
  total_pages: number;
  current_page: number;
  limit: number;
}
