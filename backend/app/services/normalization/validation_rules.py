"""Validation and Consistency Engine for Normalized CVs (Prompt 9).

Detects anomalies, data integrity violations, and temporal inconsistencies:
1. Start date after end date (temporal inversion)
2. Malformed email addresses
3. Malformed URLs
4. Date ranges mistaken for phone numbers
5. Duplicate certifications
6. Duplicate projects
7. Duplicate skills
8. Impossible source references (invalid block ID format or invalid page numbers)
9. Missing provenance (empty source_block_ids)
10. Unsupported model-returned facts (empty raw_text and raw_value)
"""

from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Set

from app.schemas.semantic_cv import (
    CanonicalSemanticCV,
    ProvenanceMetadata,
    SemanticEducation,
    SemanticExperience,
)

# Date range regex detecting temporal ranges in non-date fields
DATE_RANGE_REGEX = re.compile(
    r"^\s*(?:19\d\d|20\d\d)\s*[-–—/]\s*(?:19\d\d|20\d\d|present|heute|current|now)\s*$",
    re.IGNORECASE,
)

EMAIL_STRICT_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

BLOCK_ID_REGEX = re.compile(r"^BLOCK_\d+$")


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


def _check_entity_provenance_and_factuality(
    entity: Any,
    entity_type: str,
    summary: str,
    valid_block_ids: Optional[Set[str]] = None,
) -> List[ValidationWarning]:
    """Check entity for missing provenance, impossible source references, and unsupported facts."""
    warnings = []
    prov: Optional[ProvenanceMetadata] = getattr(entity, "provenance", None)

    if not prov:
        warnings.append(ValidationWarning(
            code="MISSING_PROVENANCE",
            message=f"{entity_type} '{summary}' is missing required ProvenanceMetadata container.",
            severity="critical",
            entity_type=entity_type,
            entity_summary=summary,
        ))
        return warnings

    # 1. Missing provenance: empty source_block_ids
    if not prov.source_block_ids or not any(bid.strip() for bid in prov.source_block_ids):
        warnings.append(ValidationWarning(
            code="MISSING_PROVENANCE",
            message=f"{entity_type} '{summary}' has empty source_block_ids; no layout block anchor.",
            severity="critical",
            entity_type=entity_type,
            entity_summary=summary,
        ))
    else:
        # 2. Impossible source references: malformed block ID or non-existent in layout
        for bid in prov.source_block_ids:
            if not BLOCK_ID_REGEX.match(bid.strip()):
                warnings.append(ValidationWarning(
                    code="IMPOSSIBLE_SOURCE_REFERENCE",
                    message=f"{entity_type} '{summary}' contains malformed source_block_id '{bid}'.",
                    severity="critical",
                    entity_type=entity_type,
                    entity_summary=summary,
                ))
            elif valid_block_ids is not None and bid.strip() not in valid_block_ids:
                warnings.append(ValidationWarning(
                    code="IMPOSSIBLE_SOURCE_REFERENCE",
                    message=f"{entity_type} '{summary}' references non-existent block ID '{bid}'.",
                    severity="critical",
                    entity_type=entity_type,
                    entity_summary=summary,
                ))

    # Check page numbers
    if not prov.source_pages or any(p <= 0 for p in prov.source_pages):
        warnings.append(ValidationWarning(
            code="IMPOSSIBLE_SOURCE_REFERENCE",
            message=f"{entity_type} '{summary}' has invalid page references: {prov.source_pages}.",
            severity="warning",
            entity_type=entity_type,
            entity_summary=summary,
        ))

    # 3. Unsupported model-returned facts: empty raw_text and empty raw_value
    has_raw_text = bool(prov.raw_text and prov.raw_text.strip())
    has_raw_val = bool(prov.raw_value and prov.raw_value.strip())
    entity_raw = getattr(entity, "raw_value", None) or getattr(entity, "raw_text", None)
    if not has_raw_text and not has_raw_val and not entity_raw:
        warnings.append(ValidationWarning(
            code="UNSUPPORTED_FACT",
            message=f"{entity_type} '{summary}' has empty verbatim raw text / raw value to support claim.",
            severity="critical",
            entity_type=entity_type,
            entity_summary=summary,
        ))

    return warnings


