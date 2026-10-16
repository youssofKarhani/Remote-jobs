export interface GeneratedDocument {
  id: string;
  user_id: string;
  job_id?: string | null;
  document_type: string;
  format: string;
  selected_evidence_ids?: string[] | null;
  download_url?: string | null;
  created_at: string;
}
