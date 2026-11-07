"""Backend domain and business logic services."""

from app.services.document_parser import parse_document
from app.services.spatial_parser import extract_spatial_document
from app.services.layout import reconstruct_reading_order
from app.services.provenance_validator import (
    CanonicalCVValidationReport,
    EntityValidationResult,
    ProvenanceErrorCode,
    ProvenanceValidationError,
    validate_canonical_cv,
    validate_entity_provenance,
)
from app.services.normalization import (
    DocumentQualityScore,
    NormalizedSemanticCVResult,
    ValidationWarning,
    normalize_canonical_cv,
)
from app.services.document_router import (
    DocumentRoutingResult,
    DocumentType,
    inspect_pdf_text_density,
    route_and_parse_document,
    sniff_document_type,
)
from app.services.ocr_service import (
    MockOCREngine,
    OCRExtractionError,
    extract_spatial_document_with_ocr,
    is_ocr_available,
)
from app.services.cv_benchmark_runner import (
    BenchmarkCorpusItem,
    BenchmarkExecutionMetrics,
    BenchmarkSuiteSummary,
    CVBenchmarkRunner,
    get_standard_benchmark_corpus,
)
from app.services.semantic_extraction_client import (
    ExtractionConfig,
    SemanticExtractionClient,
    SemanticExtractionError,
    SemanticExtractionResult,
    build_source_blocks_prompt_context,
    heuristic_fallback_extract,
    parse_canonical_semantic_cv_json,
)
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
    "extract_spatial_document",
    "reconstruct_reading_order",
    "validate_canonical_cv",
    "validate_entity_provenance",
    "ProvenanceValidationError",
    "ProvenanceErrorCode",
    "CanonicalCVValidationReport",
    "EntityValidationResult",
    "normalize_canonical_cv",
    "NormalizedSemanticCVResult",
    "DocumentQualityScore",
    "ValidationWarning",
    "DocumentType",
    "DocumentRoutingResult",
    "sniff_document_type",
    "inspect_pdf_text_density",
    "route_and_parse_document",
    "OCRExtractionError",
    "is_ocr_available",
    "extract_spatial_document_with_ocr",
    "MockOCREngine",
    "CVBenchmarkRunner",
    "get_standard_benchmark_corpus",
    "BenchmarkCorpusItem",
    "BenchmarkExecutionMetrics",
    "BenchmarkSuiteSummary",
    "SemanticExtractionClient",
    "ExtractionConfig",
    "SemanticExtractionResult",
    "SemanticExtractionError",
    "heuristic_fallback_extract",
    "parse_canonical_semantic_cv_json",
    "build_source_blocks_prompt_context",
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
