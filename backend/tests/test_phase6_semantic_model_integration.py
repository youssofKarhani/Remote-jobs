"""Test Suite for Phase 6 — Semantic Model Integration (Prompt 8).

Verifies:
1. Valid structured response (valid JSON schema, valid source block IDs, deterministic options).
2. Malformed JSON handling (triggers parsing error, falls back with explicit degraded record).
3. Invalid block IDs rejection (hallucinated block IDs not in request blocks are rejected).
4. Unsupported facts rejection (missing block IDs or missing raw text rejected).
5. Connection timeout handling (bounded retry backoff, graceful fallback with degraded=True).
6. Temporary 502 recovery (recovers after transient gateway cold start error).
7. Exhausted retries handling (all retries fail, explicit fallback with semantic_model_error).
8. Feature flag disabled (bypasses LLM, executes deterministic heuristic fallback).
9. Schema enforcement and options (temperature = 0, format schema validation).
10. Naming consistency across cv_semantic_extractor, cv_extraction_llm, and semantic_extraction_client.
"""

import json
from typing import Any, Dict, List
import httpx
import pytest

from app.config import settings
from app.schemas.layout import BoundingBox, ColumnLayout, LayoutDocument, SourceBlock
from app.schemas.semantic_cv import (
    CanonicalSemanticCV,
    ProvenanceMetadata,
    RawNormalizedValue,
    SemanticEducation,
    SemanticExperience,
    SemanticPersonalInfo,
    SemanticSkill,
    UnknownSection,
)
from app.services.provenance_validator import (
    ProvenanceErrorCode,
    validate_canonical_cv,
    validate_entity_provenance,
)
from app.services.cv_semantic_extractor import (
    CVSemanticExtractor,
    ExtractionConfig,
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
import app.services.cv_extraction_llm as cv_llm_module


# ============================================================================
# Test Fixtures & Helpers
# ============================================================================

def _make_bbox(x0=0.0, y0=0.0, x1=100.0, y1=20.0) -> BoundingBox:
    return BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1)


def _make_block(
    block_id: str,
    page: int,
    text: str,
    region_type: str = "main_body",
    reading_order: int = 1,
    is_heading: bool = False,
    heading_level: int = None,
    column: int = 0,
) -> SourceBlock:
    return SourceBlock(
        id=block_id,
        page=page,
        column=column,
        region_type=region_type,
        bbox=_make_bbox(),
        text=text,
        raw_text=text,
        reading_order=reading_order,
        is_heading=is_heading,
        heading_level=heading_level,
    )


@pytest.fixture
def sample_two_column_layout_doc() -> LayoutDocument:
    """Simulates a reconstructed LayoutDocument for a 2-column CV (similar to Youssof's CV)."""
    blocks = [
        # Header
        _make_block(
            "BLOCK_001", page=1, text="Youssof El Karhani | youssof@example.com | +49 170 1234567 | Berlin, Germany",
            region_type="header", reading_order=1
        ),
        # Left Sidebar: Skills & Languages
        _make_block("BLOCK_002", page=1, text="TECHNICAL SKILLS", region_type="left_sidebar", reading_order=2, is_heading=True, heading_level=1),
        _make_block("BLOCK_003", page=1, text="Python, FastAPI, PostgreSQL, Docker, PyTorch, MangoDB", region_type="left_sidebar", reading_order=3),
        _make_block("BLOCK_004", page=1, text="LANGUAGES", region_type="left_sidebar", reading_order=4, is_heading=True, heading_level=1),
        _make_block("BLOCK_005", page=1, text="English (Fluent), German (B2), Arabic (Native)", region_type="left_sidebar", reading_order=5),
        # Right Main Body: Experience & Education & Unknown Section
        _make_block("BLOCK_006", page=1, text="WORK EXPERIENCE", region_type="main_body", reading_order=6, is_heading=True, heading_level=1, column=1),
        _make_block("BLOCK_007", page=1, text="Senior Backend Engineer at TechCorp\nArchitected high-throughput microservices using FastAPI.", region_type="main_body", reading_order=7, column=1),
        _make_block("BLOCK_008", page=1, text="EDUCATION", region_type="main_body", reading_order=8, is_heading=True, heading_level=1, column=1),
        _make_block("BLOCK_009", page=1, text="B.Sc. in Computer Science\nTechnical University of Berlin", region_type="main_body", reading_order=9, column=1),
        _make_block("BLOCK_010", page=1, text="OPEN SOURCE CONTRIBUTIONS", region_type="main_body", reading_order=10, is_heading=True, heading_level=1, column=1),
        _make_block("BLOCK_011", page=1, text="Maintainer of py-fast-parser with 200+ stars on GitHub", region_type="main_body", reading_order=11, column=1),
    ]
    return LayoutDocument(
        filename="youssof_cv_test.pdf",
        total_pages=1,
        source_blocks=blocks,
        reading_order_text="\n\n".join(b.text for b in blocks),
    )


