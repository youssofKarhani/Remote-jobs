"""Validation and Consistency Engine for Normalized CVs.

Detects temporal inversions (e.g. end_date < start_date), future dates,
incoherent current status, and malformed contact fields without discarding user data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.schemas.semantic_cv import CanonicalSemanticCV, SemanticEducation, SemanticExperience


@dataclass
class ValidationWarning:
    """Non-blocking validation warning highlighting data anomalies."""
    code: str
    message: str
    severity: str = "warning"  # "info", "warning", "critical"
    entity_type: str = ""
    entity_summary: str = ""


def _compare_iso_dates(date_a: str, date_b: str) -> int:
    """Compare two ISO date strings (e.g. '2020-01' vs '2022-04').
    
    Returns:
        -1 if a < b, 0 if a == b, 1 if a > b
    """
    if date_a < date_b:
        return -1
    elif date_a > date_b:
        return 1
    return 0


def validate_career_consistency(cv: CanonicalSemanticCV) -> List[ValidationWarning]:
    """Run non-destructive validation checks across all sections of a CanonicalSemanticCV."""
    warnings: List[ValidationWarning] = []
    current_year = datetime.now().year

    # 1. Experience Validations
    for idx, exp in enumerate(cv.experiences):
        summary = f"{exp.role_title.raw_value} at {exp.company_name.raw_value}"
        start_iso = exp.start_date.normalized_value if exp.start_date else None
        end_iso = exp.end_date.normalized_value if exp.end_date else None

        # Temporal inversion
        if start_iso and end_iso and end_iso != "Present":
            if _compare_iso_dates(start_iso, end_iso) > 0:
                warnings.append(ValidationWarning(
                    code="TEMPORAL_INVERSION",
                    message=f"End date '{exp.end_date.raw_value}' precedes start date '{exp.start_date.raw_value}'.",
                    severity="warning",
                    entity_type="Experience",
                    entity_summary=summary,
                ))

        # Future start date
        if start_iso:
            try:
                start_yr = int(start_iso.split("-")[0])
                if start_yr > current_year + 1:
                    warnings.append(ValidationWarning(
                        code="FUTURE_START_DATE",
                        message=f"Start year {start_yr} is in the future.",
                        severity="warning",
                        entity_type="Experience",
                        entity_summary=summary,
                    ))
            except ValueError:
                pass

        # Contradictory current status
        if exp.is_current and end_iso and end_iso != "Present":
            try:
                end_yr = int(end_iso.split("-")[0])
                if end_yr < current_year:
                    warnings.append(ValidationWarning(
                        code="CONTRADICTORY_CURRENT_STATUS",
                        message="Role is marked as current, but has an end date in the past.",
                        severity="info",
                        entity_type="Experience",
                        entity_summary=summary,
                    ))
            except ValueError:
                pass

        # Missing bullets
        if not exp.bullets:
            warnings.append(ValidationWarning(
                code="EMPTY_EXPERIENCE_BULLETS",
                message="Work experience record contains no discrete achievement bullets.",
                severity="info",
                entity_type="Experience",
                entity_summary=summary,
            ))

    # 2. Education Validations
    for edu in cv.education:
        summary = f"{edu.degree.raw_value} from {edu.institution.raw_value}"
        start_iso = edu.start_date.normalized_value if edu.start_date else None
        end_iso = edu.end_date.normalized_value if edu.end_date else None

        if start_iso and end_iso and end_iso != "Present":
            if _compare_iso_dates(start_iso, end_iso) > 0:
                warnings.append(ValidationWarning(
                    code="EDUCATION_TEMPORAL_INVERSION",
                    message=f"Education completion '{edu.end_date.raw_value}' precedes start '{edu.start_date.raw_value}'.",
                    severity="warning",
                    entity_type="Education",
                    entity_summary=summary,
                ))

    # 3. Personal Info Validations
    if cv.personal_info:
        if cv.personal_info.email and cv.personal_info.email.confidence < 0.8:
            warnings.append(ValidationWarning(
                code="SUSPICIOUS_EMAIL",
                message=f"Email '{cv.personal_info.email.raw_value}' does not match standard email pattern.",
                severity="warning",
                entity_type="PersonalInfo",
                entity_summary="Email",
            ))

    return warnings
