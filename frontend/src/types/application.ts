import { Job } from "./job";

export interface ApplicationEvent {
  id: string;
  application_id: string;
  event_type: string;
  description?: string | null;
  created_at: string;
}

export type ApplicationStage = "Saved" | "Applying" | "Applied" | "Interview" | "Offer" | "Rejected";

export interface Application {
  id: string;
  user_id: string;
  job_id: string;
  status: ApplicationStage;
  tailored_cv_id?: string | null;
  cover_letter_id?: string | null;
  applied_at?: string | null;
  salary_offered?: number | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  job?: Job | null;
  events?: ApplicationEvent[];
}
