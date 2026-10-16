"""Job Matching and Compatibility Assessment Router."""

import uuid
from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.job import Job
from app.models.matching import JobMatch
from app.models.user import User
from app.schemas.matching import JobMatchRead, PaginatedMatchesResponse
from app.services.matching_service import matching_service

router = APIRouter(tags=["Job Matching"])


@router.post("/jobs/{job_id}/match", response_model=JobMatchRead)
async def assess_job_match(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger or re-calculate AI compatibility assessment for a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    match = await matching_service.assess_candidate_job(
        db=db,
        user=current_user,
        job=job,
    )
    return JobMatchRead.model_validate(match)


@router.get("/jobs/{job_id}/match", response_model=Optional[JobMatchRead])
async def get_job_match_for_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve existing match record for a job if already calculated."""
    match = db.query(JobMatch).filter(
        JobMatch.user_id == current_user.id,
        JobMatch.job_id == job_id,
    ).first()

    if not match:
        return None

    return JobMatchRead.model_validate(match)


@router.get("/matches", response_model=PaginatedMatchesResponse)
async def list_matches(
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum compatibility score"),
    status: Optional[str] = Query(None, description="Match status ('new', 'viewed', 'dismissed', 'saved')"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve candidate's assessed job matches, filterable by minimum score."""
    query = db.query(JobMatch).filter(JobMatch.user_id == current_user.id)

    if min_score is not None:
        query = query.filter(JobMatch.overall_score >= min_score)

    if status:
        query = query.filter(JobMatch.status == status)

    query = query.order_by(JobMatch.overall_score.desc(), JobMatch.matched_at.desc())

    total_items = query.count()
    total_pages = max(1, ceil(total_items / limit))
    matches = query.offset((page - 1) * limit).limit(limit).all()

    return PaginatedMatchesResponse(
        items=[JobMatchRead.model_validate(m) for m in matches],
        total_items=total_items,
        total_pages=total_pages,
        current_page=page,
        limit=limit,
    )


@router.get("/matches/{match_id}", response_model=JobMatchRead)
async def get_match_detail(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full assessment breakdown and matched evidence for a specific match."""
    match = db.query(JobMatch).filter(
        JobMatch.id == match_id,
        JobMatch.user_id == current_user.id,
    ).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match '{match_id}' not found.",
        )

    return JobMatchRead.model_validate(match)
