"""Test Suite for Phase 8 — Document Routing and OCR Fallback.

Verifies:
1. Magic byte and extension sniffing for PDFs, DOCX, Plain Text, and Unknown binary files.
2. PDF text density and embedded raster image inspection.
3. Native PDF routing directly to Phase 2 spatial extraction without triggering OCR.
4. Plain text and DOCX routing with coordinate-compatible SpatialDocument wrapping.
5. Scanned PDF detection and explicit OCR requirement (Rule 10: Zero Silent Fallback).
6. Scanned PDF extraction via MockOCREngine producing valid bounding boxes, blocks, lines, and words.
7. Downstream integration: OCR SpatialDocument -> Phase 3 Layout -> Phase 6 Fallback -> Phase 7 Normalization.
8. Robust error handling for empty files, unknown formats, and missing OCR engines.
"""

import io
from pathlib import Path
import pytest

from app.schemas.spatial import BoundingBox, SpatialDocument
from app.services.document_parser import (
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFileFormatError,
)
from app.services.document_router import (
    DocumentRoutingResult,
    DocumentType,
    detect_file_extension,
    inspect_pdf_text_density,
    route_and_parse_document,
    sniff_document_type,
)
from app.services.layout import reconstruct_reading_order
from app.services.normalization import normalize_canonical_cv
from app.services.ocr_service import (
    MockOCREngine,
    OCRExtractionError,
    extract_spatial_document_with_ocr,
    is_ocr_available,
)
from app.services.semantic_extraction_client import heuristic_fallback_extract

# Reference files & test helper
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "test_data"
SAMPLE_PDF = FIXTURES_DIR / "sample_cv.pdf"
YOUSSOF_CV = FIXTURES_DIR / "youssof_cv.pdf"


def make_in_memory_native_pdf(text: str = "John Doe\nSoftware Engineer\nPython FastAPI PostgreSQL Docker Kubernetes") -> bytes:
    import pymupdf
    doc = pymupdf.open()
    page = doc.new_page(width=612.0, height=792.0)
    for i, line in enumerate(text.split("\n")):
        page.insert_text(pymupdf.Point(50.0, 50.0 + (i * 20.0)), line, fontsize=12.0)
    data = doc.tobytes()
    doc.close()
    return data


# ============================================================================
# 1. Extension Detection & Magic Byte Sniffing Tests
# ============================================================================

def test_detect_file_extension():
    assert detect_file_extension("resume.pdf") == "pdf"
    assert detect_file_extension("RESUME.DOCX") == "docx"
    assert detect_file_extension("path/to/my.cv.txt") == "txt"
    assert detect_file_extension("no_extension") == ""
    assert detect_file_extension("") == ""


def test_sniff_document_type_pdf():
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    assert sniff_document_type(pdf_bytes, "cv.pdf") == DocumentType.NATIVE_PDF
    # Without extension, PDF magic bytes still identify as PDF
    assert sniff_document_type(pdf_bytes, "unknown_file") == DocumentType.NATIVE_PDF


def test_sniff_document_type_docx():
    # DOCX is a ZIP container containing [Content_Types].xml or word/document.xml
    docx_bytes = b"PK\x03\x04\x14\x00\x00\x00\x08\x00word/document.xml" + b"\x00" * 50
    assert sniff_document_type(docx_bytes, "resume.docx") == DocumentType.DOCX
    assert sniff_document_type(docx_bytes, "no_ext") == DocumentType.DOCX


def test_sniff_document_type_plain_text():
    text_bytes = b"John Doe\nSoftware Engineer\nEmail: john@example.com\n"
    assert sniff_document_type(text_bytes, "resume.txt") == DocumentType.PLAIN_TEXT
    assert sniff_document_type(text_bytes, "README.md") == DocumentType.PLAIN_TEXT


def test_sniff_document_type_unknown():
    random_binary = b"\x00\x01\x02\x03\x04\x05\x06\x07\x89PNG\r\n\x1a\n"
    assert sniff_document_type(random_binary, "image.png") == DocumentType.UNKNOWN
    assert sniff_document_type(b"", "empty.txt") == DocumentType.UNKNOWN


# ============================================================================
# 2. PDF Density & Scanned Detection Tests
# ============================================================================

def test_inspect_pdf_text_density_native_pdf():
    if YOUSSOF_CV.exists():
        pdf_bytes = YOUSSOF_CV.read_bytes()
    elif SAMPLE_PDF.exists():
        pdf_bytes = SAMPLE_PDF.read_bytes()
    else:
        pdf_bytes = make_in_memory_native_pdf()

    is_scanned, word_count, total_pages, images_per_page = inspect_pdf_text_density(pdf_bytes)
    assert not is_scanned
    assert word_count >= 5
    assert total_pages >= 1


