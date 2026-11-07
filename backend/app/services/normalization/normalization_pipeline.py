"""Normalization and Validation Pipeline Orchestrator.

Applies deterministic normalizers (skills, dates, titles, degrees, languages, contacts),
runs consistency validations, and calculates document quality scores.
Preserves all raw values and adheres strictly to Rule 3 & 4.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from app.schemas.semantic_cv import CanonicalSemanticCV
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


def normalize_canonical_cv(cv: CanonicalSemanticCV) -> NormalizedSemanticCVResult:
    """Normalize all entities in a CanonicalSemanticCV in-place and score quality."""
    # 1. Personal Info
    if cv.personal_info:
        normalize_personal_info_entity(cv.personal_info)

    # 2. Work Experiences
    for exp in cv.experiences:
        if exp.role_title:
            normalize_raw_normalized_title(exp.role_title)

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

    # 6. Run consistency validation
    warnings = validate_career_consistency(cv)

    # 7. Compute quality and confidence scores
    quality_score = compute_cv_quality_score(cv, warnings=warnings)

    return NormalizedSemanticCVResult(
        cv=cv,
        quality_score=quality_score,
        warnings=warnings,
    )
