"""Backend domain and business logic services."""

from app.services.document_parser import parse_document
from app.services.cv_extraction_service import cv_extraction_service, CVExtractionService
from app.services.evidence_validation import (
    EvidenceValidationError,
    validate_selected_evidence_ids,
    get_user_allowed_evidence_ids,
    resolve_verified_evidence_text,
)
from app.services.job_deduplication import (
    compute_content_hash,
    sanitize_job_title,
    job_deduplication_service,
    JobDeduplicationService,
)
from app.services.job_filtering import (
    JOB_TYPE_MAPPING,
    deterministic_filter_service,
    DeterministicFilterService,
)

__all__ = [
    "parse_document",
    "cv_extraction_service",
    "CVExtractionService",
    "EvidenceValidationError",
    "validate_selected_evidence_ids",
    "get_user_allowed_evidence_ids",
    "resolve_verified_evidence_text",
    "compute_content_hash",
    "sanitize_job_title",
    "job_deduplication_service",
    "JobDeduplicationService",
    "JOB_TYPE_MAPPING",
    "deterministic_filter_service",
    "DeterministicFilterService",
]