def test_inspect_pdf_text_density_scanned_stub():
    # Synthetic PDF with zero text words and embedded dummy image structure
    scanned_stub = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /XObject << /Im1 4 0 R >> >> >> endobj\n"
        b"4 0 obj <</Type /XObject /Subtype /Image /Width 100 /Height 100 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Length 0>> stream\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer <</Size 5 /Root 1 0 R>>\nstartxref\n300\n%%EOF"
    )
    is_scanned, word_count, total_pages, images = inspect_pdf_text_density(scanned_stub)
    assert is_scanned
    assert word_count == 0
    assert total_pages == 1


# ============================================================================
# 3. Document Routing Tests
# ============================================================================

def test_route_native_pdf():
    if YOUSSOF_CV.exists():
        pdf_bytes = YOUSSOF_CV.read_bytes()
    else:
        pdf_bytes = make_in_memory_native_pdf("Alice Engineer\nPython FastAPI\nEducation BSc Computer Science")

    res = route_and_parse_document(pdf_bytes, filename="resume.pdf", enable_ocr=False)

    assert isinstance(res, DocumentRoutingResult)
    assert res.document_type == DocumentType.NATIVE_PDF
    assert res.is_scanned is False
    assert res.needs_ocr is False
    assert res.ocr_used is False
    assert res.native_word_count > 5
    assert res.spatial_document is not None
    assert len(res.spatial_document.pages) >= 1
    assert res.routing_reason == "high_density_vector_text_extracted"


def test_route_plain_text():
    text_content = "Jane Doe\nSenior Backend Engineer\nPython, Docker, FastAPI"
    raw_bytes = text_content.encode("utf-8")

    res = route_and_parse_document(raw_bytes, filename="resume.txt")
    assert res.document_type == DocumentType.PLAIN_TEXT
    assert res.is_scanned is False
    assert res.needs_ocr is False
    assert res.spatial_document is not None
    assert res.spatial_document.extraction_mode == "plain_text_spatial"
    assert "Jane Doe" in res.spatial_document.raw_text
    assert len(res.spatial_document.pages[0].blocks) == 3


def test_route_empty_document_raises():
    with pytest.raises(EmptyDocumentError):
        route_and_parse_document(b"", filename="empty.pdf")


def test_route_unsupported_format_raises():
    with pytest.raises(UnsupportedFileFormatError):
        route_and_parse_document(b"\x89PNG\r\n\x1a\n", filename="avatar.png")


def test_route_scanned_pdf_ocr_disabled():
    scanned_stub = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>> endobj\n"
        b"trailer <</Size 4 /Root 1 0 R>>\n%%EOF"
    )
    res = route_and_parse_document(scanned_stub, filename="scanned.pdf", enable_ocr=False)
    assert res.document_type == DocumentType.SCANNED_PDF
    assert res.is_scanned is True
    assert res.needs_ocr is True
    assert res.ocr_used is False
    assert res.spatial_document is None
    assert "OCR engine is unavailable or disabled" in (res.error or "")


# ============================================================================
# 4. OCR Service & MockOCREngine Tests
# ============================================================================

def test_is_ocr_available_safe_call():
    # Must return a boolean without crashing even if Tesseract is not installed
    avail = is_ocr_available()
    assert isinstance(avail, bool)


def test_mock_ocr_engine_spatial_document():
    mock_engine = MockOCREngine(
        mock_pages_words=[
            [
                {"text": "Alice", "bbox": (50.0, 50.0, 90.0, 65.0), "line_idx": 0},
                {"text": "Smith", "bbox": (95.0, 50.0, 140.0, 65.0), "line_idx": 0},
                {"text": "TECHNICAL", "bbox": (50.0, 90.0, 120.0, 105.0), "line_idx": 1, "is_bold": True},
                {"text": "SKILLS", "bbox": (125.0, 90.0, 175.0, 105.0), "line_idx": 1, "is_bold": True},
                {"text": "Python,", "bbox": (50.0, 120.0, 100.0, 135.0), "line_idx": 2},
                {"text": "FastAPI,", "bbox": (105.0, 120.0, 155.0, 135.0), "line_idx": 2},
                {"text": "MangoDB", "bbox": (160.0, 120.0, 220.0, 135.0), "line_idx": 2},
            ]
        ]
    )

    dummy_scanned_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>> endobj\n"
        b"trailer <</Size 4 /Root 1 0 R>>\n%%EOF"
    )

    res = route_and_parse_document(
        dummy_scanned_pdf,
        filename="scanned_resume.pdf",
        enable_ocr=True,
        ocr_service=mock_engine,
    )

    assert res.document_type == DocumentType.SCANNED_PDF
    assert res.is_scanned is True
    assert res.needs_ocr is True
    assert res.ocr_used is True
    assert res.ocr_engine == "MockOCREngine"
    assert res.spatial_document is not None

    sp_doc = res.spatial_document
    assert len(sp_doc.pages) == 1
    assert sp_doc.extraction_mode == "mock_ocr_spatial"

    page = sp_doc.pages[0]
    assert len(page.blocks) == 1
    block = page.blocks[0]
    assert len(block.lines) == 3
    assert "Alice Smith" in block.raw_text
    assert "MangoDB" in block.raw_text


