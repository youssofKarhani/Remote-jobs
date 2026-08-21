"""Deterministic Job Filtering Service matching candidate preferences without AI cost."""

import re
from typing import List, Optional
from app.models.job import Job
from app.models.preference import CandidatePreference

JOB_TYPE_MAPPING = {
    "Full Time": ["vollzeit", "full-time", "full time", "festanstellung"],
    "Part Time": ["teilzeit", "part-time", "part time"],
    "Internship": ["praktikum", "internship", "intern", "praktikant"],
    "Working Student": ["werkstudent", "working student", "studentische aushilfe", "werkstudententätigkeit"],
}


class DeterministicFilterService:
    """Fast, zero-cost deterministic filtering of jobs against CandidatePreference criteria."""

    @staticmethod
    def _make_word_pattern(term: str) -> str:
        """Create word boundary regex pattern resilient to symbols like C++, C#, .NET."""
        escaped = re.escape(term.strip().lower())
        return rf"(?<!\w){escaped}(?!\w)"

    @classmethod
    def is_job_eligible(cls, job: Job, pref: Optional[CandidatePreference]) -> bool:
        """Determine whether a job satisfies all deterministic preference constraints.
        
        Returns True if pref is None or empty.
        """
        if not pref:
            return True

        # 1. Excluded Companies Check (case-insensitive substring)
        if pref.excluded_companies:
            job_comp = (job.company_name or "").lower().strip()
            for exc in pref.excluded_companies:
                if exc and exc.lower().strip() in job_comp:
                    return False

        # 2. Excluded Keywords Check (word boundary regex on title and description)
        if pref.excluded_keywords:
            title_lower = (job.title or "").lower()
            desc_lower = (job.description or "").lower()
            for kw in pref.excluded_keywords:
                if kw and kw.strip():
                    pattern = cls._make_word_pattern(kw)
                    if re.search(pattern, title_lower) or re.search(pattern, desc_lower):
                        return False

        # 3. Remote Policy Enforcement
        if pref.remote_only and not job.remote:
            return False

        # 4. Location Match Check (applies when not remote or when location criteria defined)
        if pref.locations and not job.remote:
            job_loc = (job.location or "").lower()
            loc_matched = False
            for loc in pref.locations:
                if loc and loc.strip():
                    pattern = cls._make_word_pattern(loc)
                    if re.search(pattern, job_loc):
                        loc_matched = True
                        break
            if not loc_matched:
                return False

        # 5. Job Type Match Check (multi-lingual German & English matching)
        if pref.job_types:
            type_matched = False
            target_keywords = []
            for jt in pref.job_types:
                mapped = JOB_TYPE_MAPPING.get(jt, [jt.lower()])
                target_keywords.extend(mapped)

            title_lower = (job.title or "").lower()
            job_types_list = job.job_types or []

            for kw in target_keywords:
                pattern = cls._make_word_pattern(kw)
                if re.search(pattern, title_lower) or any(re.search(pattern, str(t).lower()) for t in job_types_list):
                    type_matched = True
                    break

            if not type_matched:
                return False

        # 6. Target Role Keyword Matching (if specified)
        if pref.target_roles:
            role_matched = False
            title_lower = (job.title or "").lower()
            tags_list = [str(t).lower() for t in (job.tags or [])]

            for role in pref.target_roles:
                if role and role.strip():
                    pattern = cls._make_word_pattern(role)
                    if re.search(pattern, title_lower) or any(re.search(pattern, tag) for tag in tags_list):
                        role_matched = True
                        break

            if not role_matched:
                return False

        # 7. Minimum Salary Threshold Check
        if pref.min_salary is not None and job.salary_max is not None:
            if float(job.salary_max) < float(pref.min_salary):
                return False

        return True

    @classmethod
    def filter_jobs(cls, jobs: List[Job], pref: Optional[CandidatePreference]) -> List[Job]:
        """Filter a list of jobs against candidate preferences."""
        if not pref:
            return jobs
        return [job for job in jobs if cls.is_job_eligible(job, pref)]


deterministic_filter_service = DeterministicFilterService()
