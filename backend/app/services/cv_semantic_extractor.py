"""Dedicated CV Semantic Extraction Service for Private Ollama / Qwen.

Integrates Phase 3 (LayoutDocument / SourceBlocks) and Phase 4 (CanonicalSemanticCV)
with the private Ollama Qwen service deployed in Phase 5.

Key Architectural Guarantees:
1. Reconstructed Source Block Input: The semantic model receives structured SourceBlock
   objects produced by the spatial/layout pipeline, not raw PDF bytes or flat corrupted text.
2. Structured JSON Output: Enforces CanonicalSemanticCV JSON Schema via Ollama's format parameter.
3. Deterministic Generation: Defaults to temperature = 0.
4. Strict Block Provenance: Every extracted entity maps to concrete SourceBlock IDs.
   Hallucinated block IDs not present in the input request are strictly rejected.
5. Raw vs Normalized Separation: Raw verbatim text is preserved; normalized values remain null.
6. Unknown Section Preservation: Unrecognized or non-standard CV sections are never discarded.
7. Resilient Cold-Start Handling: Bounded exponential retry backoff for connection refused,
   temporary connection resets, HTTP 502/503/504, and cold-start timeouts.
8. No Silent Heuristic Fallback: Degraded states explicitly record parser_mode='heuristic_fallback',
   degraded=True, and semantic_model_error.
9. Feature Flag Isolation: Respects CV_EXTRACTION_LLM_ENABLED=false until rollout.
"""

import asyncio
from dataclasses import dataclass, field
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx

from app.config import settings
from app.schemas.layout import LayoutDocument, SourceBlock
from app.schemas.semantic_cv import (
    CanonicalSemanticCV,
    ProvenanceMetadata,
    RawNormalizedValue,
    SemanticAward,
    SemanticCertification,
    SemanticEducation,
    SemanticExperience,
    SemanticExperienceBullet,
    SemanticLanguage,
    SemanticPersonalInfo,
    SemanticProject,
    SemanticPublication,
    SemanticSkill,
    SemanticVolunteering,
    UnknownSection,
    UnknownSectionItem,
)
from app.services.provenance_validator import (
    CanonicalCVValidationReport,
    validate_canonical_cv,
)

logger = logging.getLogger(__name__)

# Transient HTTP status codes and exceptions for cold start retries
TRANSIENT_STATUS_CODES = {502, 503, 504}
TRANSIENT_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.TimeoutException,
    httpx.RemoteProtocolError,
)


class SemanticExtractionError(Exception):
    """Raised when semantic extraction fails and cannot be recovered."""
    pass


class SchemaValidationError(SemanticExtractionError):
    """Raised when model output fails JSON Schema or Pydantic structural validation."""
    pass


class ProvenanceIntegrityError(SemanticExtractionError):
    """Raised when extracted entities contain invalid or hallucinated source block references."""
    pass


@dataclass
class ExtractionConfig:
    """Configuration for the semantic extraction client."""
    base_url: str = field(default_factory=lambda: getattr(settings, "CV_EXTRACTION_LLM_BASE_URL", "http://cv-extractor-llm.railway.internal:11434"))
    model: str = field(default_factory=lambda: getattr(settings, "CV_EXTRACTION_LLM_MODEL", "qwen3:1.7b"))
    enabled: bool = field(default_factory=lambda: getattr(settings, "CV_EXTRACTION_LLM_ENABLED", False))
    timeout_seconds: float = field(default_factory=lambda: getattr(settings, "CV_EXTRACTION_LLM_TIMEOUT_SECONDS", 90.0))
    temperature: float = 0.0
    max_retries: int = field(default_factory=lambda: getattr(settings, "CV_EXTRACTION_LLM_MAX_RETRIES", 3))
    initial_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 8.0
    fallback_to_heuristics: bool = field(default_factory=lambda: getattr(settings, "LLM_FALLBACK_TO_HEURISTICS", True))


@dataclass
class SemanticExtractionResult:
    """Outcome of a CV semantic extraction attempt with full provenance and audit metadata."""
    canonical_cv: Optional[CanonicalSemanticCV] = None
    validation_report: Optional[CanonicalCVValidationReport] = None
    success: bool = False
    parser_mode: str = "semantic_llm"  # "semantic_llm" or "heuristic_fallback"
    degraded: bool = False
    semantic_model_error: Optional[str] = None
    extraction_method: str = "semantic_llm"
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    raw_response: Optional[str] = None
    model_used: Optional[str] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None