def validate_career_consistency(
    cv: CanonicalSemanticCV,
    valid_block_ids: Optional[Set[str]] = None,
) -> List[ValidationWarning]:
    """Run non-destructive validation checks across all sections of a CanonicalSemanticCV."""
    warnings: List[ValidationWarning] = []
    current_year = datetime.now().year

    # 1. Personal Info Validations
    if cv.personal_info:
        p_summary = cv.personal_info.full_name.raw_value if cv.personal_info.full_name else "Personal Info"
        warnings.extend(_check_entity_provenance_and_factuality(
            cv.personal_info, "PersonalInfo", p_summary, valid_block_ids=valid_block_ids
        ))

        # Check for date ranges mistaken for phone numbers
        if cv.personal_info.phone and cv.personal_info.phone.raw_value:
            raw_phone = cv.personal_info.phone.raw_value.strip()
            if DATE_RANGE_REGEX.match(raw_phone):
                warnings.append(ValidationWarning(
                    code="DATE_RANGE_AS_PHONE",
                    message=f"Phone number '{raw_phone}' appears to be a date range mistaken for a phone number.",
                    severity="warning",
                    entity_type="PersonalInfo",
                    entity_summary="Phone",
                ))

        # Check for malformed email
        if cv.personal_info.email and cv.personal_info.email.raw_value:
            raw_email = cv.personal_info.email.raw_value.strip()
            if not EMAIL_STRICT_REGEX.match(raw_email):
                warnings.append(ValidationWarning(
                    code="MALFORMED_EMAIL",
                    message=f"Email '{raw_email}' does not conform to valid email syntax.",
                    severity="warning",
                    entity_type="PersonalInfo",
                    entity_summary="Email",
                ))

        # Check for malformed URLs
        for field_name, url_obj in [
            ("LinkedIn", cv.personal_info.linkedin_url),
            ("GitHub", cv.personal_info.github_url),
            ("Portfolio", cv.personal_info.portfolio_url),
        ]:
            if url_obj and url_obj.raw_value:
                raw_u = url_obj.raw_value.strip()
                if " " in raw_u or "\n" in raw_u or "." not in raw_u:
                    warnings.append(ValidationWarning(
                        code="MALFORMED_URL",
                        message=f"{field_name} URL '{raw_u}' is malformed or invalid.",
                        severity="warning",
                        entity_type="PersonalInfo",
                        entity_summary=field_name,
                    ))

    # 2. Experience Validations
    seen_experiences = set()
    for idx, exp in enumerate(cv.experiences):
        summary = f"{exp.role_title.raw_value} at {exp.company_name.raw_value}"
        warnings.extend(_check_entity_provenance_and_factuality(
            exp, "Experience", summary, valid_block_ids=valid_block_ids
        ))

        start_iso = exp.start_date.normalized_value if exp.start_date else None
        end_iso = exp.end_date.normalized_value if exp.end_date else None

        # Check for duplicate experiences
        exp_key = (
            exp.role_title.raw_value.lower().strip() if exp.role_title else "",
            exp.company_name.raw_value.lower().strip() if exp.company_name else "",
            start_iso or "",
        )
        if exp_key in seen_experiences:
            warnings.append(ValidationWarning(
                code="DUPLICATE_EXPERIENCE",
                message=f"Duplicate work experience detected: '{summary}'.",
                severity="info",
                entity_type="Experience",
                entity_summary=summary,
            ))
        else:
            seen_experiences.add(exp_key)

        # Temporal inversion: start date after end date
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

        # Check bullets provenance
        for bullet in exp.bullets:
            warnings.extend(_check_entity_provenance_and_factuality(
                bullet, "ExperienceBullet", bullet.raw_text[:40], valid_block_ids=valid_block_ids
            ))

    # 3. Education Validations
    seen_education = set()
    for edu in cv.education:
        summary = f"{edu.degree.raw_value} from {edu.institution.raw_value}"
        warnings.extend(_check_entity_provenance_and_factuality(
            edu, "Education", summary, valid_block_ids=valid_block_ids
        ))

        start_iso = edu.start_date.normalized_value if edu.start_date else None
        end_iso = edu.end_date.normalized_value if edu.end_date else None

        edu_key = (
            edu.degree.raw_value.lower().strip() if edu.degree else "",
            edu.institution.raw_value.lower().strip() if edu.institution else "",
        )
        if edu_key in seen_education:
            warnings.append(ValidationWarning(
                code="DUPLICATE_EDUCATION",
                message=f"Duplicate education detected: '{summary}'.",
                severity="info",
                entity_type="Education",
                entity_summary=summary,
            ))
        else:
            seen_education.add(edu_key)

        # Temporal inversion
        if start_iso and end_iso and end_iso != "Present":
            if _compare_iso_dates(start_iso, end_iso) > 0:
                warnings.append(ValidationWarning(
                    code="EDUCATION_TEMPORAL_INVERSION",
                    message=f"Education completion '{edu.end_date.raw_value}' precedes start '{edu.start_date.raw_value}'.",
                    severity="warning",
                    entity_type="Education",
                    entity_summary=summary,
                ))

    # 4. Duplicate Skills Validation
    seen_skills = set()
    for s in cv.skills:
        warnings.extend(_check_entity_provenance_and_factuality(
            s, "Skill", s.raw_value, valid_block_ids=valid_block_ids
        ))
        effective_key = (s.normalized_value or s.raw_value).lower().strip()
        if effective_key in seen_skills:
            warnings.append(ValidationWarning(
                code="DUPLICATE_SKILLS",
                message=f"Duplicate skill entry detected: '{s.raw_value}'.",
                severity="info",
                entity_type="Skill",
                entity_summary=s.raw_value,
            ))
        else:
            seen_skills.add(effective_key)

    # 5. Duplicate Certifications Validation
    seen_certs = set()
    for cert in cv.certifications:
        summary = cert.name.raw_value if cert.name else "Certification"
        warnings.extend(_check_entity_provenance_and_factuality(
            cert, "Certification", summary, valid_block_ids=valid_block_ids
        ))
        cert_key = (
            cert.name.raw_value.lower().strip() if cert.name else "",
            cert.issuing_organization.raw_value.lower().strip() if cert.issuing_organization else "",
        )
        if cert_key in seen_certs:
            warnings.append(ValidationWarning(
                code="DUPLICATE_CERTIFICATIONS",
                message=f"Duplicate certification detected: '{summary}'.",
                severity="info",
                entity_type="Certification",
                entity_summary=summary,
            ))
        else:
            seen_certs.add(cert_key)

    # 6. Duplicate Projects Validation
    seen_projects = set()
    for proj in cv.projects:
        summary = proj.title.raw_value if proj.title else "Project"
        warnings.extend(_check_entity_provenance_and_factuality(
            proj, "Project", summary, valid_block_ids=valid_block_ids
        ))
        proj_key = proj.title.raw_value.lower().strip() if proj.title else ""
        if proj_key in seen_projects:
            warnings.append(ValidationWarning(
                code="DUPLICATE_PROJECTS",
                message=f"Duplicate project detected: '{summary}'.",
                severity="info",
                entity_type="Project",
                entity_summary=summary,
            ))
        else:
            seen_projects.add(proj_key)

    return warnings
