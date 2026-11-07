"""Confidence and Quality Scoring Engine for Semantic CV Ingestion.

Computes multi-dimensional quality scores across extraction provenance,
normalization completeness, and temporal coherence.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.schemas.semantic_cv import CanonicalSemanticCV
from app.services.normalization.validation_rules import ValidationWarning


@dataclass
class DocumentQualityScore:
    """Document-level composite ingestion confidence assessment."""
    overall_score: float
    section_scores: Dict[str, float] = field(default_factory=dict)
    total_entities: int = 0
    normalized_entities: int = 0
    normalization_rate: float = 0.0
    warnings_count: int = 0
    warnings: List[ValidationWarning] = field(default_factory=list)


def compute_cv_quality_score(
    cv: CanonicalSemanticCV,
    warnings: Optional[List[ValidationWarning]] = None
) -> DocumentQualityScore:
    """Compute granular quality scores across all sections of a CanonicalSemanticCV."""
    warnings = warnings or []
    section_scores: Dict[str, float] = {}

    total_entities = 0
    normalized_entities = 0

    # 1. Personal Info Score
    if cv.personal_info:
        p_scores = []
        if cv.personal_info.full_name:
            p_scores.append(cv.personal_info.full_name.confidence)
            total_entities += 1
            if cv.personal_info.full_name.is_normalized():
                normalized_entities += 1

        if cv.personal_info.email:
            p_scores.append(cv.personal_info.email.confidence)
            total_entities += 1
            if cv.personal_info.email.is_normalized():
                normalized_entities += 1

        if cv.personal_info.phone:
            p_scores.append(cv.personal_info.phone.confidence)
            total_entities += 1
            if cv.personal_info.phone.is_normalized():
                normalized_entities += 1

        section_scores["personal_info"] = round(sum(p_scores) / len(p_scores), 2) if p_scores else 0.8
    else:
        section_scores["personal_info"] = 0.0

    # 2. Skills Score
    if cv.skills:
        s_confs = []
        for s in cv.skills:
            total_entities += 1
            if s.normalized_value:
                normalized_entities += 1
                s_confs.append(s.provenance.extraction_confidence if hasattr(s.provenance, "extraction_confidence") else 0.95)
            else:
                s_confs.append(0.6)
        section_scores["skills"] = round(sum(s_confs) / len(s_confs), 2)
    else:
        section_scores["skills"] = 0.0

    # 3. Experience Score
    if cv.experiences:
        exp_confs = []
        for exp in cv.experiences:
            if exp.role_title:
                total_entities += 1
                if exp.role_title.is_normalized():
                    normalized_entities += 1
            if exp.start_date:
                total_entities += 1
                if exp.start_date.is_normalized():
                    normalized_entities += 1

            prov_conf = exp.provenance.extraction_confidence if hasattr(exp.provenance, "extraction_confidence") else 0.8
            exp_confs.append(prov_conf)
        section_scores["experience"] = round(sum(exp_confs) / len(exp_confs), 2)
    else:
        section_scores["experience"] = 0.0

    # 4. Education Score
    if cv.education:
        edu_confs = []
        for edu in cv.education:
            if edu.degree:
                total_entities += 1
                if edu.degree.is_normalized():
                    normalized_entities += 1
            prov_conf = edu.provenance.extraction_confidence if hasattr(edu.provenance, "extraction_confidence") else 0.8
            edu_confs.append(prov_conf)
        section_scores["education"] = round(sum(edu_confs) / len(edu_confs), 2)
    else:
        section_scores["education"] = 0.0

    # Normalization Rate (clamped 0.0 to 1.0)
    norm_rate = round(min(1.0, normalized_entities / total_entities), 2) if total_entities > 0 else 0.0

    # Base weights
    base_weights = {
        "experience": 0.35,
        "skills": 0.30,
        "education": 0.20,
        "personal_info": 0.15,
    }

    # Normalize weights across actively present sections
    active_weights = {k: w for k, w in base_weights.items() if section_scores.get(k, 0.0) > 0.0}
    total_active_weight = sum(active_weights.values())

    if total_active_weight > 0:
        composite = sum(section_scores[k] * (w / total_active_weight) for k, w in active_weights.items())
    else:
        composite = 0.5

    # Composite incorporates normalization completion
    composite = (composite * 0.90) + (norm_rate * 0.10)

    # Minor penalty for warnings (0.02 per warning, max 0.10 penalty)
    warning_penalty = min(len(warnings) * 0.02, 0.10)
    final_score = max(0.0, round(composite - warning_penalty, 2))

    return DocumentQualityScore(
        overall_score=final_score,
        section_scores=section_scores,
        total_entities=total_entities,
        normalized_entities=normalized_entities,
        normalization_rate=norm_rate,
        warnings_count=len(warnings),
        warnings=warnings,
    )
