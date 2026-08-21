export interface CandidateProfile {
  id: string;
  user_id: string;
  headline?: string | null;
  summary?: string | null;
  phone?: string | null;
  location?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  portfolio_url?: string | null;
  raw_cv_text?: string | null;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface EvidenceItem {
  id: string;
  user_id: string;
  experience_record_id?: string | null;
  stable_id: string;
  raw_text: string;
  category: string;
  variants?: Record<string, string> | null;
  is_verified: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface ExperienceRecord {
  id: string;
  user_id: string;
  company_name: string;
  role_title: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  description?: string | null;
  display_order: number;
  evidence_items?: EvidenceItem[];
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: string;
  user_id: string;
  stable_id: string;
  name: string;
  category: string;
  proficiency?: string | null;
  years_of_experience?: number | null;
  is_verified: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  stable_id: string;
  title: string;
  category?: string | null;
  description: string;
  technologies: string[];
  url?: string | null;
  github_url?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  is_verified: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface Certification {
  id: string;
  user_id: string;
  stable_id: string;
  name: string;
  issuing_organization: string;
  issue_date?: string | null;
  expiration_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
  is_verified: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface EducationRecord {
  id: string;
  user_id: string;
  stable_id: string;
  institution: string;
  degree: string;
  field_of_study: string;
  start_date?: string | null;
  end_date?: string | null;
  grade?: string | null;
  activities?: string | null;
  is_verified: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface EvidenceBank {
  profile: CandidateProfile | null;
  experiences: ExperienceRecord[];
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
  education: EducationRecord[];
}