# ============================================================================
# 1. Module & Naming Consistency Tests
# ============================================================================

class TestModuleNamingConsistency:
    def test_dedicated_service_naming_and_exports(self):
        """Ensure CVSemanticExtractor is accessible via cv_semantic_extractor and cv_extraction_llm."""
        assert CVSemanticExtractor is not None
        assert cv_llm_module.CVSemanticExtractor is CVSemanticExtractor
        assert cv_llm_module.SemanticExtractionClient is CVSemanticExtractor

    def test_default_config_matches_application_settings(self):
        config = ExtractionConfig()
        assert config.base_url == getattr(settings, "CV_EXTRACTION_LLM_BASE_URL", "http://cv-extractor-llm.railway.internal:11434")
        assert config.model == getattr(settings, "CV_EXTRACTION_LLM_MODEL", "qwen3:1.7b")
        assert config.enabled == getattr(settings, "CV_EXTRACTION_LLM_ENABLED", False)
        assert config.timeout_seconds == getattr(settings, "CV_EXTRACTION_LLM_TIMEOUT_SECONDS", 90.0)
        assert config.temperature == 0.0


# ============================================================================
# 2. Reconstructed Source Block Input Construction Tests
# ============================================================================

class TestSourceBlockInputConstruction:
    def test_build_blocks_json_payload_format(self, sample_two_column_layout_doc):
        """Verify blocks are serialized conceptually with id, page, section_hint, text."""
        payload = build_blocks_json_payload(sample_two_column_layout_doc)
        assert "blocks" in payload
        assert len(payload["blocks"]) == 11
        first_b = payload["blocks"][0]
        assert first_b["id"] == "BLOCK_001"
        assert first_b["page"] == 1
        assert "section_hint" in first_b
        assert "youssof@example.com" in first_b["text"]

    def test_build_source_blocks_prompt_context(self, sample_two_column_layout_doc):
        context = build_source_blocks_prompt_context(sample_two_column_layout_doc, document_id="DOC_YOUSSOF_001")
        assert "DOCUMENT ID: DOC_YOUSSOF_001" in context
        assert "TOTAL BLOCKS: 11" in context
        assert "BLOCK_001" in context
        assert "BLOCK_007" in context
        assert "=== STRUCTURED SOURCE BLOCKS ===" in context


# ============================================================================
# 3. Model Reasoning (<think>) Stripping & JSON Extraction Tests
# ============================================================================

class TestThinkingTokenSanitization:
    def test_strip_thinking_tokens(self):
        sample = "<think>\nThinking about extracting personal info...\n</think>\n```json\n{\"full_name\": {\"raw_value\": \"Alice\"}}\n```"
        stripped = strip_thinking_tokens(sample)
        assert "<think>" not in stripped
        assert "</think>" not in stripped
        assert "Alice" in stripped

    def test_extract_json_payload_with_fences(self):
        text = "Here is the result:\n```json\n{\"personal_info\": null}\n```\nHope it helps!"
        extracted = extract_json_payload(text)
        assert extracted == '{"personal_info": null}'


# ============================================================================
# 4. Prompt 8 Specific Core Test Suite: 8 Required Test Cases
# ============================================================================

