"""Confidence and Quality Scoring Engine for Semantic CV Ingestion (Prompt 9).

Computes multi-signal confidence metrics:
1. Extraction Quality: Provenance grounding and raw text completeness.
2. Layout Confidence: Block reference stability and valid page coverage.
3. Semantic Confidence: Model extraction and parser confidence across sections.
4. Source Consistency: Absence of temporal inversions and contradictory dates.
5. Deterministic Validation Outcome: Penalty weighting based on validation warnings.

IMPORTANT ARCHITECTURAL RULE:
Do NOT present confidence as verification. Extracted evidence is never marked
is_verified = True automatically.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

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

    # Multi-signal confidence breakdown (Prompt 9)
    extraction_quality: float = 1.0
    layout_confidence: float = 1.0
    semantic_confidence: float = 1.0
    source_consistency: float = 1.0
    validation_outcome_score: float = 1.0

    # Invariant: Never present confidence as verification
    is_verified: bool = False

    def to_metadata_dict(self) -> Dict[str, Any]:
        """Serialize confidence breakdown for CV metadata storage."""
        return {
            "overall_score": self.overall_score,
            "extraction_quality": self.extraction_quality,
            "layout_confidence": self.layout_confidence,
            "semantic_confidence": self.semantic_confidence,
            "source_consistency": self.source_consistency,
            "validation_outcome_score": self.validation_outcome_score,
            "normalization_rate": self.normalization_rate,
            "warnings_count": self.warnings_count,
            "is_verified": False,
        }


def compute_cv_quality_score(
    cv: CanonicalSemanticCV,
    warnings: Optional[List[ValidationWarning]] = None,
) -> DocumentQualityScore:
    """Compute granular multi-signal quality and confidence scores across a CanonicalSemanticCV."""
    warnings = warnings or []
    section_scores: Dict[str, float] = {}

    total_entities = 0
    normalized_entities = 0

    all_extraction_confs: List[float] = []
    all_semantic_confs: List[float] = []

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

        if hasattr(cv.personal_info.provenance, "extraction_confidence"):
            all_extraction_confs.append(cv.personal_info.provenance.extraction_confidence)

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
            if hasattr(s.provenance, "extraction_confidence"):
                all_extraction_confs.append(s.provenance.extraction_confidence)
            norm_conf = s.metadata.get("normalization_confidence", 0.9) if s.metadata else 0.9
            all_semantic_confs.append(norm_conf)
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
            all_extraction_confs.append(prov_conf)
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
            all_extraction_confs.append(prov_conf)
        section_scores["education"] = round(sum(edu_confs) / len(edu_confs), 2)
    else:
        section_scores["education"] = 0.0

    # Normalization Rate
    norm_rate = round(min(1.0, normalized_entities / total_entities), 2) if total_entities > 0 else 0.0

    # Signal 1: Extraction Quality
    extraction_quality = round(sum(all_extraction_confs) / len(all_extraction_confs), 2) if all_extraction_confs else 0.90

    # Signal 2: Layout Confidence (anchored source blocks)
    has_layout = bool(cv.source_document_id)
    layout_confidence = 0.95 if has_layout else 0.80

    # Signal 3: Semantic Confidence
    semantic_confidence = round(sum(all_semantic_confs) / len(all_semantic_confs), 2) if all_semantic_confs else 0.90

    # Signal 4: Source Consistency (reduced if temporal or contradictory warnings)
    consistency_warnings = [w for w in warnings if w.code in ("TEMPORAL_INVERSION", "EDUCATION_TEMPORAL_INVERSION", "FUTURE_START_DATE", "CONTRADICTORY_CURRENT_STATUS")]
    source_consistency = max(0.5, round(1.0 - (len(consistency_warnings) * 0.15), 2))

    # Signal 5: Validation Outcome Score
    warning_penalty = min(len(warnings) * 0.02, 0.15)
    validation_outcome_score = max(0.5, round(1.0 - warning_penalty, 2))

    # Composite Overall Score
    base_weights = {
        "experience": 0.35,
        "skills": 0.30,
        "education": 0.20,
        "personal_info": 0.15,
    }
    active_weights = {k: w for k, w in base_weights.items() if section_scores.get(k, 0.0) > 0.0}
    total_active_weight = sum(active_weights.values())

    if total_active_weight > 0:
        composite = sum(section_scores[k] * (w / total_active_weight) for k, w in active_weights.items())
    else:
        composite = 0.5

    # Combine with normalization rate, source consistency, and warning penalty
    composite = (composite * 0.85) + (norm_rate * 0.10) + (source_consistency * 0.05)
    final_score = max(0.0, round(composite - warning_penalty, 2))

    return DocumentQualityScore(
        overall_score=final_score,
        section_scores=section_scores,
        total_entities=total_entities,
        normalized_entities=normalized_entities,
        normalization_rate=norm_rate,
        warnings_count=len(warnings),
        warnings=warnings,
        extraction_quality=extraction_quality,
        layout_confidence=layout_confidence,
        semantic_confidence=semantic_confidence,
        source_consistency=source_consistency,
        validation_outcome_score=validation_outcome_score,
        is_verified=False,
    )
