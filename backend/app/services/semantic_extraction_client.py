"""Semantic Extraction Client (Re-export Shim).

Maintained for full backward compatibility across the monorepo.
Primary implementation lives in app.services.cv_semantic_extractor.
"""

from app.services.cv_semantic_extractor import (
    CVSemanticExtractor,
    ExtractionConfig,
    ProvenanceIntegrityError,
    SchemaValidationError,
    SemanticExtractionClient,
    SemanticExtractionError,
    SemanticExtractionResult,
    SYSTEM_EXTRACTION_PROMPT,
    build_blocks_json_payload,
    build_source_blocks_prompt_context,
    derive_section_hint,
    extract_json_payload,
    heuristic_fallback_extract,
    parse_canonical_semantic_cv_json,
    strip_thinking_tokens,
)

__all__ = [
    "CVSemanticExtractor",
    "ExtractionConfig",
    "ProvenanceIntegrityError",
    "SchemaValidationError",
    "SemanticExtractionClient",
    "SemanticExtractionError",
    "SemanticExtractionResult",
    "SYSTEM_EXTRACTION_PROMPT",
    "build_blocks_json_payload",
    "build_source_blocks_prompt_context",
    "derive_section_hint",
    "extract_json_payload",
    "heuristic_fallback_extract",
    "parse_canonical_semantic_cv_json",
    "strip_thinking_tokens",
]
