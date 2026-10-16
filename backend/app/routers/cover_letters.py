"""Cover Letter Generator Router."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.cover_letter import CoverLetter
from app.models.job import Job
from app.models.user import User
from app.schemas.cover_letter import (
    CoverLetterRead,
    GenerateCoverLetterRequest,
    PositioningStrategyInfo,
    UpdateCoverLetterRequest,
)
from app.services.cover_letter_service import cover_letter_service

router = APIRouter(tags=["Cover Letters"])


@router.get("/cover-letters/strategies", response_model=List[PositioningStrategyInfo])
async def list_cover_letter_strategies():
    """List the 10 engineering positioning strategies."""
    return cover_letter_service.get_available_strategies()


@router.post("/jobs/{job_id}/cover-letter", response_model=CoverLetterRead)
async def generate_cover_letter_for_job(
    job_id: uuid.UUID,
    payload: GenerateCoverLetterRequest = GenerateCoverLetterRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate or regenerate an evidence-grounded cover letter with the selected strategy."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    letter = await cover_letter_service.generate_grounded_letter(
        db=db,
        user=current_user,
        job=job,
        strategy_id_or_name=payload.strategy,
    )
    return CoverLetterRead.model_validate(letter)


@router.get("/jobs/{job_id}/cover-letter", response_model=Optional[CoverLetterRead])
async def get_cover_letter_for_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve existing cover letter generated for this job."""
    letter = db.query(CoverLetter).filter(
        CoverLetter.user_id == current_user.id,
        CoverLetter.job_id == job_id,
    ).first()

    if not letter:
        return None

    return CoverLetterRead.model_validate(letter)


@router.put("/jobs/{job_id}/cover-letter", response_model=CoverLetterRead)
async def update_cover_letter_for_job(
    job_id: uuid.UUID,
    payload: UpdateCoverLetterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save user edits to the generated cover letter."""
    letter = db.query(CoverLetter).filter(
        CoverLetter.user_id == current_user.id,
        CoverLetter.job_id == job_id,
    ).first()

    if not letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cover letter for job '{job_id}' not found. Generate one first.",
        )

    letter.content = payload.content
    db.commit()
    db.refresh(letter)
    return CoverLetterRead.model_validate(letter)
