"""Strict Evidence ID Validation Engine and Safe Text Resolver.

Enforces Non-Negotiable Invariants:
1. LLMs may only select evidence by stable ID; they cannot create or modify factual CV bullets.
2. selected_ids ⊆ allowed_ids is strictly enforced in Python and database queries.
3. Multi-tenant scoping guarantees User A can never select or resolve User B's evidence.
"""

import uuid
from typing import Any, Dict, List, Optional, Set
from sqlalchemy.orm import Session

from app.models.evidence import (
    Certification,
    EducationRecord,
    EvidenceItem,
    Project,
    Skill,
)


class EvidenceValidationError(ValueError):
    """Raised when an LLM or client provides invalid, non-existent, or cross-tenant evidence IDs."""
    pass


def validate_selected_evidence_ids(
    selected_ids: List[str],
    allowed_ids: Set[str],
    max_bullets: Optional[int] = None,
) -> None:
    """Strict validation rule: selected_ids ⊆ allowed_ids.
    
    Raises EvidenceValidationError if any selected ID is not in allowed_ids,
    or if selected_ids count exceeds max_bullets limit.
    """
    if not selected_ids:
        return

    selected_set = set(selected_ids)
    invalid_ids = selected_set - allowed_ids
    if invalid_ids:
        raise EvidenceValidationError(
            f"Validation Failed: The following evidence IDs are invalid or unauthorized: {sorted(list(invalid_ids))}"
        )

    if max_bullets is not None and len(selected_ids) > max_bullets:
        raise EvidenceValidationError(
            f"Validation Failed: Selected {len(selected_ids)} bullets exceeds maximum allowed ({max_bullets})"
        )


def get_user_allowed_evidence_ids(
    db: Session,
    user_id: uuid.UUID,
    verified_only: bool = True,
) -> Set[str]:
    """Retrieve the set of all valid stable IDs belonging to the authenticated user.
    
    If verified_only=True (default), returns only verified items (is_verified=True).
    """
    allowed: Set[str] = set()

    # Query EvidenceItems (experience bullets)
    q_bullets = db.query(EvidenceItem.stable_id).filter(EvidenceItem.user_id == user_id)
    if verified_only:
        q_bullets = q_bullets.filter(EvidenceItem.is_verified.is_(True))
    for (sid,) in q_bullets.all():
        if sid:
            allowed.add(sid)

    # Query Skills
    q_skills = db.query(Skill.stable_id).filter(Skill.user_id == user_id)
    if verified_only:
        q_skills = q_skills.filter(Skill.is_verified.is_(True))
    for (sid,) in q_skills.all():
        if sid:
            allowed.add(sid)

    # Query Projects
    q_projects = db.query(Project.stable_id).filter(Project.user_id == user_id)
    if verified_only:
        q_projects = q_projects.filter(Project.is_verified.is_(True))
    for (sid,) in q_projects.all():
        if sid:
            allowed.add(sid)

    # Query Certifications
    q_certs = db.query(Certification.stable_id).filter(Certification.user_id == user_id)
    if verified_only:
        q_certs = q_certs.filter(Certification.is_verified.is_(True))
    for (sid,) in q_certs.all():
        if sid:
            allowed.add(sid)

    # Query Education Records
    q_edu = db.query(EducationRecord.stable_id).filter(EducationRecord.user_id == user_id)
    if verified_only:
        q_edu = q_edu.filter(EducationRecord.is_verified.is_(True))
    for (sid,) in q_edu.all():
        if sid:
            allowed.add(sid)

    return allowed


def resolve_verified_evidence_text(
    db: Session,
    user_id: uuid.UUID,
    selected_ids: List[str],
) -> List[Dict[str, Any]]:
    """Fetch verified database text records for given stable IDs scoped strictly by user_id.
    
    Prevents hallucination by retrieving exact stored text.
    Raises EvidenceValidationError if any selected ID cannot be found or is unverified.
    """
    if not selected_ids:
        return []

    allowed_ids = get_user_allowed_evidence_ids(db, user_id=user_id, verified_only=True)
    validate_selected_evidence_ids(selected_ids, allowed_ids)

    resolved: List[Dict[str, Any]] = []

    for sid in selected_ids:
        prefix = sid.split("_")[0] if "_" in sid else ""

        if prefix == "EXP":
            item = (
                db.query(EvidenceItem)
                .filter(EvidenceItem.user_id == user_id, EvidenceItem.stable_id == sid)
                .first()
            )
            if item:
                resolved.append({
                    "stable_id": item.stable_id,
                    "type": "experience_bullet",
                    "text": item.raw_text,
                    "category": item.category,
                    "variants": item.variants,
                })
        elif prefix == "SKILL":
            item = (
                db.query(Skill)
                .filter(Skill.user_id == user_id, Skill.stable_id == sid)
                .first()
            )
            if item:
                resolved.append({
                    "stable_id": item.stable_id,
                    "type": "skill",
                    "name": item.name,
                    "category": item.category,
                })
        elif prefix == "PROJ":
            item = (
                db.query(Project)
                .filter(Project.user_id == user_id, Project.stable_id == sid)
                .first()
            )
            if item:
                resolved.append({
                    "stable_id": item.stable_id,
                    "type": "project",
                    "title": item.title,
                    "description": item.description,
                    "technologies": item.technologies,
                })
        elif prefix == "CERT":
            item = (
                db.query(Certification)
                .filter(Certification.user_id == user_id, Certification.stable_id == sid)
                .first()
            )
            if item:
                resolved.append({
                    "stable_id": item.stable_id,
                    "type": "certification",
                    "name": item.name,
                    "issuing_organization": item.issuing_organization,
                })
        elif prefix == "EDU":
            item = (
                db.query(EducationRecord)
                .filter(EducationRecord.user_id == user_id, EducationRecord.stable_id == sid)
                .first()
            )
            if item:
                resolved.append({
                    "stable_id": item.stable_id,
                    "type": "education",
                    "institution": item.institution,
                    "degree": item.degree,
                    "field_of_study": item.field_of_study,
                })

    return resolved
