"""Jobs discovery, filtering, and external synchronization router."""

import uuid
from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.integrations.arbeitnow import ArbeitnowSource
from app.models.job import Job
from app.models.preference import CandidatePreference
from app.models.user import User
from app.schemas.job import (
    JobRead,
    JobSyncRequest,
    JobSyncResponse,
    PaginatedJobsResponse,
    PaginationMeta,
)
from app.services.job_deduplication import job_deduplication_service
from app.services.job_filtering import deterministic_filter_service

router = APIRouter(prefix="/jobs", tags=["Job Discovery"])


@router.get("", response_model=PaginatedJobsResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search keyword in title or company"),
    country: Optional[str] = Query(None, description="Filter by location/country"),
    remote_only: Optional[bool] = Query(None, description="Filter remote only"),
    job_types: Optional[str] = Query(None, description="Comma-separated job types"),
    sort_by: str = Query("newest", pattern="^(newest|oldest|company)$"),
    apply_preferences: bool = Query(False, description="Filter by candidate stored preferences"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve paginated deduplicated job listings with optional candidate preference filtering."""
    query = db.query(Job)

    # Apply URL query filters
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            Job.title.ilike(term) | Job.company_name.ilike(term) | Job.description.ilike(term)
        )

    if country and country.strip():
        query = query.filter(Job.location.ilike(f"%{country.strip()}%"))

    if remote_only is True:
        query = query.filter(Job.remote.is_(True))

    # Apply sorting
    if sort_by == "oldest":
        query = query.order_by(Job.published_at.asc())
    elif sort_by == "company":
        query = query.order_by(Job.company_name.asc(), Job.published_at.desc())
    else:
        query = query.order_by(Job.published_at.desc())

    all_matching = query.all()

    # Apply candidate deterministic preference filtering if requested
    if apply_preferences:
        pref = db.query(CandidatePreference).filter(CandidatePreference.user_id == current_user.id).first()
        filtered = deterministic_filter_service.filter_jobs(all_matching, pref)
    else:
        filtered = all_matching

    total_items = len(filtered)
    total_pages = max(1, ceil(total_items / limit))
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_items = filtered[start_idx:end_idx]

    job_reads = [JobRead.model_validate(j) for j in page_items]

    return PaginatedJobsResponse(
        items=job_reads,
        pagination=PaginationMeta(
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            limit=limit,
        ),
    )


@router.get("/{job_id_or_slug}", response_model=JobRead)
async def get_job_detail(
    job_id_or_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get single job posting details by UUID or slug."""
    job = None
    try:
        j_uuid = uuid.UUID(job_id_or_slug)
        job = db.query(Job).filter(Job.id == j_uuid).first()
    except ValueError:
        pass

    if not job:
        job = db.query(Job).filter(Job.slug == job_id_or_slug).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job posting '{job_id_or_slug}' not found.",
        )

    return JobRead.model_validate(job)


@router.post("/sync", response_model=JobSyncResponse)
async def sync_external_jobs(
    sync_req: JobSyncRequest = JobSyncRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger external job ingestion from Arbeitnow with multi-level deduplication."""
    if sync_req.source.lower() == "arbeitnow":
        source_client = ArbeitnowSource()
        try:
            raw_jobs = await source_client.fetch_jobs(page=1)
            stats = job_deduplication_service.ingest_raw_jobs(
                db=db,
                raw_jobs=raw_jobs,
                source_name="arbeitnow",
            )
            return JobSyncResponse(
                status="sync_complete",
                source="arbeitnow",
                fetched_count=stats.get("total_fetched", len(raw_jobs)),
                new_jobs_inserted=stats.get("new_jobs_inserted", 0),
                duplicates_skipped=stats.get("duplicates_skipped", 0),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch jobs from {sync_req.source}: {str(e)}",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported job source '{sync_req.source}'. Supported sources: ['arbeitnow'].",
        )
