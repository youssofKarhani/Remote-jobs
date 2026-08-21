export interface Company {
  id: string;
  name: string;
  normalized_name: string;
  website?: string | null;
  logo_url?: string | null;
  description?: string | null;
  engineering_focus?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  company_id?: string | null;
  slug: string;
  title: string;
  sanitized_title?: string | null;
  company_name: string;
  location: string;
  remote: boolean;
  url: string;
  description: string;
  tags: string[];
  job_types: string[];
  salary_min?: number | null;
  salary_max?: number | null;
  salary_currency?: string | null;
  published_at: string;
  content_hash: string;
  company?: Company | null;
  created_at: string;
  updated_at: string;
}

export interface JobFilterParams {
  keywords?: string;
  location?: string;
  remote_only?: boolean;
  job_type?: string;
  min_salary?: number;
  limit?: number;
  offset?: number;
}