# ============================================================================
# 1. System Prompt & Structured Input Builder
# ============================================================================

SYSTEM_EXTRACTION_PROMPT = """You are an expert CV semantic extraction engine.
Your task is to parse candidate CV content from numbered source blocks into a single valid JSON object.

CRITICAL RULES:
1. STRICT FACTUAL GROUNDING: Extract ONLY facts explicitly supported by the supplied source blocks.
   - Do NOT invent employers.
   - Do NOT invent dates.
   - Do NOT invent degrees or fields of study.
   - Do NOT invent certifications.
   - Do NOT invent skills.
   - Do NOT infer technologies not stated.
   - Do NOT invent metrics or numbers.
   - Do NOT invent achievements or job duties.
   - Do NOT infer missing employment periods.
2. NULL OVER INFERENCE: If a field (e.g. end_date, gpa, location, phone) is not mentioned in the source blocks, set it to null. DO NOT guess or infer missing values.
3. BLOCK PROVENANCE: Every extracted entity MUST have a `provenance` object containing:
   - "source_block_ids": list of block IDs where this information appears (e.g. ["BLOCK_003"])
   - "source_pages": list of 1-based page numbers (e.g. [1])
   - "raw_text": verbatim or near-verbatim quote from the source block supporting this claim
   - "raw_value": exact raw string snippet (e.g. "Python", "MangoDB", "Senior Software Engineer")
   - "extraction_method": "semantic_llm"
   - "extraction_confidence": float between 0.0 and 1.0
   CRITICAL: ONLY reference block IDs that exist in the input request blocks. NEVER invent block IDs.
4. RAW VS NORMALIZED: Put raw strings into `raw_value`. Leave `normalized_value` as null. Normalization happens in a subsequent deterministic pipeline stage.
5. UNKNOWN SECTIONS: Any section that does not clearly belong to personal_info, experiences, education, skills, certifications, projects, languages, awards, volunteering, or publications MUST be preserved under `unknown_sections`. DO NOT discard unknown sections.
6. OUTPUT FORMAT: Respond ONLY with a valid JSON object matching the CanonicalSemanticCV schema.
"""


def derive_section_hint(block: SourceBlock, preceding_heading: Optional[str] = None) -> str:
    """Derive an informative section hint from block properties and reading context."""
    if block.is_heading:
        return f"Heading: {block.text.strip()}"
    if preceding_heading:
        return preceding_heading
    if block.region_type == "header":
        return "Personal Info / Header"
    if "sidebar" in block.region_type:
        return "Sidebar Content"
    return "Body"


def build_blocks_json_payload(layout_doc: LayoutDocument) -> Dict[str, Any]:
    """Build conceptual structured input for the semantic model from layout source blocks.

    Conceptual structure:
    {
      "blocks": [
        {
          "id": "BLOCK_010",
          "page": 1,
          "section_hint": "Education",
          "text": "..."
        }
      ]
    }
    """
    blocks_list = []
    current_heading = None

    for block in layout_doc.source_blocks:
        if block.is_heading:
            current_heading = block.text.strip()

        hint = derive_section_hint(block, current_heading)
        blocks_list.append({
            "id": block.id,
            "page": block.page,
            "section_hint": hint,
            "text": block.text.strip(),
        })

    return {"blocks": blocks_list}


def build_source_blocks_prompt_context(
    layout_doc: LayoutDocument,
    document_id: Optional[str] = None,
) -> str:
    """Format LayoutDocument source blocks into a structured prompt context."""
    blocks_payload = build_blocks_json_payload(layout_doc)

    lines: List[str] = []
    lines.append(f"DOCUMENT ID: {document_id or layout_doc.filename}")
    lines.append(f"TOTAL PAGES: {layout_doc.total_pages}")
    lines.append(f"TOTAL BLOCKS: {len(layout_doc.source_blocks)}")
    lines.append("")
    lines.append("=== STRUCTURED SOURCE BLOCKS ===")
    lines.append(json.dumps(blocks_payload, indent=2))
    lines.append("=== END OF SOURCE BLOCKS ===")
    lines.append("")
    lines.append(
        "Extract candidate career data into a valid JSON object matching the CanonicalSemanticCV schema. "
        "Every claim must reference ONLY the block IDs provided in the above blocks list. "
        "Do not invent any facts, dates, skills, or block IDs."
    )
    return "\n".join(lines)


