"""Job Normalization and Multi-Level Deduplication Engine.

Ensures no duplicate job postings exist across multiple runs or diverse source providers
using canonical URL deduplication and SHA-256 content hashing.
"""

import hashlib
import re
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.job import Company, Job, JobSource, JobSourceRecord
from app.protocols.job_source import RawJobDTO


def compute_content_hash(url: str, title: str, company: str, location: str) -> str:
    """Computes a deterministic SHA-256 hash for job deduplication.
    
    1. Canonical URL (stripped of query parameters and lowercase).
    2. Normalized title (stripped of gender markers, brackets, extra whitespace).
    3. Normalized company name (lowercase, stripped).
    4. Normalized location (lowercase, stripped).
    """
    norm_title = re.sub(r"\(.*?\)|\[.*?\]", "", title).lower().strip()
    norm_title = re.sub(r"\s+", " ", norm_title)
    norm_company = company.lower().strip()
    norm_loc = location.lower().strip()
    norm_url = url.split("?")[0].lower().strip()

    payload = f"{norm_url}|{norm_title}|{norm_company}|{norm_loc}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sanitize_job_title(title: str) -> str:
    """Clean job title by stripping recruitment noise, gender markers (m/w/d), and brackets."""
    cleaned = re.sub(r"\(m/w/d\)|\(m/f/d\)|\(gn\)|\(d/m/w\)|\(all genders\)", "", title, flags=re.I)
    cleaned = re.sub(r"\[.*?\]|\(.*?\)", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or title


class JobDeduplicationService:
    """Service to normalize raw vendor job listings and persist deduplicated canonical records."""

    @staticmethod
    def get_or_create_source(db: Session, source_name: str, base_url: str = "https://arbeitnow.com/api/job-board-api") -> JobSource:
        """Find or initialize a registered JobSource in database."""
        source = db.query(JobSource).filter(JobSource.name == source_name).first()
        if not source:
            source = JobSource(
                name=source_name,
                base_url=base_url,
                is_active=True,
            )
            db.add(source)
            db.flush()
        return source

    @staticmethod
    def get_or_create_company(db: Session, company_name: str) -> Company:
        """Find or initialize canonical Company record."""
        norm_name = company_name.lower().strip()
        company = db.query(Company).filter(Company.normalized_name == norm_name).first()
        if not company:
            company = Company(
                name=company_name.strip(),
                normalized_name=norm_name,
            )
            db.add(company)
            db.flush()
        return company

    def ingest_raw_jobs(
        self,
        db: Session,
        raw_jobs: List[RawJobDTO],
        source_name: str = "arbeitnow",
    ) -> Dict[str, Any]:
        """Ingest, deduplicate, and persist raw jobs into canonical Job and JobSourceRecord tables."""
        source = self.get_or_create_source(db, source_name)
        new_inserted = 0
        duplicates_skipped = 0

        for raw in raw_jobs:
            content_hash = compute_content_hash(
                url=raw.external_url,
                title=raw.title,
                company=raw.company_name,
                location=raw.location,
            )
            clean_url = raw.external_url.split("?")[0].strip()

            # Check if Job already exists by hash, canonical url, or slug
            existing_job = (
                db.query(Job)
                .filter(
                    (Job.content_hash == content_hash)
                    | (Job.url == clean_url)
                    | (Job.slug == raw.external_id)
                )
                .first()
            )

            if existing_job:
                duplicates_skipped += 1
                # Check if this source record is already linked
                existing_record = (
                    db.query(JobSourceRecord)
                    .filter(
                        JobSourceRecord.source_id == source.id,
                        JobSourceRecord.external_id == raw.external_id,
                    )
                    .first()
                )
                if not existing_record:
                    source_record = JobSourceRecord(
                        job_id=existing_job.id,
                        source_id=source.id,
                        external_id=raw.external_id,
                        external_url=raw.external_url,
                        raw_payload=raw.raw_data or {},
                    )
                    db.add(source_record)
            else:
                # New canonical job
                company = self.get_or_create_company(db, raw.company_name)
                sanitized_title = sanitize_job_title(raw.title)

                new_job = Job(
                    company_id=company.id,
                    slug=raw.external_id,
                    title=raw.title,
                    sanitized_title=sanitized_title,
                    company_name=raw.company_name,
                    location=raw.location,
                    remote=raw.remote,
                    url=clean_url,
                    description=raw.description,
                    tags=raw.tags or [],
                    job_types=raw.job_types or [],
                    published_at=raw.published_at,
                    content_hash=content_hash,
                )
                db.add(new_job)
                db.flush()  # populate new_job.id

                source_record = JobSourceRecord(
                    job_id=new_job.id,
                    source_id=source.id,
                    external_id=raw.external_id,
                    external_url=raw.external_url,
                    raw_payload=raw.raw_data or {},
                )
                db.add(source_record)
                new_inserted += 1

        db.commit()

        return {
            "source": source_name,
            "total_fetched": len(raw_jobs),
            "new_jobs_inserted": new_inserted,
            "duplicates_skipped": duplicates_skipped,
        }


# Global deduplication service instance
job_deduplication_service = JobDeduplicationService()
