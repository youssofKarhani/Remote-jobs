import { API_BASE_URL } from "./constants";
import { CandidatePreference } from "@/types/preferences";
import { Job } from "@/types/job";

// Helper for local token management
export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token") || null;
}

export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", token);
  }
}

export function clearAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("auth_token");
  }
}

export interface ApiFetchOptions extends RequestInit {
  token?: string | null;
}

export async function fetchApi<T>(
  endpoint: string,
  options: ApiFetchOptions = {}
): Promise<T> {
  const token = options.token !== undefined ? options.token : getAuthToken();
  const headers: Record<string, string> = {};

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...headers,
      ...(options.headers as Record<string, string>),
    },
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(`API Error [${response.status}]: ${errorDetail}`);
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------
export const authApi = {
  async register(email: string, password: string, fullName: string) {
    return fetchApi("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
  },

  async login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const data = await fetchApi<{ access_token: string; token_type: string }>("/api/v1/auth/login/json", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
  },

  async getCurrentUser<T = any>() {
    return fetchApi<T>("/api/v1/auth/me", { method: "GET" });
  },
};

// ---------------------------------------------------------------------------
// CV Ingestion API
// ---------------------------------------------------------------------------
export const cvApi = {
  async uploadCV(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return fetchApi<{
      task_id: string;
      status: string;
      filename: string;
      message: string;
      summary?: {
        experiences_extracted: number;
        bullets_extracted: number;
        skills_extracted: number;
        projects_extracted: number;
        certifications_extracted: number;
        education_extracted: number;
      };
    }>("/api/v1/cv/upload", {
      method: "POST",
      body: formData,
    });
  },

  async parseText(text: string) {
    return fetchApi<{
      task_id: string;
      status: string;
      filename: string;
      message: string;
      summary?: {
        experiences_extracted: number;
        bullets_extracted: number;
        skills_extracted: number;
        projects_extracted: number;
        certifications_extracted: number;
        education_extracted: number;
      };
    }>("/api/v1/cv/parse-text", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  },

  async getStatus(taskId: string) {
    return fetchApi<{
      task_id: string;
      status: string;
      progress_percent: number;
      message: string;
    }>(`/api/v1/cv/status/${taskId}`, { method: "GET" });
  },
};

// ---------------------------------------------------------------------------
// Candidate Profile & Evidence Bank API
// ---------------------------------------------------------------------------
export const profileApi = {
  async getProfile() {
    return fetchApi<any>("/api/v1/profile", { method: "GET" });
  },

  async updateProfile(data: {
    full_name?: string;
    headline?: string;
    summary?: string;
    phone?: string;
    location?: string;
    linkedin_url?: string;
    github_url?: string;
    portfolio_url?: string;
  }) {
    return fetchApi<any>("/api/v1/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async verifyEvidence(itemId: string, itemType: string = "experience_bullet", isVerified: boolean = true) {
    return fetchApi<{
      item_id: string;
      item_type: string;
      is_verified: boolean;
      status: string;
    }>("/api/v1/profile/evidence/verify", {
      method: "POST",
      body: JSON.stringify({
        item_id: itemId,
        item_type: itemType,
        is_verified: isVerified,
      }),
    });
  },

  async verifyAll() {
    return fetchApi<{ status: string; message: string }>("/api/v1/profile/evidence/verify-all", {
      method: "POST",
    });
  },

  // Evidence items CRUD
  async addEvidence(data: { experience_record_id?: string; raw_text: string; category?: string; variants?: Record<string, string>; is_verified?: boolean }) {
    return fetchApi<any>("/api/v1/profile/evidence", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateEvidence(itemId: string, data: { raw_text?: string; category?: string; variants?: Record<string, string>; is_verified?: boolean }) {
    return fetchApi<any>(`/api/v1/profile/evidence/${itemId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async deleteEvidence(itemId: string) {
    return fetchApi<any>(`/api/v1/profile/evidence/${itemId}`, {
      method: "DELETE",
    });
  },

  // Experience records CRUD
  async createExperience(data: { company_name: string; role_title: string; location?: string; start_date: string; end_date?: string; is_current?: boolean; description?: string }) {
    return fetchApi<any>("/api/v1/profile/experiences", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateExperience(id: string, data: any) {
    return fetchApi<any>(`/api/v1/profile/experiences/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async deleteExperience(id: string) {
    return fetchApi<any>(`/api/v1/profile/experiences/${id}`, {
      method: "DELETE",
    });
  },

  // Skills CRUD
  async createSkill(data: { name: string; category?: string; proficiency?: string; years_of_experience?: number; is_verified?: boolean }) {
    return fetchApi<any>("/api/v1/profile/skills", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async deleteSkill(id: string) {
    return fetchApi<any>(`/api/v1/profile/skills/${id}`, {
      method: "DELETE",
    });
  },

  // Projects CRUD
  async createProject(data: { title: string; category?: string; description: string; technologies?: string[]; url?: string; github_url?: string; is_verified?: boolean }) {
    return fetchApi<any>("/api/v1/profile/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async deleteProject(id: string) {
    return fetchApi<any>(`/api/v1/profile/projects/${id}`, {
      method: "DELETE",
    });
  },

  // Certifications CRUD
  async createCertification(data: { name: string; issuing_organization: string; issue_date?: string; expiration_date?: string; credential_id?: string; credential_url?: string; is_verified?: boolean }) {
    return fetchApi<any>("/api/v1/profile/certifications", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async deleteCertification(id: string) {
    return fetchApi<any>(`/api/v1/profile/certifications/${id}`, {
      method: "DELETE",
    });
  },

  // Education CRUD
  async createEducation(data: { institution: string; degree: string; field_of_study: string; start_date?: string; end_date?: string; grade?: string; activities?: string; is_verified?: boolean }) {
    return fetchApi<any>("/api/v1/profile/education", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async deleteEducation(id: string) {
    return fetchApi<any>(`/api/v1/profile/education/${id}`, {
      method: "DELETE",
    });
  },
};


// ---------------------------------------------------------------------------
// Candidate Preferences API
// ---------------------------------------------------------------------------
export const preferencesApi = {
  async getPreferences() {
    return fetchApi<CandidatePreference>("/api/v1/preferences", { method: "GET" });
  },

  async updatePreferences(data: Partial<CandidatePreference>) {
    return fetchApi<CandidatePreference>("/api/v1/preferences", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },
};

// ---------------------------------------------------------------------------
// Jobs Discovery API
// ---------------------------------------------------------------------------
export interface JobListParams {
  page?: number;
  limit?: number;
  search?: string;
  country?: string;
  remote_only?: boolean;
  job_types?: string;
  sort_by?: "newest" | "oldest" | "company";
  min_salary?: number;
  apply_preferences?: boolean;
}

export interface PaginatedJobs {
  items: Job[];
  pagination: {
    total_items: number;
    total_pages: number;
    current_page: number;
    limit: number;
  };
}

export const jobsApi = {
  async getJobs(params: JobListParams = {}): Promise<PaginatedJobs> {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page.toString());
    if (params.limit) query.set("limit", params.limit.toString());
    if (params.search) query.set("search", params.search);
    if (params.country) query.set("country", params.country);
    if (params.remote_only !== undefined) query.set("remote_only", params.remote_only.toString());
    if (params.job_types) query.set("job_types", params.job_types);
    if (params.sort_by) query.set("sort_by", params.sort_by);
    if (params.min_salary !== undefined) query.set("min_salary", params.min_salary.toString());
    if (params.apply_preferences !== undefined)
      query.set("apply_preferences", params.apply_preferences.toString());

    return fetchApi<PaginatedJobs>(`/api/v1/jobs?${query.toString()}`, {
      method: "GET",
    });
  },

  async syncJobs(source: string = "arbeitnow", forceRefresh: boolean = false) {
    return fetchApi<{
      status: string;
      source: string;
      fetched_count: number;
      new_jobs_inserted: number;
      duplicates_skipped: number;
    }>("/api/v1/jobs/sync", {
      method: "POST",
      body: JSON.stringify({ source, force_refresh: forceRefresh }),
    });
  },

  async getJobDetail(jobIdOrSlug: string): Promise<Job> {
    return fetchApi<Job>(`/api/v1/jobs/${jobIdOrSlug}`, { method: "GET" });
  },
};

// ---------------------------------------------------------------------------
// Matching & Compatibility Assessment API
// ---------------------------------------------------------------------------
export const matchingApi = {
  async matchJob(jobId: string) {
    return fetchApi<any>(`/api/v1/jobs/${jobId}/match`, {
      method: "POST",
    });
  },

  async getJobMatch(jobId: string) {
    return fetchApi<any>(`/api/v1/jobs/${jobId}/match`, {
      method: "GET",
    });
  },

  async getMatches(params: { min_score?: number; status?: string; page?: number; limit?: number } = {}) {
    const query = new URLSearchParams();
    if (params.min_score !== undefined) query.set("min_score", params.min_score.toString());
    if (params.status) query.set("status", params.status);
    if (params.page) query.set("page", params.page.toString());
    if (params.limit) query.set("limit", params.limit.toString());

    return fetchApi<any>(`/api/v1/matches?${query.toString()}`, {
      method: "GET",
    });
  },

  async getMatchDetail(matchId: string) {
    return fetchApi<any>(`/api/v1/matches/${matchId}`, {
      method: "GET",
    });
  },
};

// ---------------------------------------------------------------------------
// CV Tailoring & Document Download API
// ---------------------------------------------------------------------------
export const tailoringApi = {
  async tailorCV(jobId: string, options: { max_bullets_per_role?: number; template_name?: string } = {}) {
    return fetchApi<any>(`/api/v1/jobs/${jobId}/tailor-cv`, {
      method: "POST",
      body: JSON.stringify(options),
    });
  },

  getDownloadUrl(documentId: string): string {
    const token = getAuthToken();
    const base = `${API_BASE_URL}/api/v1/documents/${documentId}/download`;
    return token ? `${base}?token=${token}` : base;
  },

  async getDocumentInfo(documentId: string) {
    return fetchApi<any>(`/api/v1/documents/${documentId}`, {
      method: "GET",
    });
  },
};

// ---------------------------------------------------------------------------
// Cover Letter Generator API
// ---------------------------------------------------------------------------
export const coverLetterApi = {
  async getStrategies() {
    return fetchApi<any[]>("/api/v1/cover-letters/strategies", {
      method: "GET",
    });
  },

  async generateCoverLetter(jobId: string, strategy: string = "Technical Depth") {
    return fetchApi<any>(`/api/v1/jobs/${jobId}/cover-letter`, {
      method: "POST",
      body: JSON.stringify({ strategy }),
    });
  },

  async getCoverLetter(jobId: string) {
    return fetchApi<any>(`/api/v1/jobs/${jobId}/cover-letter`, {
      method: "GET",
    });
  },

  async updateCoverLetter(jobId: string, content: string) {
    return fetchApi<any>(`/api/v1/jobs/${jobId}/cover-letter`, {
      method: "PUT",
      body: JSON.stringify({ content }),
    });
  },
};

// ---------------------------------------------------------------------------
// Application Tracking System (ATS) API
// ---------------------------------------------------------------------------
export const atsApi = {
  async getApplications(status?: string) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return fetchApi<any[]>(`/api/v1/applications${query}`, {
      method: "GET",
    });
  },

  async createApplication(data: {
    job_id: string;
    status?: string;
    notes?: string;
    tailored_cv_id?: string;
    cover_letter_id?: string;
    salary_offered?: number;
  }) {
    return fetchApi<any>("/api/v1/applications", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateStatus(applicationId: string, status: string) {
    return fetchApi<any>(`/api/v1/applications/${applicationId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  },

  async updateApplication(applicationId: string, data: any) {
    return fetchApi<any>(`/api/v1/applications/${applicationId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async deleteApplication(applicationId: string) {
    return fetchApi<any>(`/api/v1/applications/${applicationId}`, {
      method: "DELETE",
    });
  },
};