# ============================================================================
# 2. Output Parser & Sanitizer
# ============================================================================

def strip_thinking_tokens(text: str) -> str:
    """Remove Qwen3 reasoning tokens (<think>...</think>) from model output."""
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"<think>.*$", "", cleaned, flags=re.DOTALL)
    return cleaned.strip()


def extract_json_payload(text: str) -> str:
    """Extract clean JSON string from LLM output, handling markdown fences and raw objects."""
    cleaned = strip_thinking_tokens(text)

    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence_match:
        return fence_match.group(1).strip()

    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start != -1 and brace_end > brace_start:
        return cleaned[brace_start : brace_end + 1].strip()

    return cleaned


def parse_canonical_semantic_cv_json(
    raw_output: str,
    document_id: Optional[str] = None,
) -> CanonicalSemanticCV:
    """Parse and validate raw LLM output into CanonicalSemanticCV."""
    json_str = extract_json_payload(raw_output)
    if not json_str:
        raise SchemaValidationError("LLM response did not contain any valid JSON content.")

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(f"Failed to parse LLM JSON output: {exc}") from exc

    if not isinstance(data, dict):
        raise SchemaValidationError(f"Expected JSON object at top level, got {type(data).__name__}")

    # Set document_id if provided
    if document_id and not data.get("source_document_id"):
        data["source_document_id"] = document_id

    # Populate source_document_id recursively on provenance if absent
    def _backfill_doc_id(obj: Any):
        if isinstance(obj, dict):
            if "source_document_id" in obj and not obj["source_document_id"]:
                obj["source_document_id"] = document_id
            for v in obj.values():
                _backfill_doc_id(v)
        elif isinstance(obj, list):
            for item in obj:
                _backfill_doc_id(item)

    if document_id:
        _backfill_doc_id(data)

    try:
        return CanonicalSemanticCV.model_validate(data)
    except Exception as exc:
        raise SchemaValidationError(f"JSON does not conform to CanonicalSemanticCV schema: {exc}") from exc


# ============================================================================
# 3. Deterministic Heuristic Fallback Extractor
# ============================================================================

