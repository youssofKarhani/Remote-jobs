"""Candidate Preferences router for deterministic matching constraints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.preference import CandidatePreference
from app.models.user import User
from app.schemas.preference import (
    CandidatePreferenceRead,
    CandidatePreferenceUpdate,
)

router = APIRouter(prefix="/preferences", tags=["Candidate Preferences"])


@router.get("", response_model=CandidatePreferenceRead)
async def get_candidate_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve candidate deterministic job search preferences."""
    pref = db.query(CandidatePreference).filter(CandidatePreference.user_id == current_user.id).first()
    if not pref:
        pref = CandidatePreference(
            user_id=current_user.id,
            target_roles=[],
            locations=["Germany"],
            remote_only=False,
            hybrid_allowed=True,
            onsite_allowed=True,
            job_types=["Full Time"],
            languages=["English"],
            excluded_companies=[],
            excluded_keywords=[],
            preferred_industries=[],
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)

    return pref


@router.put("", response_model=CandidatePreferenceRead)
@router.post("", response_model=CandidatePreferenceRead)
async def update_candidate_preferences(
    pref_update: CandidatePreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update or upsert candidate deterministic job search preferences."""
    pref = db.query(CandidatePreference).filter(CandidatePreference.user_id == current_user.id).first()
    if not pref:
        pref = CandidatePreference(user_id=current_user.id)
        db.add(pref)

    if pref_update.target_roles is not None:
        pref.target_roles = pref_update.target_roles
    if pref_update.locations is not None:
        pref.locations = pref_update.locations
    if pref_update.remote_only is not None:
        pref.remote_only = pref_update.remote_only
    if pref_update.hybrid_allowed is not None:
        pref.hybrid_allowed = pref_update.hybrid_allowed
    if pref_update.onsite_allowed is not None:
        pref.onsite_allowed = pref_update.onsite_allowed
    if pref_update.job_types is not None:
        pref.job_types = pref_update.job_types
    if pref_update.min_salary is not None:
        pref.min_salary = pref_update.min_salary
    if pref_update.salary_currency is not None:
        pref.salary_currency = pref_update.salary_currency
    if pref_update.max_seniority is not None:
        pref.max_seniority = pref_update.max_seniority
    if pref_update.languages is not None:
        pref.languages = pref_update.languages
    if pref_update.excluded_companies is not None:
        pref.excluded_companies = pref_update.excluded_companies
    if pref_update.excluded_keywords is not None:
        pref.excluded_keywords = pref_update.excluded_keywords
    if pref_update.preferred_industries is not None:
        pref.preferred_industries = pref_update.preferred_industries

    db.commit()
    db.refresh(pref)
    return pref
