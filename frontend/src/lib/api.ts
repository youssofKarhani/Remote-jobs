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

  async getCurrentUser() {
    return fetchApi("/api/v1/auth/me", { method: "GET" });
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