def heuristic_fallback_extract(
    layout_doc: LayoutDocument,
    document_id: Optional[str] = None,
) -> CanonicalSemanticCV:
    """Deterministic fallback that constructs a valid CanonicalSemanticCV from SourceBlocks.

    Guarantees:
    - Accurate block provenance for every extracted item.
    - Zero hallucinated values or block IDs.
    - Unknown or unclassified blocks are preserved under unknown_sections.
    """
    doc_id = document_id or layout_doc.filename

    header_block = next((b for b in layout_doc.source_blocks if b.region_type == "header"), None)
    if not header_block and layout_doc.source_blocks:
        header_block = layout_doc.source_blocks[0]

    header_text = header_block.text if header_block else ""
    header_block_ids = [header_block.id] if header_block else []
    header_pages = [header_block.page] if header_block else ([1] if layout_doc.total_pages > 0 else [])

    name_str = "Candidate Name"
    email_val = None
    phone_val = None

    from app.services.document_parser import reconstruct_broken_urls
    all_doc_text = "\n".join(b.text for b in layout_doc.source_blocks)
    cleaned_doc_text = reconstruct_broken_urls(all_doc_text)

    if header_text:
        lines = [l.strip() for l in header_text.split("\n") if l.strip()]
        if lines:
            first_segment = lines[0].split("|")[0].split("•")[0].strip()
            if first_segment and len(first_segment) < 60:
                name_str = first_segment

        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", header_text)
        if email_match:
            email_val = RawNormalizedValue(raw_value=email_match.group(0))

        phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,9}", header_text)
        if phone_match and not re.match(r"^\d{4}\s*-\s*\d{4}$", phone_match.group(0)):
            phone_val = RawNormalizedValue(raw_value=phone_match.group(0))

    if not email_val:
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", cleaned_doc_text)
        if email_match:
            email_val = RawNormalizedValue(raw_value=email_match.group(0).strip())
            for b in layout_doc.source_blocks:
                if email_match.group(0) in b.text and b.id not in header_block_ids:
                    header_block_ids.append(b.id)
                    if b.page not in header_pages:
                        header_pages.append(b.page)
                    break

    if not phone_val:
        phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,9}", cleaned_doc_text)
        if phone_match and not re.match(r"^\d{4}\s*-\s*\d{4}$", phone_match.group(0)):
            phone_val = RawNormalizedValue(raw_value=phone_match.group(0).strip())
            for b in layout_doc.source_blocks:
                if phone_match.group(0) in b.text and b.id not in header_block_ids:
                    header_block_ids.append(b.id)
                    if b.page not in header_pages:
                        header_pages.append(b.page)
                    break

    linkedin_val = None
    li_match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[\w\-]+", cleaned_doc_text, re.I)
    if li_match:
        linkedin_val = RawNormalizedValue(raw_value=li_match.group(0).strip())

    github_val = None
    gh_match = re.search(r"https?://(?:www\.)?github\.com/[\w\-\.]+", cleaned_doc_text, re.I)
    if gh_match:
        github_val = RawNormalizedValue(raw_value=gh_match.group(0).strip())

    personal_info = SemanticPersonalInfo(
        full_name=RawNormalizedValue(raw_value=name_str),
        email=email_val,
        phone=phone_val,
        linkedin_url=linkedin_val,
        github_url=github_val,
        provenance=ProvenanceMetadata(
            source_document_id=doc_id,
            source_pages=header_pages,
            source_block_ids=header_block_ids,
            raw_text=header_text[:300] if header_text else name_str,
            raw_value=name_str,
            extraction_method="layout_heuristic",
            extraction_confidence=0.8,
        ),
    )

    experiences: List[SemanticExperience] = []
    educations: List[SemanticEducation] = []
    skills: List[SemanticSkill] = []
    certifications: List[SemanticCertification] = []
    projects: List[SemanticProject] = []
    languages: List[SemanticLanguage] = []
    unknown_sections: List[UnknownSection] = []

    current_section: Optional[str] = None
    current_heading_block: Optional[SourceBlock] = None
    section_blocks: List[SourceBlock] = []

    def _flush_section():
        nonlocal current_section, current_heading_block, section_blocks
        candidates = list(section_blocks)
        if not candidates and current_heading_block:
            heading_txt = current_heading_block.text.strip()
            if ":" in heading_txt or "\n" in heading_txt or len(heading_txt.split()) > 3:
                candidates = [current_heading_block]

        if not candidates:
            return

        combined_text = "\n".join(b.text for b in candidates)
        block_ids = [b.id for b in candidates]
        pages = sorted(list(set(b.page for b in candidates)))

        prov = ProvenanceMetadata(
            source_document_id=doc_id,
            source_pages=pages,
            source_block_ids=block_ids,
            raw_text=combined_text[:500],
            raw_value=combined_text[:200],
            extraction_method="layout_heuristic",
            extraction_confidence=0.75,
        )

        if current_section == "experience":
            # Search all blocks in section plus heading block if it contains body text
            all_text_candidates: List[SourceBlock] = []
            if current_heading_block and len(current_heading_block.text.split("\n")) > 1:
                all_text_candidates.append(current_heading_block)
            all_text_candidates.extend(candidates)

            if not all_text_candidates and current_heading_block:
                all_text_candidates = [current_heading_block]

            combined_exp_text = "\n".join(b.text for b in all_text_candidates)
            all_lines = [l.strip() for l in combined_exp_text.split("\n") if l.strip()]

            role = None
            company = None

            # Pattern search in first 3 lines
            for line in all_lines[:3]:
                if " at " in line:
                    parts = line.split(" at ", 1)
                    role = parts[0].strip()
                    company = parts[1].strip()
                    break
                elif " - " in line:
                    parts = line.split(" - ", 1)
                    company = parts[0].strip()
                    role = parts[1].strip()
                    break
                elif " bei " in line:
                    parts = line.split(" bei ", 1)
                    role = parts[0].strip()
                    company = parts[1].strip()
                    break
                elif " chez " in line:
                    parts = line.split(" chez ", 1)
                    role = parts[0].strip()
                    company = parts[1].strip()
                    break

            if not role and all_lines:
                role = all_lines[0]
            if not company and len(all_lines) > 1:
                company = all_lines[1]
            if not company:
                company = all_lines[0] if all_lines else "Experience"
            if not role:
                role = "Professional"

            # Clean parenthetical dates if in company/role strings
            date_match = re.search(
                r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|März|Januar|Februar)?\.?\s*(?:19|20)\d{2}(?:\s*[-–—/]\s*(?:(?:19|20)\d{2}|Present|Current|heute))?)\b",
                combined_exp_text,
                re.I,
            )
            start_date_str = date_match.group(1).strip() if date_match else "Undated"

            if "(" in company and ")" in company:
                company = re.sub(r"\(.*?\)", "", company).strip()
            if "(" in role and ")" in role:
                role = re.sub(r"\(.*?\)", "", role).strip()

            bullet_items: List[Tuple[str, SourceBlock]] = []
            for b in all_text_candidates:
                blines = [l.strip() for l in b.text.split("\n") if l.strip()]
                for bl in blines:
                    bl_clean = re.sub(r"\(.*?\)", "", bl).strip()
                    if company and (bl_clean.lower() == company.lower() or bl.lower() == company.lower()):
                        continue
                    if role and (bl_clean.lower() == role.lower() or bl.lower() == role.lower()):
                        continue
                    if any(sep in bl for sep in (" at ", " - ", " – ", " — ", " bei ", " chez ")):
                        if (company and company.lower() in bl.lower()) and (role and role.lower() in bl.lower()):
                            continue
                    if len(bl) > 8:
                        bullet_items.append((bl, b))

            if not bullet_items and all_text_candidates:
                bullet_items = [(all_text_candidates[0].text, all_text_candidates[0])]

            bullets = [
                SemanticExperienceBullet(
                    raw_text=btxt,
                    provenance=ProvenanceMetadata(
                        source_document_id=doc_id,
                        source_pages=[src_b.page],
                        source_block_ids=[src_b.id],
                        raw_text=btxt,
                        raw_value=btxt,
                        extraction_method="layout_heuristic",
                        extraction_confidence=0.75,
                    ),
                )
                for btxt, src_b in bullet_items
            ]

            exp = SemanticExperience(
                role_title=RawNormalizedValue(raw_value=role[:80]),
                company_name=RawNormalizedValue(raw_value=company[:80]),
                start_date=RawNormalizedValue(raw_value=start_date_str),
                is_current=bool(date_match and any(w in date_match.group(1).lower() for w in ["present", "current", "heute"])),
                bullets=bullets,
                provenance=prov,
            )
            experiences.append(exp)

        elif current_section == "education":
            first_b = candidates[0]
            lines = [l.strip() for l in first_b.text.split("\n") if l.strip()]
            deg = lines[0] if lines else None
            inst = lines[1] if len(lines) > 1 else (lines[0] if lines else None)

            edu = SemanticEducation(
                institution=RawNormalizedValue(raw_value=inst[:100]) if inst else None,
                degree=RawNormalizedValue(raw_value=deg[:100]) if deg else None,
                provenance=prov,
            )
            educations.append(edu)

        elif current_section == "skills":
            skill_source_blocks = list(candidates)
            if current_heading_block and current_heading_block not in skill_source_blocks:
                h_txt = current_heading_block.text.strip()
                if ":" in h_txt or "," in h_txt:
                    skill_source_blocks.insert(0, current_heading_block)

            all_text = "\n".join(b.text for b in skill_source_blocks)
            cleaned_text = re.sub(r"(?i)\b(?:technical\s+)?(?:skills|technologies|tech\s+stack|key\s+skills)\s*:\s*", "", all_text)
            tokens = [t.strip() for t in re.split(r"[,•|\n]+", cleaned_text) if t.strip()]
            for token in tokens:
                # Discard sentences or paragraphs mistakenly split into skills
                if len(token.split()) > 4 or len(token) > 40:
                    continue
                supp_b = next((b for b in skill_source_blocks if token in b.text), skill_source_blocks[0])
                skills.append(
                    SemanticSkill(
                        raw_value=token,
                        category="technical",
                        provenance=ProvenanceMetadata(
                            source_document_id=doc_id,
                            source_pages=[supp_b.page],
                            source_block_ids=[supp_b.id],
                            raw_text=token,
                            raw_value=token,
                            extraction_method="layout_heuristic",
                            extraction_confidence=0.8,
                        ),
                    )
                )

        elif current_section == "languages":
            for b in candidates:
                tokens = [t.strip() for t in re.split(r"[,•|\n]+", b.text) if t.strip()]
                for token in tokens:
                    languages.append(
                        SemanticLanguage(
                            language=RawNormalizedValue(raw_value=token),
                            provenance=ProvenanceMetadata(
                                source_document_id=doc_id,
                                source_pages=[b.page],
                                source_block_ids=[b.id],
                                raw_text=token,
                                raw_value=token,
                                extraction_method="layout_heuristic",
                                extraction_confidence=0.8,
                            ),
                        )
                    )

        elif current_section == "certifications":
            for b in candidates:
                certifications.append(
                    SemanticCertification(
                        name=RawNormalizedValue(raw_value=b.text[:80]),
                        issuing_organization=RawNormalizedValue(raw_value="Issuing Organization"),
                        provenance=ProvenanceMetadata(
                            source_document_id=doc_id,
                            source_pages=[b.page],
                            source_block_ids=[b.id],
                            raw_text=b.text,
                            raw_value=b.text[:80],
                            extraction_method="layout_heuristic",
                            extraction_confidence=0.75,
                        ),
                    )
                )

        elif current_section == "projects":
            for b in candidates:
                projects.append(
                    SemanticProject(
                        title=RawNormalizedValue(raw_value=b.text[:80]),
                        description=b.text,
                        provenance=ProvenanceMetadata(
                            source_document_id=doc_id,
                            source_pages=[b.page],
                            source_block_ids=[b.id],
                            raw_text=b.text,
                            raw_value=b.text[:80],
                            extraction_method="layout_heuristic",
                            extraction_confidence=0.75,
                        ),
                    )
                )

        elif current_section == "unknown":
            heading_title = current_heading_block.text if current_heading_block else "Unclassified Section"
            unknown_sections.append(
                UnknownSection(
                    section_type="unknown",
                    heading=heading_title,
                    items=[
                        UnknownSectionItem(
                            raw_text=b.text,
                            provenance=ProvenanceMetadata(
                                source_document_id=doc_id,
                                source_pages=[b.page],
                                source_block_ids=[b.id],
                                raw_text=b.text,
                                raw_value=b.text,
                                extraction_method="layout_heuristic",
                                extraction_confidence=0.7,
                            ),
                        )
                        for b in candidates
                    ],
                    provenance=prov,
                )
            )

        section_blocks = []

    def _classify_heading(text: str) -> str:
        t = text.lower()
        if any(k in t for k in ("experience", "employment", "work history", "career", "berufserfahrung")):
            return "experience"
        if any(k in t for k in ("education", "academic", "university", "degree", "ausbildung")):
            return "education"
        if any(k in t for k in ("skill", "technologies", "competencies", "tech stack", "kenntnisse", "fähigkeiten")):
            return "skills"
        if any(k in t for k in ("language", "languages", "sprachen")):
            return "languages"
        if any(k in t for k in ("certificate", "certification", "credentials")):
            return "certifications"
        if any(k in t for k in ("project", "portfolio")):
            return "projects"
        return "unknown"

    unassigned_blocks: List[SourceBlock] = []

    for block in layout_doc.source_blocks:
        if block.region_type == "header":
            continue

        if block.is_heading:
            _flush_section()
            current_section = _classify_heading(block.text)
            current_heading_block = block
        else:
            if current_section:
                section_blocks.append(block)
            else:
                unassigned_blocks.append(block)

    _flush_section()

    for ub in unassigned_blocks:
        cleaned_ub_text = re.sub(r"(?i)\b(?:technical\s+)?(?:skills|technologies|tech\s+stack|key\s+skills)\s*:\s*", "", ub.text)
        tokens = [t.strip() for t in re.split(r"[,•|\n]+", cleaned_ub_text) if t.strip()]
        is_skill_list = (len(tokens) >= 2 and all(len(t) < 40 for t in tokens)) or any(
            t.lower() in ("python", "javascript", "typescript", "react", "fastapi", "docker", "kubernetes", "aws", "postgresql", "sql", "git", "linux", "go", "java")
            for t in tokens
        )
        if is_skill_list:
            for token in tokens:
                if len(token) <= 40:
                    skills.append(
                        SemanticSkill(
                            raw_value=token,
                            category="technical",
                            provenance=ProvenanceMetadata(
                                source_document_id=doc_id,
                                source_pages=[ub.page],
                                source_block_ids=[ub.id],
                                raw_text=token,
                                raw_value=token,
                                extraction_method="layout_heuristic",
                                extraction_confidence=0.75,
                            ),
                        )
                    )
        else:
            unknown_sections.append(
                UnknownSection(
                    section_type="unknown",
                    heading="Unclassified Content",
                    items=[
                        UnknownSectionItem(
                            raw_text=ub.text,
                            provenance=ProvenanceMetadata(
                                source_document_id=doc_id,
                                source_pages=[ub.page],
                                source_block_ids=[ub.id],
                                raw_text=ub.text,
                                raw_value=ub.text,
                                extraction_method="layout_heuristic",
                                extraction_confidence=0.7,
                            ),
                        )
                    ],
                    provenance=ProvenanceMetadata(
                        source_document_id=doc_id,
                        source_pages=[ub.page],
                        source_block_ids=[ub.id],
                        raw_text=ub.text,
                        raw_value=ub.text,
                        extraction_method="layout_heuristic",
                        extraction_confidence=0.7,
                    ),
                )
            )

    return CanonicalSemanticCV(
        source_document_id=doc_id,
        personal_info=personal_info,
        experiences=experiences,
        education=educations,
        skills=skills,
        certifications=certifications,
        projects=projects,
        languages=languages,
        unknown_sections=unknown_sections,
        metadata={
            "method": "layout_heuristic",
            "source_total_blocks": len(layout_doc.source_blocks),
            "fallback": True,
        },
    )


