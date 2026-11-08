"""Deterministic Normalization, Validation, and Confidence Module (Phase 7)."""

from app.services.normalization.company_normalizer import (
    normalize_company_name,
    normalize_raw_normalized_company,
)
from app.services.normalization.confidence_scorer import (
    DocumentQualityScore,
    compute_cv_quality_score,
)
from app.services.normalization.contact_normalizer import (
    normalize_email_string,
    normalize_personal_info_entity,
    normalize_phone_number,
    normalize_url,
)
from app.services.normalization.date_normalizer import (
    calculate_duration_months,
    is_current_period,
    normalize_raw_normalized_date,
    parse_single_date,
    split_date_range,
)
from app.services.normalization.language_normalizer import (
    normalize_language_entity,
    normalize_language_name,
    normalize_proficiency_cefr,
)
from app.services.normalization.normalization_pipeline import (
    NormalizedSemanticCVResult,
    deduplicate_cv_records,
    normalize_canonical_cv,
)
from app.services.normalization.skill_normalizer import (
    normalize_skill_entity,
    normalize_skill_name,
)
from app.services.normalization.title_normalizer import (
    normalize_degree,
    normalize_institution,
    normalize_job_title,
    normalize_raw_normalized_degree,
    normalize_raw_normalized_institution,
    normalize_raw_normalized_title,
)
from app.services.normalization.validation_rules import (
    ValidationWarning,
    validate_career_consistency,
)

__all__ = [
    "normalize_canonical_cv",
    "NormalizedSemanticCVResult",
    "compute_cv_quality_score",
    "DocumentQualityScore",
    "ValidationWarning",
    "validate_career_consistency",
    "normalize_skill_entity",
    "normalize_skill_name",
    "parse_single_date",
    "normalize_raw_normalized_date",
    "calculate_duration_months",
    "is_current_period",
    "split_date_range",
    "normalize_job_title",
    "normalize_degree",
    "normalize_institution",
    "normalize_raw_normalized_title",
    "normalize_raw_normalized_degree",
    "normalize_raw_normalized_institution",
    "normalize_company_name",
    "normalize_raw_normalized_company",
    "normalize_language_entity",
    "normalize_language_name",
    "normalize_proficiency_cefr",
    "normalize_personal_info_entity",
    "normalize_email_string",
    "normalize_phone_number",
    "normalize_url",
    "deduplicate_cv_records",
]
