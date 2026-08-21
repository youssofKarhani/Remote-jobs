"""Candidate Profile and Evidence Bank management router."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.evidence import (
    Certification,
    EducationRecord,
    EvidenceItem,
    ExperienceRecord,
    Project,
    Skill,
)
from app.models.profile import CandidateProfile
from app.models.user import User
from app.schemas.profile import (
    CandidateProfileRead,
    CandidateProfileUpdate,
    CertificationRead,
    EducationRecordRead,
    EvidenceBankRead,
    EvidenceItemRead,
    EvidenceItemUpdate,
    EvidenceVerificationRequest,
    EvidenceVerificationResponse,
    ExperienceRecordRead,
    ProjectRead,
    SkillRead,
)

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])


def _build_evidence_bank(db: Session, user_id: uuid.UUID) -> EvidenceBankRead:
    """Helper to query all candidate evidence bank entities scoped to user."""
    # 1. Experience records with nested bullets
    exp_records = (
        db.query(ExperienceRecord)
        .filter(ExperienceRecord.user_id == user_id)
        .order_by(ExperienceRecord.display_order)
        .all()
    )
    exp_reads = []
    for exp in exp_records:
        bullets = (
            db.query(EvidenceItem)
            .filter(
                EvidenceItem.user_id == user_id,
                EvidenceItem.experience_record_id == exp.id,
            )
            .order_by(EvidenceItem.display_order)
            .all()
        )
        exp_reads.append(
            ExperienceRecordRead(
                id=exp.id,
                company_name=exp.company_name,
                role_title=exp.role_title,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                display_order=exp.display_order,
                bullets=[EvidenceItemRead.model_validate(b) for b in bullets],
            )
        )

    # 2. Skills
    skills = (
        db.query(Skill)
        .filter(Skill.user_id == user_id)
        .order_by(Skill.display_order)
        .all()
    )

    # 3. Projects
    projects = (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.display_order)
        .all()
    )

    # 4. Certifications
    certs = (
        db.query(Certification)
        .filter(Certification.user_id == user_id)
        .order_by(Certification.display_order)
        .all()
    )

    # 5. Education
    education = (
        db.query(EducationRecord)
        .filter(EducationRecord.user_id == user_id)
        .order_by(EducationRecord.display_order)
        .all()
    )

    return EvidenceBankRead(
        experiences=exp_reads,
        skills=[SkillRead.model_validate(s) for s in skills],
        projects=[ProjectRead.model_validate(p) for p in projects],
        certifications=[CertificationRead.model_validate(c) for c in certs],
        education=[EducationRecordRead.model_validate(e) for e in education],
    )


@router.get("", response_model=CandidateProfileRead)
async def get_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full canonical candidate profile and structured Evidence Bank."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            headline="Software Professional",
            is_verified=False,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    evidence_bank = _build_evidence_bank(db, current_user.id)

    return CandidateProfileRead(
        id=profile.id,
        user_id=profile.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        headline=profile.headline,
        summary=profile.summary,
        phone=profile.phone,
        location=profile.location,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        portfolio_url=profile.portfolio_url,
        raw_cv_text=profile.raw_cv_text,
        is_verified=profile.is_verified,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        evidence_bank=evidence_bank,
    )


@router.put("", response_model=CandidateProfileRead)
@router.patch("", response_model=CandidateProfileRead)
async def update_candidate_profile(
    profile_update: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update canonical candidate profile metadata."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
        db.add(current_user)

    if profile_update.headline is not None:
        profile.headline = profile_update.headline
    if profile_update.summary is not None:
        profile.summary = profile_update.summary
    if profile_update.phone is not None:
        profile.phone = profile_update.phone
    if profile_update.location is not None:
        profile.location = profile_update.location
    if profile_update.linkedin_url is not None:
        profile.linkedin_url = profile_update.linkedin_url
    if profile_update.github_url is not None:
        profile.github_url = profile_update.github_url
    if profile_update.portfolio_url is not None:
        profile.portfolio_url = profile_update.portfolio_url

    db.commit()
    db.refresh(profile)

    evidence_bank = _build_evidence_bank(db, current_user.id)

    return CandidateProfileRead(
        id=profile.id,
        user_id=profile.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        headline=profile.headline,
        summary=profile.summary,
        phone=profile.phone,
        location=profile.location,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        portfolio_url=profile.portfolio_url,
        raw_cv_text=profile.raw_cv_text,
        is_verified=profile.is_verified,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        evidence_bank=evidence_bank,
    )


@router.post("/evidence/verify", response_model=EvidenceVerificationResponse)
@router.post("/evidence/{category}/verify", response_model=EvidenceVerificationResponse)
async def verify_evidence_item(
    payload: EvidenceVerificationRequest,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle or set the verification status of a specific candidate evidence item."""
    item_id = payload.item_id.strip()
    item_type = category or payload.item_type

    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        item_uuid = None

    # 1. Try EvidenceItem (EXP_xxx or UUID)
    q_ev = db.query(EvidenceItem).filter(EvidenceItem.user_id == current_user.id)
    if item_uuid:
        ev_item = q_ev.filter((EvidenceItem.stable_id == item_id) | (EvidenceItem.id == item_uuid)).first()
    else:
        ev_item = q_ev.filter(EvidenceItem.stable_id == item_id).first()

    if ev_item:
        ev_item.is_verified = payload.is_verified
        db.commit()
        return EvidenceVerificationResponse(
            item_id=ev_item.stable_id,
            item_type="experience_bullet",
            is_verified=ev_item.is_verified,
        )

    # 2. Try Skill (SKILL_xxx or UUID)
    q_sk = db.query(Skill).filter(Skill.user_id == current_user.id)
    if item_uuid:
        skill_item = q_sk.filter((Skill.stable_id == item_id) | (Skill.id == item_uuid)).first()
    else:
        skill_item = q_sk.filter(Skill.stable_id == item_id).first()

    if skill_item:
        skill_item.is_verified = payload.is_verified
        db.commit()
        return EvidenceVerificationResponse(
            item_id=skill_item.stable_id,
            item_type="skill",
            is_verified=skill_item.is_verified,
        )

    # 3. Try Project (PROJ_xxx or UUID)
    q_pr = db.query(Project).filter(Project.user_id == current_user.id)
    if item_uuid:
        proj_item = q_pr.filter((Project.stable_id == item_id) | (Project.id == item_uuid)).first()
    else:
        proj_item = q_pr.filter(Project.stable_id == item_id).first()

    if proj_item:
        proj_item.is_verified = payload.is_verified
        db.commit()
        return EvidenceVerificationResponse(
            item_id=proj_item.stable_id,
            item_type="project",
            is_verified=proj_item.is_verified,
        )

    # 4. Try Certification (CERT_xxx or UUID)
    q_ce = db.query(Certification).filter(Certification.user_id == current_user.id)
    if item_uuid:
        cert_item = q_ce.filter((Certification.stable_id == item_id) | (Certification.id == item_uuid)).first()
    else:
        cert_item = q_ce.filter(Certification.stable_id == item_id).first()

    if cert_item:
        cert_item.is_verified = payload.is_verified
        db.commit()
        return EvidenceVerificationResponse(
            item_id=cert_item.stable_id,
            item_type="certification",
            is_verified=cert_item.is_verified,
        )

    # 5. Try EducationRecord (EDU_xxx or UUID)
    q_ed = db.query(EducationRecord).filter(EducationRecord.user_id == current_user.id)
    if item_uuid:
        edu_item = q_ed.filter((EducationRecord.stable_id == item_id) | (EducationRecord.id == item_uuid)).first()
    else:
        edu_item = q_ed.filter(EducationRecord.stable_id == item_id).first()

    if edu_item:
        edu_item.is_verified = payload.is_verified
        db.commit()
        return EvidenceVerificationResponse(
            item_id=edu_item.stable_id,
            item_type="education",
            is_verified=edu_item.is_verified,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Evidence item '{item_id}' not found for authenticated user.",
    )


@router.post("/evidence/verify-all")
async def verify_all_evidence_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all unverified candidate evidence items as verified."""
    db.query(EvidenceItem).filter(EvidenceItem.user_id == current_user.id).update({"is_verified": True})
    db.query(Skill).filter(Skill.user_id == current_user.id).update({"is_verified": True})
    db.query(Project).filter(Project.user_id == current_user.id).update({"is_verified": True})
    db.query(Certification).filter(Certification.user_id == current_user.id).update({"is_verified": True})
    db.query(EducationRecord).filter(EducationRecord.user_id == current_user.id).update({"is_verified": True})
    
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if profile:
        profile.is_verified = True

    db.commit()
    return {"status": "success", "message": "All evidence items marked as verified."}