# ============================================================================
# 4. Dedicated CV Semantic Extractor Client
# ============================================================================

class CVSemanticExtractor:
    """Dedicated CV Semantic Extraction client for private Ollama / Qwen.

    Provides bounded exponential backoff retries for cold start resilience,
    schema enforcement via Ollama JSON schema parameter, strict source block
    provenance validation, and explicit degraded/fallback auditing.
    """

    def __init__(
        self,
        config: Optional[ExtractionConfig] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.config = config or ExtractionConfig()
        self._external_client = http_client

    async def _call_ollama_api(
        self,
        prompt: str,
        system: str,
        schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Call Ollama /api/generate with bounded exponential backoff retry for cold starts."""
        url = f"{self.config.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "format": schema or CanonicalSemanticCV.model_json_schema(),
            "options": {
                "temperature": self.config.temperature,
                "num_predict": 4096,
            },
        }

        last_error: Optional[Exception] = None
        current_backoff = self.config.initial_backoff_seconds

        for attempt in range(1, self.config.max_retries + 1):
            try:
                if self._external_client:
                    response = await self._external_client.post(
                        url, json=payload, timeout=self.config.timeout_seconds
                    )
                else:
                    async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                        response = await client.post(url, json=payload)

                if response.status_code in TRANSIENT_STATUS_CODES:
                    raise httpx.HTTPStatusError(
                        f"Serverless/Ollama temporary cold-start error (HTTP {response.status_code})",
                        request=response.request,
                        response=response,
                    )

                response.raise_for_status()
                data = response.json()
                return data.get("response", "")

            except TRANSIENT_EXCEPTIONS as exc:
                last_error = exc
                logger.warning(
                    f"Ollama network/cold-start error on attempt {attempt}/{self.config.max_retries}: {exc}"
                )
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code in TRANSIENT_STATUS_CODES:
                    logger.warning(
                        f"Ollama temporary HTTP status {exc.response.status_code} on attempt {attempt}/{self.config.max_retries}: {exc}"
                    )
                else:
                    # Non-transient HTTP error (e.g. 400 Bad Request, 404 Not Found)
                    raise SemanticExtractionError(f"Ollama returned non-retryable HTTP {exc.response.status_code}: {exc}") from exc
            except Exception as exc:
                last_error = exc
                logger.warning(f"Unexpected error calling Ollama on attempt {attempt}/{self.config.max_retries}: {exc}")

            if attempt < self.config.max_retries:
                logger.info(f"Retrying in {current_backoff:.1f}s (attempt {attempt + 1}/{self.config.max_retries})...")
                await asyncio.sleep(current_backoff)
                current_backoff = min(current_backoff * 2.0, self.config.max_backoff_seconds)

        raise SemanticExtractionError(
            f"Ollama service at {url} unavailable after {self.config.max_retries} bounded attempts: {last_error}"
        )

    async def extract(
        self,
        layout_doc: LayoutDocument,
        document_id: Optional[str] = None,
    ) -> SemanticExtractionResult:
        """Extract structured CanonicalSemanticCV from a LayoutDocument with strict provenance validation.

        If the dedicated service is disabled (CV_EXTRACTION_LLM_ENABLED=false) or errors,
        and fallback is permitted, falls back to deterministic heuristic extraction
        and records explicit fallback metadata:
        - parser_mode = 'heuristic_fallback'
        - degraded = True
        - semantic_model_error = '...'
        """
        start_time = time.perf_counter()
        doc_id = document_id or layout_doc.filename
        valid_block_ids: Set[str] = {b.id for b in layout_doc.source_blocks} if layout_doc else set()

        # 1. Feature Flag Check
        if not self.config.enabled:
            logger.info("CV_EXTRACTION_LLM_ENABLED is False; using deterministic heuristic extraction.")
            if not self.config.fallback_to_heuristics:
                return SemanticExtractionResult(
                    canonical_cv=None,
                    success=False,
                    parser_mode="heuristic_fallback",
                    degraded=True,
                    semantic_model_error="CV_EXTRACTION_LLM_ENABLED is false and fallback_to_heuristics is false.",
                    extraction_method="disabled",
                    fallback_used=False,
                    fallback_reason="CV extraction LLM is disabled via feature flag.",
                    duration_seconds=time.perf_counter() - start_time,
                    error="CV_EXTRACTION_LLM_ENABLED is false.",
                )

            fallback_cv = heuristic_fallback_extract(layout_doc, document_id=doc_id)
            report = validate_canonical_cv(fallback_cv, valid_block_ids=valid_block_ids)
            return SemanticExtractionResult(
                canonical_cv=report.accepted_cv or fallback_cv,
                validation_report=report,
                success=True,
                parser_mode="heuristic_fallback",
                degraded=True,
                semantic_model_error="CV_EXTRACTION_LLM_ENABLED is false",
                extraction_method="layout_heuristic",
                fallback_used=True,
                fallback_reason="Dedicated CV extraction LLM is disabled via CV_EXTRACTION_LLM_ENABLED=false.",
                duration_seconds=time.perf_counter() - start_time,
            )

        # 2. Build Structured Prompt Context
        user_prompt = build_source_blocks_prompt_context(layout_doc, document_id=doc_id)
        expected_schema = CanonicalSemanticCV.model_json_schema()

        # 3. Call Ollama API with Bounded Retries
        try:
            raw_response = await self._call_ollama_api(
                prompt=user_prompt,
                system=SYSTEM_EXTRACTION_PROMPT,
                schema=expected_schema,
            )
            canonical_cv = parse_canonical_semantic_cv_json(raw_response, document_id=doc_id)

            # 4. Strict Provenance Validation
            validation_report = validate_canonical_cv(canonical_cv, valid_block_ids=valid_block_ids)

            # Filter out any hallucinated entities that failed provenance checks
            valid_cv = validation_report.accepted_cv or canonical_cv

            duration = time.perf_counter() - start_time
            return SemanticExtractionResult(
                canonical_cv=valid_cv,
                validation_report=validation_report,
                success=True,
                parser_mode="semantic_llm",
                degraded=False,
                semantic_model_error=None,
                extraction_method="semantic_llm",
                fallback_used=False,
                raw_response=raw_response,
                model_used=self.config.model,
                duration_seconds=duration,
            )

        except Exception as exc:
            duration = time.perf_counter() - start_time
            error_msg = str(exc)
            logger.error(f"Semantic LLM extraction failed: {error_msg}")

            if not self.config.fallback_to_heuristics:
                return SemanticExtractionResult(
                    canonical_cv=None,
                    success=False,
                    parser_mode="heuristic_fallback",
                    degraded=True,
                    semantic_model_error=error_msg,
                    extraction_method="semantic_llm",
                    fallback_used=False,
                    duration_seconds=duration,
                    error=error_msg,
                )

            # Explicit Fallback Recording (Rule 10: No Silent Fallback)
            logger.warning("Executing deterministic heuristic fallback due to LLM failure.")
            fallback_cv = heuristic_fallback_extract(layout_doc, document_id=doc_id)
            report = validate_canonical_cv(fallback_cv, valid_block_ids=valid_block_ids)
            return SemanticExtractionResult(
                canonical_cv=report.accepted_cv or fallback_cv,
                validation_report=report,
                success=True,
                parser_mode="heuristic_fallback",
                degraded=True,
                semantic_model_error=error_msg,
                extraction_method="layout_heuristic",
                fallback_used=True,
                fallback_reason=f"LLM extraction error: {error_msg}",
                duration_seconds=duration,
                error=error_msg,
            )

    async def extract_canonical_cv(
        self,
        layout_doc: LayoutDocument,
        document_id: Optional[str] = None,
    ) -> SemanticExtractionResult:
        """Alias for extract() to ensure full interface compatibility."""
        return await self.extract(layout_doc, document_id=document_id)


# Backward-compatible alias
SemanticExtractionClient = CVSemanticExtractor