class TestPhase6RequiredTestCases:

    # 1. Valid Structured Response
    @pytest.mark.asyncio
    async def test_1_valid_structured_response(self, sample_two_column_layout_doc):
        """Model returns valid JSON matching CanonicalSemanticCV schema and valid block IDs."""
        mock_payload = {
            "response": json.dumps({
                "source_document_id": "youssof_cv_test.pdf",
                "personal_info": {
                    "full_name": {"raw_value": "Youssof El Karhani", "normalized_value": None},
                    "email": {"raw_value": "youssof@example.com", "normalized_value": None},
                    "provenance": {
                        "source_pages": [1],
                        "source_block_ids": ["BLOCK_001"],
                        "raw_text": "Youssof El Karhani | youssof@example.com",
                        "extraction_method": "semantic_llm",
                    }
                },
                "skills": [
                    {
                        "raw_value": "Python",
                        "normalized_value": None,
                        "provenance": {
                            "source_pages": [1],
                            "source_block_ids": ["BLOCK_003"],
                            "raw_text": "Python",
                            "raw_value": "Python",
                            "extraction_method": "semantic_llm",
                        }
                    }
                ]
            })
        }

        mock_transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=mock_payload)
        )
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(enabled=True, temperature=0.0)
            client = CVSemanticExtractor(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert res.success is True
            assert res.parser_mode == "semantic_llm"
            assert res.degraded is False
            assert res.semantic_model_error is None
            assert res.fallback_used is False
            assert res.canonical_cv.personal_info.full_name.raw_value == "Youssof El Karhani"
            assert res.canonical_cv.skills[0].raw_value == "Python"
            assert res.validation_report.is_valid is True

    # 2. Malformed JSON Response
    @pytest.mark.asyncio
    async def test_2_malformed_json_response(self, sample_two_column_layout_doc):
        """Model returns malformed/corrupted JSON. Must trigger fallback with explicit degraded record."""
        mock_payload = {
            "response": "```json\n{ corrupted_json: true, unterminated string ... "
        }

        mock_transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=mock_payload)
        )
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(enabled=True, fallback_to_heuristics=True)
            client = CVSemanticExtractor(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert res.success is True
            assert res.parser_mode == "heuristic_fallback"
            assert res.degraded is True
            assert "Failed to parse LLM JSON output" in res.semantic_model_error
            assert res.fallback_used is True
            assert res.canonical_cv is not None
            assert res.validation_report.is_valid is True

    # 3. Invalid Block IDs (Hallucinated IDs)
    @pytest.mark.asyncio
    async def test_3_invalid_block_ids_rejected(self, sample_two_column_layout_doc):
        """Model invents a block ID not in the request. The entity must be rejected."""
        mock_payload = {
            "response": json.dumps({
                "source_document_id": "youssof_cv_test.pdf",
                "personal_info": {
                    "full_name": {"raw_value": "Youssof El Karhani", "normalized_value": None},
                    "provenance": {
                        "source_pages": [1],
                        "source_block_ids": ["BLOCK_001"],
                        "raw_text": "Youssof El Karhani",
                        "extraction_method": "semantic_llm",
                    }
                },
                "skills": [
                    {
                        "raw_value": "RealSkill",
                        "normalized_value": None,
                        "provenance": {
                            "source_pages": [1],
                            "source_block_ids": ["BLOCK_003"],
                            "raw_text": "Python",
                            "raw_value": "Python",
                            "extraction_method": "semantic_llm",
                        }
                    },
                    {
                        # Hallucinated block ID: BLOCK_999 does not exist in request
                        "raw_value": "HallucinatedSkill",
                        "normalized_value": None,
                        "provenance": {
                            "source_pages": [1],
                            "source_block_ids": ["BLOCK_999"],
                            "raw_text": "Invented Skill",
                            "raw_value": "Invented Skill",
                            "extraction_method": "semantic_llm",
                        }
                    }
                ]
            })
        }

        mock_transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=mock_payload)
        )
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(enabled=True)
            client = CVSemanticExtractor(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert res.success is True
            # Hallucinated entity filtered out
            assert len(res.canonical_cv.skills) == 1
            assert res.canonical_cv.skills[0].raw_value == "RealSkill"
            assert len(res.validation_report.rejected_claims) == 1
            assert "BLOCK_999" in res.validation_report.rejected_claims[0]["errors"][0]

    # 4. Unsupported Facts / Missing Provenance
    def test_4_unsupported_facts_rejected(self):
        """Entity missing source_block_ids or missing raw_text must be rejected."""
        valid_ids = {"BLOCK_001", "BLOCK_002"}

        # Empty block IDs
        bad_prov_1 = ProvenanceMetadata(
            source_pages=[1],
            source_block_ids=[],
            raw_text="No block ID",
        )
        skill_1 = SemanticSkill(raw_value="Rust", provenance=bad_prov_1)
        res_1 = validate_entity_provenance(skill_1, valid_block_ids=valid_ids)
        assert res_1.is_valid is False
        assert ProvenanceErrorCode.EMPTY_SOURCE_BLOCK_IDS in res_1.error_codes

        # Empty raw text / raw value
        bad_prov_2 = ProvenanceMetadata(
            source_pages=[1],
            source_block_ids=["BLOCK_001"],
            raw_text="",
            raw_value="",
        )
        skill_2 = SemanticSkill(raw_value="", provenance=bad_prov_2)
        res_2 = validate_entity_provenance(skill_2, valid_block_ids=valid_ids)
        assert res_2.is_valid is False
        assert ProvenanceErrorCode.EMPTY_RAW_TEXT in res_2.error_codes

    # 5. Connection Timeout Handling
    @pytest.mark.asyncio
    async def test_5_connection_timeout_handling(self, sample_two_column_layout_doc):
        """Timeout triggers bounded retries then graceful fallback with degraded=True."""
        def handler(request):
            raise httpx.ConnectTimeout("Connection timed out to Ollama service")

        mock_transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(
                enabled=True,
                max_retries=2,
                initial_backoff_seconds=0.01,
                fallback_to_heuristics=True,
            )
            client = CVSemanticExtractor(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert res.success is True
            assert res.parser_mode == "heuristic_fallback"
            assert res.degraded is True
            assert "timed out" in res.semantic_model_error.lower()
            assert res.fallback_used is True
            assert res.canonical_cv is not None

    # 6. Temporary 502 Cold Start Recovery
    @pytest.mark.asyncio
    async def test_6_temporary_502_recovery(self, sample_two_column_layout_doc):
        """First request returns 502 Bad Gateway; second attempt succeeds."""
        attempt_count = 0

        def handler(request):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                return httpx.Response(502, text="Bad Gateway (Cold Start)")
            return httpx.Response(200, json={
                "response": json.dumps({
                    "source_document_id": "youssof_cv_test.pdf",
                    "personal_info": {
                        "full_name": {"raw_value": "Youssof El Karhani", "normalized_value": None},
                        "provenance": {
                            "source_pages": [1],
                            "source_block_ids": ["BLOCK_001"],
                            "raw_text": "Youssof El Karhani",
                            "extraction_method": "semantic_llm",
                        }
                    }
                })
            })

        mock_transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(
                enabled=True,
                max_retries=3,
                initial_backoff_seconds=0.01,
            )
            client = CVSemanticExtractor(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert attempt_count == 2
            assert res.success is True
            assert res.parser_mode == "semantic_llm"
            assert res.degraded is False
            assert res.semantic_model_error is None

    # 7. Exhausted Retries Returns Explicit Fallback
    @pytest.mark.asyncio
    async def test_7_exhausted_retries_returns_explicit_fallback(self, sample_two_column_layout_doc):
        """Persistent 502 across all retries returns explicit fallback with semantic_model_error."""
        attempt_count = 0

        def handler(request):
            nonlocal attempt_count
            attempt_count += 1
            return httpx.Response(502, text="Bad Gateway (Cold Start)")

        mock_transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(
                enabled=True,
                max_retries=2,
                initial_backoff_seconds=0.01,
                fallback_to_heuristics=True,
            )
            client = CVSemanticExtractor(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert attempt_count == 2
            assert res.success is True
            assert res.parser_mode == "heuristic_fallback"
            assert res.degraded is True
            assert "unavailable after 2 bounded attempts" in res.semantic_model_error
            assert res.fallback_used is True

    # 8. Feature Flag Disabled Bypasses LLM
    @pytest.mark.asyncio
    async def test_8_feature_disabled_bypasses_llm(self, sample_two_column_layout_doc):
        """When CV_EXTRACTION_LLM_ENABLED=false, LLM is not called and heuristic fallback runs."""
        call_count = 0

        def handler(request):
            nonlocal call_count
            call_count += 1
            return httpx.Response(200, json={"response": "{}"})

        mock_transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(enabled=False, fallback_to_heuristics=True)
            client = CVSemanticExtractor(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert call_count == 0  # Zero HTTP calls made!
            assert res.success is True
            assert res.parser_mode == "heuristic_fallback"
            assert res.degraded is True
            assert "CV_EXTRACTION_LLM_ENABLED is false" in res.semantic_model_error
            assert res.fallback_used is True
            assert res.canonical_cv is not None
            assert res.canonical_cv.personal_info.full_name.raw_value == "Youssof El Karhani"
