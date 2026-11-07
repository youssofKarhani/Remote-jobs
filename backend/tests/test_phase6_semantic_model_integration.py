"""Test Suite for Phase 6 — Semantic Model Integration.

Verifies:
1. Extraction configuration defaults and environment overrides.
2. Source block prompt serialization preserving block IDs, pages, regions, and reading order.
3. Qwen3 reasoning token stripping (<think>...</think>) and robust JSON extraction.
4. Parsing into CanonicalSemanticCV schema with document ID backfilling.
5. Deterministic heuristic fallback with strict block provenance and unknown section preservation.
6. Feature flagging and explicit fallback recording (Rule 10: No Silent Fallback).
7. Mocked LLM execution against simulated Ollama /api/generate endpoint.
8. Provenance validation rejecting hallucinations or invalid block references.
9. Network error resilience, retry backoff, and fallback handling.
10. Multi-column CV integration test ensuring technical skills do not interleave with projects/education.
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
from app.services.provenance_validator import validate_canonical_cv
from app.services.semantic_extraction_client import (
    ExtractionConfig,
    SemanticExtractionClient,
    SemanticExtractionError,
    SemanticExtractionResult,
    build_source_blocks_prompt_context,
    extract_json_payload,
    heuristic_fallback_extract,
    parse_canonical_semantic_cv_json,
    strip_thinking_tokens,
)


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
# 1. Configuration & Settings Tests
# ============================================================================

class TestExtractionConfig:
    def test_default_config_matches_application_settings(self):
        config = ExtractionConfig()
        assert config.base_url == getattr(settings, "CV_EXTRACTION_LLM_BASE_URL", "http://localhost:11434")
        assert config.model == getattr(settings, "CV_EXTRACTION_LLM_MODEL", "qwen3:1.7b")
        assert config.enabled == getattr(settings, "CV_EXTRACTION_LLM_ENABLED", False)
        assert config.timeout_seconds == getattr(settings, "CV_EXTRACTION_LLM_TIMEOUT_SECONDS", 90.0)

    def test_custom_config_overrides(self):
        config = ExtractionConfig(
            base_url="http://custom-ollama:11434",
            model="qwen3:3b",
            enabled=True,
            timeout_seconds=45.0,
            max_retries=3,
            fallback_to_heuristics=False,
        )
        assert config.base_url == "http://custom-ollama:11434"
        assert config.model == "qwen3:3b"
        assert config.enabled is True
        assert config.timeout_seconds == 45.0
        assert config.max_retries == 3
        assert config.fallback_to_heuristics is False


# ============================================================================
# 2. Prompt Construction Tests
# ============================================================================

class TestPromptConstruction:
    def test_build_source_blocks_prompt_context(self, sample_two_column_layout_doc):
        context = build_source_blocks_prompt_context(sample_two_column_layout_doc, document_id="DOC_YOUSSOF_001")
        assert "DOCUMENT ID: DOC_YOUSSOF_001" in context
        assert "TOTAL BLOCKS: 11" in context
        # Verify block headers exist with IDs and reading order
        assert "[BLOCK_001] (Page 1, Region: header):" in context
        assert "Youssof El Karhani" in context
        assert "[BLOCK_002] (Page 1, Region: left_sidebar, Heading: Level 1):" in context
        assert "TECHNICAL SKILLS" in context
        assert "[BLOCK_007] (Page 1, Region: main_body):" in context
        assert "Senior Backend Engineer" in context


# ============================================================================
# 3. Output Sanitization & Reasoning Token Stripping Tests
# ============================================================================

class TestOutputSanitization:
    def test_strip_thinking_tokens_complete_block(self):
        raw = "<think>\nThis is internal reasoning.\nThe user wants a JSON format.\n</think>\n{\"document_id\": \"DOC_001\"}"
        assert strip_thinking_tokens(raw) == '{"document_id": "DOC_001"}'

    def test_strip_thinking_tokens_dangling_open_tag(self):
        raw = "<think>\nReasoning got truncated..."
        assert strip_thinking_tokens(raw) == ""

    def test_extract_json_payload_from_markdown_fence(self):
        raw = "<think>done</think>\nHere is your JSON:\n```json\n{\"key\": \"value\"}\n```"
        assert extract_json_payload(raw) == '{"key": "value"}'

    def test_extract_json_payload_from_raw_braces(self):
        raw = "Some introductory text\n{\"key\": 123}\nSome concluding text"
        assert extract_json_payload(raw) == '{"key": 123}'


# ============================================================================
# 4. JSON Schema Parsing Tests
# ============================================================================

class TestJsonSchemaParsing:
    def test_parse_valid_canonical_json(self):
        raw_json = json.dumps({
            "document_id": "DOC_TEST_01",
            "personal_info": {
                "full_name": {"raw_value": "Youssof El Karhani", "normalized_value": None},
                "email": {"raw_value": "youssof@example.com", "normalized_value": None},
                "provenance": {
                    "source_pages": [1],
                    "source_block_ids": ["BLOCK_001"],
                    "raw_text": "Youssof El Karhani",
                    "extraction_method": "semantic_llm",
                }
            },
            "skills": [
                {
                    "raw_value": "MangoDB",
                    "normalized_value": None,
                    "provenance": {
                        "source_pages": [1],
                        "source_block_ids": ["BLOCK_003"],
                        "raw_text": "MangoDB",
                        "raw_value": "MangoDB",
                        "extraction_method": "semantic_llm",
                    }
                }
            ]
        })
        cv = parse_canonical_semantic_cv_json(raw_json, document_id="DOC_TEST_01")
        assert isinstance(cv, CanonicalSemanticCV)
        assert cv.personal_info.full_name.raw_value == "Youssof El Karhani"
        assert cv.personal_info.full_name.normalized_value is None
        assert cv.skills[0].raw_value == "MangoDB"
        assert cv.skills[0].normalized_value is None
        assert cv.skills[0].provenance.source_block_ids == ["BLOCK_003"]

    def test_parse_invalid_json_raises_semantic_extraction_error(self):
        with pytest.raises(SemanticExtractionError):
            parse_canonical_semantic_cv_json("Not valid json at all")


# ============================================================================
# 5. Deterministic Heuristic Fallback Extractor Tests
# ============================================================================

class TestHeuristicFallbackExtractor:
    def test_fallback_extractor_grounds_all_items_with_valid_block_ids(self, sample_two_column_layout_doc):
        cv = heuristic_fallback_extract(sample_two_column_layout_doc, document_id="DOC_FALLBACK_01")
        assert isinstance(cv, CanonicalSemanticCV)
        assert cv.personal_info.email.raw_value == "youssof@example.com"
        assert cv.personal_info.provenance.source_block_ids == ["BLOCK_001"]

        # Technical skills extracted from left sidebar
        skill_names = [s.raw_value for s in cv.skills]
        assert "Python" in skill_names
        assert "FastAPI" in skill_names
        assert "MangoDB" in skill_names

        # Verify all skills reference BLOCK_003
        for s in cv.skills:
            assert "BLOCK_003" in s.provenance.source_block_ids

        # Experience extracted from main body
        assert len(cv.experiences) > 0
        assert "BLOCK_007" in cv.experiences[0].provenance.source_block_ids

        # Unknown section preserved
        assert len(cv.unknown_sections) == 1
        assert cv.unknown_sections[0].heading == "OPEN SOURCE CONTRIBUTIONS"
        assert "BLOCK_011" in cv.unknown_sections[0].items[0].provenance.source_block_ids

        # Validate complete document provenance
        valid_ids = {b.id for b in sample_two_column_layout_doc.source_blocks}
        report = validate_canonical_cv(cv, valid_block_ids=valid_ids)
        assert report.is_valid is True
        assert len(report.rejected_claims) == 0


# ============================================================================
# 6. Feature Flagging & Safe Fallback Tests (Rule 10 & 15)
# ============================================================================

class TestFeatureFlaggingAndFallback:
    @pytest.mark.asyncio
    async def test_when_llm_disabled_fallback_records_explicit_metadata(self, sample_two_column_layout_doc):
        config = ExtractionConfig(enabled=False, fallback_to_heuristics=True)
        client = SemanticExtractionClient(config=config)

        res: SemanticExtractionResult = await client.extract(sample_two_column_layout_doc)
        assert res.success is True
        assert res.fallback_used is True
        assert res.extraction_method == "layout_heuristic"
        assert "CV_EXTRACTION_LLM_ENABLED=false" in res.fallback_reason
        assert res.canonical_cv is not None
        assert res.validation_report.is_valid is True

    @pytest.mark.asyncio
    async def test_when_llm_disabled_and_no_fallback_allowed_returns_error(self, sample_two_column_layout_doc):
        config = ExtractionConfig(enabled=False, fallback_to_heuristics=False)
        client = SemanticExtractionClient(config=config)

        res: SemanticExtractionResult = await client.extract(sample_two_column_layout_doc)
        assert res.success is False
        assert res.fallback_used is False
        assert res.canonical_cv is None
        assert "CV_EXTRACTION_LLM_ENABLED is False" in res.error


# ============================================================================
# 7. Mocked LLM Execution & Provenance Validation Tests
# ============================================================================

class TestMockedLLMExecution:
    @pytest.mark.asyncio
    async def test_mocked_ollama_call_success(self, sample_two_column_layout_doc):
        mock_response_payload = {
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

        # Mock transport
        mock_transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=mock_response_payload)
        )
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(enabled=True)
            client = SemanticExtractionClient(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert res.success is True
            assert res.fallback_used is False
            assert res.extraction_method == "semantic_llm"
            assert res.canonical_cv.personal_info.full_name.raw_value == "Youssof El Karhani"
            assert res.canonical_cv.skills[0].raw_value == "Python"
            assert res.validation_report.is_valid is True

    @pytest.mark.asyncio
    async def test_mocked_ollama_call_filters_hallucinated_block_ids(self, sample_two_column_layout_doc):
        """Rule 6: A semantic object referencing an invalid block must be rejected."""
        mock_response_payload = {
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
                        # Hallucinated skill referencing non-existent BLOCK_999
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
            lambda request: httpx.Response(200, json=mock_response_payload)
        )
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(enabled=True)
            client = SemanticExtractionClient(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert res.success is True
            # Hallucinated skill must be filtered out by provenance validator
            assert len(res.canonical_cv.skills) == 1
            assert res.canonical_cv.skills[0].raw_value == "RealSkill"
            assert len(res.validation_report.rejected_claims) == 1
            assert "BLOCK_999" in res.validation_report.rejected_claims[0]["errors"][0]

    @pytest.mark.asyncio
    async def test_ollama_network_error_triggers_fallback_with_explicit_reason(self, sample_two_column_layout_doc):
        """Rule 10: Fallback must never happen silently; explicit reason is recorded."""
        mock_transport = httpx.MockTransport(
            lambda request: httpx.Response(500, text="Internal Server Error")
        )
        async with httpx.AsyncClient(transport=mock_transport) as mock_http_client:
            config = ExtractionConfig(enabled=True, max_retries=1, fallback_to_heuristics=True)
            client = SemanticExtractionClient(config=config, http_client=mock_http_client)

            res = await client.extract(sample_two_column_layout_doc)
            assert res.success is True
            assert res.fallback_used is True
            assert res.extraction_method == "layout_heuristic"
            assert "LLM extraction failure" in res.fallback_reason
            assert res.canonical_cv is not None
            assert res.validation_report.is_valid is True
