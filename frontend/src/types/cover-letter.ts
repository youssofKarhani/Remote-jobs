export interface PositioningStrategy {
  id: string;
  name: string;
  tagline: string;
  description: string;
}

export interface CoverLetter {
  id: string;
  user_id: string;
  job_id: string;
  strategy: string;
  content: string;
  referenced_evidence_ids: string[];
  created_at: string;
  updated_at: string;
}
