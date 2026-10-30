"""Provenance Validation Engine for Semantic CV Extraction.

Enforces the Core Semantic Extraction Rule:
"A semantic object without valid source provenance must not be accepted as a normal extracted candidate claim."

Validates:
1. Non-empty source_block_ids referencing legitimate layout blocks.
2. Non-empty source_pages referencing valid document pages.
3. Non-empty raw_text / raw_value verifying the factual claim exists in source.
4. Block existence against the actual ingestion run's LayoutDocument source blocks.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.semantic_cv import (
    CanonicalSemanticCV,
    ProvenanceMetadata,
    SemanticBaseEntity,
    SemanticExperience,
    SemanticPersonalInfo,
)


class ProvenanceErrorCode(str, Enum):
    MISSING_PROVENANCE = "MISSING_PROVENANCE"
    EMPTY_SOURCE_BLOCK_IDS = "EMPTY_SOURCE_BLOCK_IDS"
    INVALID_SOURCE_BLOCK_REFERENCE = "INVALID_SOURCE_BLOCK_REFERENCE"
    EMPTY_SOURCE_PAGES = "EMPTY_SOURCE_PAGES"
    EMPTY_RAW_TEXT = "EMPTY_RAW_TEXT"
    INVALID_CONFIDENCE = "INVALID_CONFIDENCE"


class ProvenanceValidationError(ValueError):
    """Raised when a semantic claim fails provenance verification."""

    def __init__(self, message: str, error_codes: Optional[List[ProvenanceErrorCode]] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_codes = error_codes or []
        self.details = details or {}


class EntityValidationResult(BaseModel):
    """Result of provenance verification for a single extracted semantic claim."""
    model_config = ConfigDict(extra="ignore")

    is_valid: bool
    entity_type: str
    errors: List[str] = Field(default_factory=list)
    error_codes: List[ProvenanceErrorCode] = Field(default_factory=list)
    entity_summary: str = ""


class CanonicalCVValidationReport(BaseModel):
    """Document-wide provenance validation audit report."""
    model_config = ConfigDict(extra="ignore")

    is_valid: bool = Field(description="True if all claims have valid source provenance")
    total_entities_checked: int = 0
    accepted_entities_count: int = 0
    rejected_entities_count: int = 0
    accepted_cv: Optional[CanonicalSemanticCV] = None
    rejected_claims: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of rejected claims with provenance failure details"
    )
    warnings: List[str] = Field(default_factory=list)


def validate_entity_provenance(
    entity: Any,
    valid_block_ids: Optional[Set[str]] = None,
    entity_name: str = "SemanticEntity",
) -> EntityValidationResult:
    """Validate that an individual semantic object satisfies strict source provenance."""
    errors: List[str] = []
    error_codes: List[ProvenanceErrorCode] = []

    # 1. Provenance attribute presence
    prov: Optional[ProvenanceMetadata] = getattr(entity, "provenance", None)
    if prov is None or not isinstance(prov, ProvenanceMetadata):
        return EntityValidationResult(
            is_valid=False,
            entity_type=entity_name,
            errors=["Entity is missing required ProvenanceMetadata container."],
            error_codes=[ProvenanceErrorCode.MISSING_PROVENANCE],
            entity_summary=str(entity)[:100],
        )

    # 2. Source block IDs must be non-empty
    if not prov.source_block_ids or not any(bid.strip() for bid in prov.source_block_ids):
        errors.append("source_block_ids is empty; semantic claim has no physical document block anchor.")
        error_codes.append(ProvenanceErrorCode.EMPTY_SOURCE_BLOCK_IDS)
    elif valid_block_ids is not None:
        # Check against ground-truth block IDs from LayoutDocument
        invalid_refs = [bid for bid in prov.source_block_ids if bid not in valid_block_ids]
        if invalid_refs:
            errors.append(f"source_block_ids references non-existent block IDs: {invalid_refs}.")
            error_codes.append(ProvenanceErrorCode.INVALID_SOURCE_BLOCK_REFERENCE)

    # 3. Source pages must be non-empty
    if not prov.source_pages or not any(p > 0 for p in prov.source_pages):
        errors.append("source_pages is empty or invalid.")
        error_codes.append(ProvenanceErrorCode.EMPTY_SOURCE_PAGES)

    # 4. Raw text or raw value must be present
    has_raw = bool(prov.raw_text.strip()) or bool(prov.raw_value and prov.raw_value.strip())
    # If the entity itself has raw_value or raw_text, check that too
    entity_raw = getattr(entity, "raw_value", None) or getattr(entity, "raw_text", None)
    if not has_raw and not entity_raw:
        errors.append("No verbatim raw_text or raw_value provided to support claim.")
        error_codes.append(ProvenanceErrorCode.EMPTY_RAW_TEXT)

    # 5. Extraction confidence bounds
    if prov.extraction_confidence < 0.0 or prov.extraction_confidence > 1.0:
        errors.append(f"extraction_confidence {prov.extraction_confidence} is outside [0.0, 1.0].")
        error_codes.append(ProvenanceErrorCode.INVALID_CONFIDENCE)

    # Summary representation
    summary = prov.raw_value or prov.raw_text or getattr(entity, "raw_value", "") or entity_name

    return EntityValidationResult(
        is_valid=(len(errors) == 0),
        entity_type=entity_name,
        errors=errors,
        error_codes=error_codes,
        entity_summary=str(summary)[:100],
    )


def validate_canonical_cv(
    cv: CanonicalSemanticCV,
    valid_block_ids: Optional[Set[str]] = None,
    strict: bool = False,
) -> CanonicalCVValidationReport:
    """Validate complete CanonicalSemanticCV against physical layout blocks.

    In accordance with the Semantic Extraction Rule:
    - Any entity without valid source provenance is rejected and removed from accepted_cv.
    - If strict=True and any claim fails, raises ProvenanceValidationError.
    """
    accepted_personal = cv.personal_info
    accepted_experiences: List[SemanticExperience] = []
    accepted_education = []
    accepted_certifications = []
    accepted_projects = []
    accepted_skills = []
    accepted_languages = []
    accepted_awards = []
    accepted_publications = []
    accepted_volunteering = []
    accepted_unknown = []

    rejected_claims: List[Dict[str, Any]] = []
    total_checked = 0

    def check_entity(item: Any, entity_type: str) -> bool:
        nonlocal total_checked
        total_checked += 1
        res = validate_entity_provenance(item, valid_block_ids=valid_block_ids, entity_name=entity_type)
        if not res.is_valid:
            rejected_claims.append({
                "entity_type": entity_type,
                "summary": res.entity_summary,
                "errors": res.errors,
                "error_codes": [c.value for c in res.error_codes],
                "item_repr": item.model_dump() if hasattr(item, "model_dump") else str(item),
            })
            return False
        return True

    # Personal info
    if cv.personal_info:
        if not check_entity(cv.personal_info, "PersonalInfo"):
            accepted_personal = None

    # Work experiences & nested bullets
    for exp in cv.experiences:
        exp_valid = check_entity(exp, "Experience")
        valid_bullets = []
        for bullet in exp.bullets:
            if check_entity(bullet, "ExperienceBullet"):
                valid_bullets.append(bullet)
        if exp_valid:
            # Keep experience with only validated bullets
            exp_copy = exp.model_copy(update={"bullets": valid_bullets})
            accepted_experiences.append(exp_copy)

    # Education
    for edu in cv.education:
        if check_entity(edu, "Education"):
            accepted_education.append(edu)

    # Certifications
    for cert in cv.certifications:
        if check_entity(cert, "Certification"):
            accepted_certifications.append(cert)

    # Projects
    for proj in cv.projects:
        if check_entity(proj, "Project"):
            accepted_projects.append(proj)

    # Skills
    for skill in cv.skills:
        if check_entity(skill, "Skill"):
            accepted_skills.append(skill)

    # Languages
    for lang in cv.languages:
        if check_entity(lang, "Language"):
            accepted_languages.append(lang)

    # Awards
    for award in cv.awards:
        if check_entity(award, "Award"):
            accepted_awards.append(award)

    # Publications
    for pub in cv.publications:
        if check_entity(pub, "Publication"):
            accepted_publications.append(pub)

    # Volunteering
    for vol in cv.volunteering:
        if check_entity(vol, "Volunteering"):
            accepted_volunteering.append(vol)

    # Unknown sections
    for unk in cv.unknown_sections:
        if check_entity(unk, "UnknownSection"):
            valid_items = [it for it in unk.items if check_entity(it, "UnknownSectionItem")]
            unk_copy = unk.model_copy(update={"items": valid_items})
            accepted_unknown.append(unk_copy)

    is_overall_valid = (len(rejected_claims) == 0)

    if strict and not is_overall_valid:
        first_err = rejected_claims[0]
        raise ProvenanceValidationError(
            f"Provenance validation failed for {len(rejected_claims)} semantic claim(s). "
            f"First failure ({first_err['entity_type']}): {first_err['errors'][0]}",
            details={"rejected_claims": rejected_claims},
        )

    accepted_cv = CanonicalSemanticCV(
        source_document_id=cv.source_document_id,
        personal_info=accepted_personal,
        experiences=accepted_experiences,
        education=accepted_education,
        certifications=accepted_certifications,
        projects=accepted_projects,
        skills=accepted_skills,
        languages=accepted_languages,
        awards=accepted_awards,
        publications=accepted_publications,
        volunteering=accepted_volunteering,
        unknown_sections=accepted_unknown,
        raw_cv_text=cv.raw_cv_text,
        extraction_mode=cv.extraction_mode,
        metadata={
            **cv.metadata,
            "provenance_validated": True,
            "total_entities_checked": total_checked,
            "accepted_entities_count": total_checked - len(rejected_claims),
            "rejected_entities_count": len(rejected_claims),
        },
    )

    return CanonicalCVValidationReport(
        is_valid=is_overall_valid,
        total_entities_checked=total_checked,
        accepted_entities_count=total_checked - len(rejected_claims),
        rejected_entities_count=len(rejected_claims),
        accepted_cv=accepted_cv,
        rejected_claims=rejected_claims,
    )
