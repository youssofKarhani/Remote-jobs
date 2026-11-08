"""Normalization and Validation Pipeline Orchestrator (Prompt 9).

Applies deterministic normalizers:
- Dates (multi-lingual, ISO format, durations)
- Phone numbers (international format, rejects date ranges mistaken for phones)
- Email (lowercased, whitespace trimmed, RFC pattern validation)
- URLs (enforces https, strips tracking query parameters)
- Languages (standardized English names, CEFR tiers)
- Skills & Technologies (taxonomy canonicalization, typo tolerance, alias mapping)
- Companies (legal entity suffix stripping, enterprise canonicalization)
- Education (degree canonicalization, institution alias expansion)
- Duplicate Records (deduplicates skills, certifications, projects, merging block provenance)

Adheres strictly to Rule 3 & 4:
- Verbatim raw values are preserved untouched.
- Normalized values are stored separately with confidence and method metadata.
- Relationships between technologies exist in metadata only and never infer unmentioned claims.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from app.schemas.semantic_cv import CanonicalSemanticCV
from app.services.normalization.company_normalizer import (
    normalize_company_name,
    normalize_raw_normalized_company,
)
from app.services.normalization.confidence_scorer import (
    DocumentQualityScore,
    compute_cv_quality_score,
)
from app.services.normalization.contact_normalizer import normalize_personal_info_entity
from app.services.normalization.date_normalizer import (
    calculate_duration_months,
    is_current_period,
    normalize_raw_normalized_date,
    split_date_range,
)
from app.services.normalization.language_normalizer import normalize_language_entity
from app.services.normalization.skill_normalizer import normalize_skill_entity
from app.services.normalization.title_normalizer import (
    normalize_raw_normalized_degree,
    normalize_raw_normalized_institution,
    normalize_raw_normalized_title,
)
from app.services.normalization.validation_rules import (
    ValidationWarning,
    validate_career_consistency,
)


@dataclass
class NormalizedSemanticCVResult:
    """Complete output of Phase 7 normalization and quality scoring."""
    cv: CanonicalSemanticCV
    quality_score: DocumentQualityScore
    warnings: List[ValidationWarning] = field(default_factory=list)


def deduplicate_cv_records(cv: CanonicalSemanticCV) -> None:
    """Deterministic deduplication of skills, certifications, and projects.

    Consolidates identical or synonymous claims by merging their source_block_ids,
    preserving full evidence provenance without redundant items.
    """
    # 1. Deduplicate Skills
    seen_skills = {}
    unique_skills = []
    for s in cv.skills:
        key = (s.normalized_value or s.raw_value).lower().strip()
        if key in seen_skills:
            existing = seen_skills[key]
            if hasattr(existing.provenance, "source_block_ids") and hasattr(s.provenance, "source_block_ids"):
                merged_bids = list(dict.fromkeys(existing.provenance.source_block_ids + s.provenance.source_block_ids))
                existing.provenance.source_block_ids = merged_bids
        else:
            seen_skills[key] = s
            unique_skills.append(s)
    cv.skills = unique_skills

    # 2. Deduplicate Certifications
    seen_certs = {}
    unique_certs = []
    for cert in cv.certifications:
        key = (
            cert.name.raw_value.lower().strip() if cert.name else "",
            cert.issuing_organization.raw_value.lower().strip() if cert.issuing_organization else "",
        )
        if key in seen_certs:
            existing = seen_certs[key]
            if hasattr(existing.provenance, "source_block_ids") and hasattr(cert.provenance, "source_block_ids"):
                merged_bids = list(dict.fromkeys(existing.provenance.source_block_ids + cert.provenance.source_block_ids))
                existing.provenance.source_block_ids = merged_bids
        else:
            seen_certs[key] = cert
            unique_certs.append(cert)
    cv.certifications = unique_certs

    # 3. Deduplicate Projects
    seen_projs = {}
    unique_projs = []
    for proj in cv.projects:
        key = proj.title.raw_value.lower().strip() if proj.title else ""
        if key in seen_projs:
            existing = seen_projs[key]
            if hasattr(existing.provenance, "source_block_ids") and hasattr(proj.provenance, "source_block_ids"):
                merged_bids = list(dict.fromkeys(existing.provenance.source_block_ids + proj.provenance.source_block_ids))
                existing.provenance.source_block_ids = merged_bids
        else:
            seen_projs[key] = proj
            unique_projs.append(proj)
    cv.projects = unique_projs


def normalize_canonical_cv(
    cv: CanonicalSemanticCV,
    deduplicate: bool = True,
) -> NormalizedSemanticCVResult:
    """Normalize all entities in a CanonicalSemanticCV in-place and score quality."""
    # 1. Personal Info
    if cv.personal_info:
        normalize_personal_info_entity(cv.personal_info)

    # 2. Work Experiences
    for exp in cv.experiences:
        if exp.role_title:
            normalize_raw_normalized_title(exp.role_title)
        if exp.company_name:
            normalize_raw_normalized_company(exp.company_name)

        # Start Date
        if exp.start_date:
            normalize_raw_normalized_date(exp.start_date)

        # End Date
        if exp.end_date:
            normalize_raw_normalized_date(exp.end_date)
            if is_current_period(exp.end_date.raw_value):
                exp.is_current = True
        elif is_current_period(exp.start_date.raw_value if exp.start_date else None):
            exp.is_current = True

        # Calculate duration
        start_iso = exp.start_date.normalized_value if exp.start_date else None
        end_iso = exp.end_date.normalized_value if exp.end_date else None
        duration = calculate_duration_months(start_iso, end_iso, is_current=exp.is_current)
        if duration is not None:
            if not exp.metadata:
                exp.metadata = {}
            exp.metadata["duration_months"] = duration

    # 3. Education
    for edu in cv.education:
        if edu.degree:
            normalize_raw_normalized_degree(edu.degree)
        if edu.institution:
            normalize_raw_normalized_institution(edu.institution)
        if edu.start_date:
            normalize_raw_normalized_date(edu.start_date)
        if edu.end_date:
            normalize_raw_normalized_date(edu.end_date)

    # 4. Skills
    for skill in cv.skills:
        normalize_skill_entity(skill)

    # 5. Languages
    for lang in cv.languages:
        normalize_language_entity(lang)

    # 6. Run consistency validation (before deduplication so duplicate warnings are captured)
    warnings = validate_career_consistency(cv)

    # 7. Deduplicate records if requested
    if deduplicate:
        deduplicate_cv_records(cv)

    # 8. Compute quality and multi-signal confidence scores
    quality_score = compute_cv_quality_score(cv, warnings=warnings)

    # Attach confidence metadata breakdown to CV root
    if not cv.metadata:
        cv.metadata = {}
    cv.metadata["confidence_breakdown"] = quality_score.to_metadata_dict()

    return NormalizedSemanticCVResult(
        cv=cv,
        quality_score=quality_score,
        warnings=warnings,
    )
