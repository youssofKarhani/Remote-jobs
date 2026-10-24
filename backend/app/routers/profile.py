"""Candidate Profile and Evidence Bank management router."""

import re
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.config import settings
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
    CertificationCreate,
    CertificationRead,
    EducationRecordCreate,
    EducationRecordRead,
    EvidenceBankRead,
    EvidenceItemCreate,
    EvidenceItemRead,
    EvidenceItemUpdate,
    EvidenceVerificationRequest,
    EvidenceVerificationResponse,
    ExperienceRecordCreate,
    ExperienceRecordRead,
    ExperienceRecordUpdate,
    ProjectCreate,
    ProjectRead,
    SkillCreate,
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


def require_evidence_verification_feature():
    """[HIDDEN:EVIDENCE_VERIFICATION] Gate verification endpoints behind feature flag."""
    if not settings.FEATURE_EVIDENCE_VERIFICATION:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence verification feature is currently disabled.",
        )


@router.post("/evidence/verify", response_model=EvidenceVerificationResponse, dependencies=[Depends(require_evidence_verification_feature)], include_in_schema=settings.FEATURE_EVIDENCE_VERIFICATION)
@router.post("/evidence/{category}/verify", response_model=EvidenceVerificationResponse, dependencies=[Depends(require_evidence_verification_feature)], include_in_schema=settings.FEATURE_EVIDENCE_VERIFICATION)
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


@router.post("/evidence/verify-all", dependencies=[Depends(require_evidence_verification_feature)], include_in_schema=settings.FEATURE_EVIDENCE_VERIFICATION)
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


def _next_stable_id(db: Session, model_cls, user_id: uuid.UUID, prefix: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)$")
    existing_ids = [sid for (sid,) in db.query(model_cls.stable_id).filter(model_cls.user_id == user_id).all() if sid]
    max_idx = 0
    for sid in existing_ids:
        m = pattern.match(sid)
        if m:
            try:
                val = int(m.group(1))
                if val > max_idx:
                    max_idx = val
            except ValueError:
                pass
    return f"{prefix}_{(max_idx + 1):03d}"


