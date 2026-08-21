export interface CandidatePreference {
  id: string;
  user_id: string;
  target_roles: string[];
  locations: string[];
  remote_only: boolean;
  hybrid_allowed: boolean;
  onsite_allowed: boolean;
  job_types: string[];
  min_salary?: number | null;
  salary_currency?: string | null;
  max_seniority?: string | null;
  languages: string[];
  excluded_companies: string[];
  excluded_keywords: string[];
  preferred_industries: string[];
  created_at: string;
  updated_at: string;
}