def test_ocr_service_missing_tesseract_raises_cleanly():
    # When no mock is provided and Tesseract is unavailable, extract_spatial_document_with_ocr
    # must raise OCRExtractionError cleanly with descriptive guidance
    if not is_ocr_available():
        with pytest.raises(OCRExtractionError) as exc_info:
            extract_spatial_document_with_ocr(b"%PDF-stub", filename="test.pdf")
        assert "Tesseract OCR engine is not installed" in str(exc_info.value)


# ============================================================================
# 5. Full Pipeline Integration: OCR -> Layout -> Semantic -> Normalization
# ============================================================================

def test_full_pipeline_flow_from_ocr_to_normalized_cv():
    """Verify that an OCR-derived SpatialDocument flows seamlessly through all phases."""
    mock_engine = MockOCREngine(
        mock_pages_words=[
            [
                {"text": "John", "bbox": (50.0, 50.0, 80.0, 65.0), "line_idx": 0},
                {"text": "Doe", "bbox": (85.0, 50.0, 115.0, 65.0), "line_idx": 0},
                {"text": "john.doe@example.com", "bbox": (50.0, 70.0, 180.0, 82.0), "line_idx": 1},
                {"text": "EXPERIENCE", "bbox": (50.0, 100.0, 130.0, 115.0), "line_idx": 2, "is_bold": True},
                {"text": "Sr.", "bbox": (50.0, 125.0, 70.0, 138.0), "line_idx": 3},
                {"text": "Software", "bbox": (75.0, 125.0, 130.0, 138.0), "line_idx": 3},
                {"text": "Engineer", "bbox": (135.0, 125.0, 190.0, 138.0), "line_idx": 3},
                {"text": "Acme", "bbox": (195.0, 125.0, 230.0, 138.0), "line_idx": 3},
                {"text": "Corp", "bbox": (235.0, 125.0, 270.0, 138.0), "line_idx": 3},
                {"text": "SKILLS", "bbox": (50.0, 160.0, 100.0, 175.0), "line_idx": 4, "is_bold": True},
                {"text": "Python,", "bbox": (50.0, 185.0, 95.0, 198.0), "line_idx": 5},
                {"text": "MangoDB", "bbox": (100.0, 185.0, 160.0, 198.0), "line_idx": 5},
            ]
        ]
    )

    dummy_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>> endobj\n"
        b"trailer <</Size 4 /Root 1 0 R>>\n%%EOF"
    )

    # 1. Route and OCR parse
    route_res = route_and_parse_document(
        dummy_pdf,
        filename="scanned_resume.pdf",
        enable_ocr=True,
        ocr_service=mock_engine,
    )
    assert route_res.ocr_used is True
    spatial_doc = route_res.spatial_document
    assert spatial_doc is not None

    # 2. Phase 3 Layout reading order
    layout_doc = reconstruct_reading_order(spatial_doc)
    assert len(layout_doc.source_blocks) >= 1

    # 3. Phase 6 Semantic fallback extraction
    raw_cv = heuristic_fallback_extract(layout_doc)
    assert raw_cv.personal_info is not None
    assert raw_cv.personal_info.full_name.raw_value == "John Doe"
    # Ensure source block IDs exist and match layout blocks
    valid_ids = {b.id for b in layout_doc.source_blocks}
    for bid in raw_cv.personal_info.provenance.source_block_ids:
        assert bid in valid_ids

    # 4. Phase 7 Normalization & Confidence scoring
    normalized_res = normalize_canonical_cv(raw_cv)
    assert normalized_res.cv is not None
    assert normalized_res.quality_score.overall_score > 0.0

    # Verify MangoDB was normalized to MongoDB
    skills = [s.normalized_value for s in normalized_res.cv.skills if s.normalized_value]
    assert "MongoDB" in skills
    # Raw value remains preserved
    raw_skills = [s.raw_value for s in normalized_res.cv.skills]
    assert any("MangoDB" in rs for rs in raw_skills)