# ---------------------------------------------------------------------------
# EvidenceItem CRUD
# ---------------------------------------------------------------------------
@router.post("/evidence", response_model=EvidenceItemRead, status_code=status.HTTP_201_CREATED)
async def create_evidence_item(
    payload: EvidenceItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a custom discrete achievement bullet point."""
    if payload.experience_record_id:
        exp = db.query(ExperienceRecord).filter(
            ExperienceRecord.id == payload.experience_record_id,
            ExperienceRecord.user_id == current_user.id,
        ).first()
        if not exp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Experience record '{payload.experience_record_id}' not found.",
            )

    stable_id = _next_stable_id(db, EvidenceItem, current_user.id, "EXP")
    item = EvidenceItem(
        user_id=current_user.id,
        experience_record_id=payload.experience_record_id,
        stable_id=stable_id,
        raw_text=payload.raw_text.strip(),
        category=payload.category,
        variants=payload.variants,
        is_verified=payload.is_verified,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return EvidenceItemRead.model_validate(item)


@router.put("/evidence/{item_id}", response_model=EvidenceItemRead)
async def update_evidence_item(
    item_id: str,
    payload: EvidenceItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edit text or variants of an evidence item."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        item_uuid = None

    q = db.query(EvidenceItem).filter(EvidenceItem.user_id == current_user.id)
    if item_uuid:
        item = q.filter((EvidenceItem.id == item_uuid) | (EvidenceItem.stable_id == item_id)).first()
    else:
        item = q.filter(EvidenceItem.stable_id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence item '{item_id}' not found.",
        )

    if payload.raw_text is not None:
        item.raw_text = payload.raw_text.strip()
    if payload.category is not None:
        item.category = payload.category
    if payload.variants is not None:
        item.variants = payload.variants
    if payload.is_verified is not None:
        item.is_verified = payload.is_verified

    db.commit()
    db.refresh(item)
    return EvidenceItemRead.model_validate(item)


@router.delete("/evidence/{item_id}")
async def delete_evidence_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an erroneous or obsolete bullet point."""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        item_uuid = None

    q = db.query(EvidenceItem).filter(EvidenceItem.user_id == current_user.id)
    if item_uuid:
        item = q.filter((EvidenceItem.id == item_uuid) | (EvidenceItem.stable_id == item_id)).first()
    else:
        item = q.filter(EvidenceItem.stable_id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence item '{item_id}' not found.",
        )

    db.delete(item)
    db.commit()
    return {"status": "deleted", "id": item_id}


# ---------------------------------------------------------------------------
# ExperienceRecord CRUD
# ---------------------------------------------------------------------------
@router.post("/experiences", response_model=ExperienceRecordRead, status_code=status.HTTP_201_CREATED)
async def create_experience_record(
    payload: ExperienceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new work experience record."""
    exp = ExperienceRecord(
        user_id=current_user.id,
        company_name=payload.company_name.strip(),
        role_title=payload.role_title.strip(),
        location=payload.location,
        start_date=payload.start_date,
        end_date=payload.end_date,
        is_current=payload.is_current,
        description=payload.description,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return ExperienceRecordRead(
        id=exp.id,
        company_name=exp.company_name,
        role_title=exp.role_title,
        location=exp.location,
        start_date=exp.start_date,
        end_date=exp.end_date,
        is_current=exp.is_current,
        description=exp.description,
        display_order=exp.display_order,
        bullets=[],
    )


@router.put("/experiences/{id}", response_model=ExperienceRecordRead)
async def update_experience_record(
    id: uuid.UUID,
    payload: ExperienceRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing work experience record."""
    exp = db.query(ExperienceRecord).filter(
        ExperienceRecord.id == id,
        ExperienceRecord.user_id == current_user.id,
    ).first()
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience record '{id}' not found.",
        )

    if payload.company_name is not None:
        exp.company_name = payload.company_name.strip()
    if payload.role_title is not None:
        exp.role_title = payload.role_title.strip()
    if payload.location is not None:
        exp.location = payload.location
    if payload.start_date is not None:
        exp.start_date = payload.start_date
    if payload.end_date is not None:
        exp.end_date = payload.end_date
    if payload.is_current is not None:
        exp.is_current = payload.is_current
    if payload.description is not None:
        exp.description = payload.description

    db.commit()
    db.refresh(exp)

    bullets = db.query(EvidenceItem).filter(
        EvidenceItem.user_id == current_user.id,
        EvidenceItem.experience_record_id == exp.id,
    ).order_by(EvidenceItem.display_order).all()

    return ExperienceRecordRead(
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


@router.delete("/experiences/{id}")
async def delete_experience_record(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a work experience record and associated evidence bullets."""
    exp = db.query(ExperienceRecord).filter(
        ExperienceRecord.id == id,
        ExperienceRecord.user_id == current_user.id,
    ).first()
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience record '{id}' not found.",
        )

    db.query(EvidenceItem).filter(EvidenceItem.experience_record_id == exp.id).delete()
    db.delete(exp)
    db.commit()
    return {"status": "deleted", "id": str(id)}


# ---------------------------------------------------------------------------
# Skills CRUD
# ---------------------------------------------------------------------------
@router.post("/skills", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
async def create_skill(
    payload: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new skill to candidate evidence bank."""
    stable_id = _next_stable_id(db, Skill, current_user.id, "SKILL")
    skill = Skill(
        user_id=current_user.id,
        stable_id=stable_id,
        name=payload.name.strip(),
        category=payload.category,
        proficiency=payload.proficiency,
        years_of_experience=payload.years_of_experience,
        is_verified=payload.is_verified,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return SkillRead.model_validate(skill)


@router.delete("/skills/{id}")
async def delete_skill(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a skill by ID or stable_id."""
    try:
        item_uuid = uuid.UUID(id)
    except ValueError:
        item_uuid = None

    q = db.query(Skill).filter(Skill.user_id == current_user.id)
    if item_uuid:
        skill = q.filter((Skill.id == item_uuid) | (Skill.stable_id == id)).first()
    else:
        skill = q.filter(Skill.stable_id == id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{id}' not found.",
        )

    db.delete(skill)
    db.commit()
    return {"status": "deleted", "id": id}


# ---------------------------------------------------------------------------
# Projects CRUD
# ---------------------------------------------------------------------------
@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a project to candidate evidence bank."""
    stable_id = _next_stable_id(db, Project, current_user.id, "PROJ")
    proj = Project(
        user_id=current_user.id,
        stable_id=stable_id,
        title=payload.title.strip(),
        category=payload.category,
        description=payload.description.strip(),
        technologies=payload.technologies,
        url=payload.url,
        github_url=payload.github_url,
        is_verified=payload.is_verified,
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return ProjectRead.model_validate(proj)


@router.delete("/projects/{id}")
async def delete_project(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project by ID or stable_id."""
    try:
        item_uuid = uuid.UUID(id)
    except ValueError:
        item_uuid = None

    q = db.query(Project).filter(Project.user_id == current_user.id)
    if item_uuid:
        proj = q.filter((Project.id == item_uuid) | (Project.stable_id == id)).first()
    else:
        proj = q.filter(Project.stable_id == id).first()

    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{id}' not found.",
        )

    db.delete(proj)
    db.commit()
    return {"status": "deleted", "id": id}


# ---------------------------------------------------------------------------
# Certifications CRUD
# ---------------------------------------------------------------------------
@router.post("/certifications", response_model=CertificationRead, status_code=status.HTTP_201_CREATED)
async def create_certification(
    payload: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a certification to candidate evidence bank."""
    stable_id = _next_stable_id(db, Certification, current_user.id, "CERT")
    cert = Certification(
        user_id=current_user.id,
        stable_id=stable_id,
        name=payload.name.strip(),
        issuing_organization=payload.issuing_organization.strip(),
        issue_date=payload.issue_date,
        expiration_date=payload.expiration_date,
        credential_id=payload.credential_id,
        credential_url=payload.credential_url,
        is_verified=payload.is_verified,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return CertificationRead.model_validate(cert)


@router.delete("/certifications/{id}")
async def delete_certification(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a certification by ID or stable_id."""
    try:
        item_uuid = uuid.UUID(id)
    except ValueError:
        item_uuid = None

    q = db.query(Certification).filter(Certification.user_id == current_user.id)
    if item_uuid:
        cert = q.filter((Certification.id == item_uuid) | (Certification.stable_id == id)).first()
    else:
        cert = q.filter(Certification.stable_id == id).first()

    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certification '{id}' not found.",
        )

    db.delete(cert)
    db.commit()
    return {"status": "deleted", "id": id}


# ---------------------------------------------------------------------------
# Education CRUD
# ---------------------------------------------------------------------------
@router.post("/education", response_model=EducationRecordRead, status_code=status.HTTP_201_CREATED)
async def create_education(
    payload: EducationRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add education record to candidate evidence bank."""
    stable_id = _next_stable_id(db, EducationRecord, current_user.id, "EDU")
    edu = EducationRecord(
        user_id=current_user.id,
        stable_id=stable_id,
        institution=payload.institution.strip(),
        degree=payload.degree.strip(),
        field_of_study=payload.field_of_study.strip(),
        start_date=payload.start_date,
        end_date=payload.end_date,
        grade=payload.grade,
        activities=payload.activities,
        is_verified=payload.is_verified,
    )
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return EducationRecordRead.model_validate(edu)


@router.delete("/education/{id}")
async def delete_education(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete education record by ID or stable_id."""
    try:
        item_uuid = uuid.UUID(id)
    except ValueError:
        item_uuid = None

    q = db.query(EducationRecord).filter(EducationRecord.user_id == current_user.id)
    if item_uuid:
        edu = q.filter((EducationRecord.id == item_uuid) | (EducationRecord.stable_id == id)).first()
    else:
        edu = q.filter(EducationRecord.stable_id == id).first()

    if not edu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Education record '{id}' not found.",
        )

    db.delete(edu)
    db.commit()
    return {"status": "deleted", "id": id}

