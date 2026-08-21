export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface ExtractionTaskStatus {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress_percent: number;
  stage_message: string;
  error_message?: string | null;
  extracted_summary?: {
    experiences_count: number;
    skills_count: number;
    projects_count: number;
    certifications_count: number;
    education_count: number;
  } | null;
}
