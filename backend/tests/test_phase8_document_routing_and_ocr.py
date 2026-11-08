"""Test Suite for Phase 8 — Document Routing and OCR Fallback.

Verifies:
1. Magic byte and extension sniffing for PDFs, DOCX, Plain Text, Images, and Unknown binary files.
2. Native text quality detection rules:
   - character count
   - printable-character ratio
   - number of text blocks
   - text coverage across pages
   - suspicious encoding (CIDs, control characters, replacement chars)
   - pages containing images but almost no text
3. OCR Trigger rules:
   - OCR used ONLY when text is absent, quality is poor, or pages are image-only.
   - Good native-text pages are never OCR'd unnecessarily.
4. Fixtures for all 6 document types:
   - 1. Native PDF (PDF_NATIVE_TEXT)
   - 2. Scanned PDF (PDF_SCANNED)
   - 3. Hybrid PDF (PDF_HYBRID)
   - 4. Structured DOCX (DOCX)
   - 5. Image CV (IMAGE)
   - 6. Poor-Encoding PDF (triggers OCR fallback)
5. OCR Provenance preservation:
   - OCR page number
   - OCR text
   - OCR confidence where available
   - coordinates where available
   - extraction_method = OCR
6. Hybrid PDF handling:
   - Native on good pages, OCR on scanned pages, merged with no duplicated content.
7. Structured DOCX parsing:
   - Headings, bold runs, and table cells preserved without plain text degradation.
8. Full downstream pipeline integration:
   - OCR SpatialDocument -> Phase 3 Layout -> Phase 6 Semantic Fallback -> Phase 7 Normalization.
"""

import io
from pathlib import Path
import pytest

import docx
import pymupdf

from app.schemas.spatial import BoundingBox, SpatialDocument
from app.services.document_parser import (
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFileFormatError,
)
from app.services.document_router import (
    DocumentQualityAssessment,
    DocumentRoutingResult,
    DocumentType,
    PageQualityMetrics,
    assess_page_text_quality,
    detect_file_extension,
    inspect_pdf_text_density,
    inspect_pdf_text_quality,
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

# Reference files
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "test_data"
SAMPLE_PDF = FIXTURES_DIR / "sample_cv.pdf"
YOUSSOF_CV = FIXTURES_DIR / "youssof_cv.pdf"


# ============================================================================
# Fixture Generators for All 6 Document Types
# ============================================================================

def make_in_memory_native_pdf(
    text: str = (
        "Alice Smith\n"
        "Senior Backend Engineer\n"
        "Python FastAPI PostgreSQL Docker Kubernetes\n"
        "Experience: Senior Developer at TechCorp 2020-2024\n"
        "Education: BSc Computer Science 2016-2020"
    ),
) -> bytes:
    """Fixture 1: High-density vector text PDF."""
    doc = pymupdf.open()
    page = doc.new_page(width=612.0, height=792.0)
    for i, line in enumerate(text.split("\n")):
        page.insert_text(pymupdf.Point(50.0, 50.0 + (i * 20.0)), line, fontsize=12.0)
    data = doc.tobytes()
    doc.close()
    return data


def make_in_memory_scanned_pdf() -> bytes:
    """Fixture 2: Scanned/rasterized PDF with embedded image and zero extractable text."""
    doc = pymupdf.open()
    page = doc.new_page(width=612.0, height=792.0)
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 100, 100), 0)
    pix.clear_with(255)
    page.insert_image(pymupdf.Rect(50.0, 50.0, 400.0, 400.0), pixmap=pix)
    data = doc.tobytes()
    doc.close()
    return data


def make_in_memory_hybrid_pdf() -> bytes:
    """Fixture 3: Hybrid PDF (Page 1 native vector text, Page 2 scanned image)."""
    doc = pymupdf.open()
    # Page 1: Native vector text
    p1 = doc.new_page(width=612.0, height=792.0)
    p1.insert_text(
        pymupdf.Point(50.0, 50.0),
        "Bob Builder\nPrincipal Cloud Architect\nKubernetes Terraform AWS Python\nAcme Systems 2018-2024",
        fontsize=12.0,
    )
    # Page 2: Raster scan image only
    p2 = doc.new_page(width=612.0, height=792.0)
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 100, 100), 0)
    pix.clear_with(200)
    p2.insert_image(pymupdf.Rect(50.0, 50.0, 400.0, 400.0), pixmap=pix)
    data = doc.tobytes()
    doc.close()
    return data


def make_in_memory_docx() -> bytes:
    """Fixture 4: Structured DOCX with headings, bold styling runs, and table cells."""
    doc = docx.Document()
    doc.add_heading("Jane Doe", level=0)
    doc.add_paragraph("Senior Python Engineer with 8 years of experience building distributed systems.")
    p_skills = doc.add_paragraph()
    run = p_skills.add_run("TECHNICAL SKILLS")
    run.bold = True
    table = doc.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "Role"
    table.rows[0].cells[1].text = "Tech Stack"
    table.rows[1].cells[0].text = "Backend Lead"
    table.rows[1].cells[1].text = "Python, FastAPI, Postgres"
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def make_in_memory_image_cv() -> bytes:
    """Fixture 5: Standalone Image CV (PNG byte stream)."""
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 200, 200), 0)
    pix.clear_with(255)
    return pix.tobytes("png")


def make_in_memory_poor_encoding_pdf() -> bytes:
    """Fixture 6: PDF with corrupted encoding / unmapped glyphs triggering OCR fallback."""
    doc = pymupdf.open()
    page = doc.new_page(width=612.0, height=792.0)
    corrupted_text = "Corrupted\n" + "".join(chr(c) for c in range(1, 15)) + "Header\n"
    page.insert_text(pymupdf.Point(50.0, 50.0), corrupted_text, fontsize=12.0)
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
    assert detect_file_extension("scan.PNG") == "png"
    assert detect_file_extension("photo.jpeg") == "jpeg"
    assert detect_file_extension("no_extension") == ""
    assert detect_file_extension("") == ""


def test_sniff_document_type_pdf():
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    assert sniff_document_type(pdf_bytes, "cv.pdf") == DocumentType.PDF_NATIVE_TEXT
    assert sniff_document_type(pdf_bytes, "unknown_file") == DocumentType.PDF_NATIVE_TEXT


def test_sniff_document_type_docx():
    docx_bytes = b"PK\x03\x04\x14\x00\x00\x00\x08\x00word/document.xml" + b"\x00" * 50
    assert sniff_document_type(docx_bytes, "resume.docx") == DocumentType.DOCX
    assert sniff_document_type(docx_bytes, "no_ext") == DocumentType.DOCX


def test_sniff_document_type_plain_text():
    text_bytes = b"John Doe\nSoftware Engineer\nEmail: john@example.com\n"
    assert sniff_document_type(text_bytes, "resume.txt") == DocumentType.TEXT
    assert sniff_document_type(text_bytes, "README.md") == DocumentType.TEXT


def test_sniff_document_type_image():
    png_magic = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    assert sniff_document_type(png_magic, "scan.png") == DocumentType.IMAGE

    jpg_magic = b"\xff\xd8\xff\xe0" + b"\x00" * 20
    assert sniff_document_type(jpg_magic, "photo.jpg") == DocumentType.IMAGE

    tiff_magic = b"II*\x00" + b"\x00" * 20
    assert sniff_document_type(tiff_magic, "document.tiff") == DocumentType.IMAGE


def test_sniff_document_type_unknown():
    random_binary = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a"
    assert sniff_document_type(random_binary, "audio.bin") == DocumentType.UNKNOWN
    assert sniff_document_type(b"", "empty.txt") == DocumentType.UNKNOWN


# ============================================================================
# 2. Native Text Quality Detection Rules Tests
# ============================================================================

def test_assess_page_text_quality_good_native():
    good_text = "John Doe\nSoftware Engineer\n5 years Python FastAPI experience"
    metrics = assess_page_text_quality(
        page_text=good_text,
        words_count=10,
        blocks_count=3,
        images_count=0,
        page_num=1,
    )
    assert metrics.quality_grade == "good"
    assert metrics.needs_ocr is False
    assert metrics.printable_ratio >= 0.95
    assert metrics.suspicious_encoding is False
    assert metrics.is_image_only is False


def test_assess_page_text_quality_suspicious_encoding():
    corrupted_text = "Header\n" + "".join(chr(i) for i in range(1, 15)) + "Text\n"
    metrics = assess_page_text_quality(
        page_text=corrupted_text,
        words_count=2,
        blocks_count=1,
        images_count=0,
        page_num=1,
    )
    assert metrics.suspicious_encoding is True
    assert metrics.quality_grade == "poor"
    assert metrics.needs_ocr is True
    assert "suspicious_encoding" in metrics.reason


def test_assess_page_text_quality_image_only():
    metrics = assess_page_text_quality(
        page_text="",
        words_count=0,
        blocks_count=0,
        images_count=1,
        page_num=1,
    )
    assert metrics.is_image_only is True
    assert metrics.needs_ocr is True
    assert metrics.quality_grade == "image_only"


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
    scanned_pdf = make_in_memory_scanned_pdf()
    is_scanned, word_count, total_pages, images = inspect_pdf_text_density(scanned_pdf)
    assert is_scanned
    assert word_count == 0
    assert total_pages == 1


# ============================================================================
# 3. All 6 Document Fixture Routing Tests
# ============================================================================

def test_fixture_1_native_pdf():
    """Fixture 1: High quality vector PDF -> PDF_NATIVE_TEXT without OCR."""
    pdf_bytes = make_in_memory_native_pdf()
    res = route_and_parse_document(pdf_bytes, filename="native_cv.pdf", enable_ocr=False)

    assert res.document_type == DocumentType.PDF_NATIVE_TEXT
    assert res.is_scanned is False
    assert res.needs_ocr is False
    assert res.ocr_used is False
    assert res.native_word_count > 10
    assert res.spatial_document is not None
    assert len(res.spatial_document.pages) == 1
    assert res.spatial_document.metadata.get("extraction_method") == "native"
    assert res.routing_reason == "high_density_vector_text_extracted"


def test_fixture_2_scanned_pdf():
    """Fixture 2: Scanned PDF -> PDF_SCANNED requiring OCR."""
    pdf_bytes = make_in_memory_scanned_pdf()
    mock_ocr = MockOCREngine(
        mock_pages_words=[
            [
                {"text": "Alice", "bbox": (50.0, 50.0, 90.0, 65.0), "confidence": 0.98},
                {"text": "Smith", "bbox": (95.0, 50.0, 140.0, 65.0), "confidence": 0.98},
                {"text": "Python", "bbox": (50.0, 80.0, 100.0, 95.0), "confidence": 0.95},
            ]
        ]
    )

    res = route_and_parse_document(
        pdf_bytes,
        filename="scanned_cv.pdf",
        enable_ocr=True,
        ocr_service=mock_ocr,
    )

    assert res.document_type == DocumentType.PDF_SCANNED
    assert res.is_scanned is True
    assert res.needs_ocr is True
    assert res.ocr_used is True
    assert res.spatial_document is not None

    sp_doc = res.spatial_document
    assert sp_doc.metadata.get("extraction_method") == "OCR"
    assert sp_doc.metadata.get("ocr_engine") == "MockOCREngine"
    assert len(sp_doc.pages) == 1

    page = sp_doc.pages[0]
    assert page.extraction_method == "OCR"
    assert page.blocks[0].extraction_method == "OCR"
    # Word confidence preserved
    assert page.blocks[0].lines[0].words[0].confidence == 0.98


def test_fixture_3_hybrid_pdf():
    """Fixture 3: Hybrid PDF -> PDF_HYBRID with native Page 1 and OCR Page 2, no duplication."""
    pdf_bytes = make_in_memory_hybrid_pdf()

    qa = inspect_pdf_text_quality(pdf_bytes)
    assert qa.classification == DocumentType.PDF_HYBRID
    assert qa.is_hybrid is True
    assert qa.pages_native_good == [1]
    assert qa.pages_needing_ocr == [2]

    mock_ocr = MockOCREngine(
        mock_pages_words=[
            [],  # Page 1 (skipped by OCR)
            [
                {"text": "Certifications:", "bbox": (50.0, 50.0, 150.0, 65.0), "confidence": 0.96},
                {"text": "AWS-Solutions-Architect", "bbox": (50.0, 80.0, 220.0, 95.0), "confidence": 0.94},
            ],
        ]
    )

    res = route_and_parse_document(
        pdf_bytes,
        filename="hybrid_cv.pdf",
        enable_ocr=True,
        ocr_service=mock_ocr,
    )

    assert res.document_type == DocumentType.PDF_HYBRID
    assert res.is_scanned is True
    assert res.needs_ocr is True
    assert res.ocr_used is True
    assert res.spatial_document is not None

    sp_doc = res.spatial_document
    assert sp_doc.extraction_mode == "pdf_hybrid_spatial"
    assert sp_doc.total_pages == 2
    assert len(sp_doc.pages) == 2

    # Verify Page 1 preserved native extraction
    p1 = sp_doc.pages[0]
    assert p1.page_number == 1
    assert p1.extraction_method == "native"
    assert "Bob Builder" in p1.raw_text

    # Verify Page 2 used OCR
    p2 = sp_doc.pages[1]
    assert p2.page_number == 2
    assert p2.extraction_method == "OCR"
    assert "AWS-Solutions-Architect" in p2.raw_text

    # Verify no content duplication between pages
    assert "Bob Builder" not in p2.raw_text
    assert "AWS-Solutions-Architect" not in p1.raw_text


def test_fixture_4_structured_docx():
    """Fixture 4: Structured DOCX preserving headings, bold runs, and table cells."""
    docx_bytes = make_in_memory_docx()
    res = route_and_parse_document(docx_bytes, filename="resume.docx", enable_ocr=False)

    assert res.document_type == DocumentType.DOCX
    assert res.is_scanned is False
    assert res.needs_ocr is False
    assert res.ocr_used is False
    assert res.spatial_document is not None

    sp_doc = res.spatial_document
    assert sp_doc.extraction_mode == "docx_structured_spatial"
    assert len(sp_doc.pages) == 1

    page = sp_doc.pages[0]
    raw_text = page.raw_text
    assert "Jane Doe" in raw_text
    assert "TECHNICAL SKILLS" in raw_text
    # Table cell contents preserved
    assert "Backend Lead" in raw_text
    assert "Python, FastAPI, Postgres" in raw_text

    # Verify bold flag preservation on heading / bold runs
    bold_words = [w for w in page.all_words if w.is_bold]
    assert any("TECHNICAL" in w.text for w in bold_words)


def test_fixture_5_image_cv():
    """Fixture 5: Standalone image CV routed through OCR into SpatialDocument."""
    img_bytes = make_in_memory_image_cv()
    mock_ocr = MockOCREngine(
        mock_pages_words=[
            [
                {"text": "Charlie", "bbox": (50.0, 50.0, 110.0, 65.0), "confidence": 0.99},
                {"text": "DevOps", "bbox": (50.0, 80.0, 100.0, 95.0), "confidence": 0.95},
                {"text": "Engineer", "bbox": (105.0, 80.0, 160.0, 95.0), "confidence": 0.95},
            ]
        ]
    )

    res = route_and_parse_document(
        img_bytes,
        filename="scanned_resume.png",
        enable_ocr=True,
        ocr_service=mock_ocr,
    )

    assert res.document_type == DocumentType.IMAGE
    assert res.is_scanned is True
    assert res.needs_ocr is True
    assert res.ocr_used is True
    assert res.spatial_document is not None

    sp_doc = res.spatial_document
    assert sp_doc.extraction_mode == "image_ocr_spatial"
    assert "Charlie" in sp_doc.raw_text
    assert "DevOps Engineer" in sp_doc.raw_text
    assert sp_doc.pages[0].extraction_method == "OCR"


def test_fixture_6_poor_encoding_pdf():
    """Fixture 6: Poor encoding PDF classified as poor quality, triggering OCR fallback."""
    poor_pdf = make_in_memory_poor_encoding_pdf()
    qa = inspect_pdf_text_quality(poor_pdf)

    assert qa.pages_metrics[0].suspicious_encoding is True
    assert qa.pages_metrics[0].quality_grade == "poor"
    assert qa.needs_ocr is True
    assert qa.classification == DocumentType.PDF_SCANNED

    mock_ocr = MockOCREngine(
        mock_pages_words=[
            [
                {"text": "Recovered", "bbox": (50.0, 50.0, 120.0, 65.0)},
                {"text": "Profile", "bbox": (125.0, 50.0, 170.0, 65.0)},
            ]
        ]
    )

    res = route_and_parse_document(
        poor_pdf,
        filename="poor_encoding.pdf",
        enable_ocr=True,
        ocr_service=mock_ocr,
    )
    assert res.document_type == DocumentType.PDF_SCANNED
    assert res.ocr_used is True
    assert "Recovered Profile" in res.spatial_document.raw_text


# ============================================================================
# 4. OCR Provenance & Bounding Box Preservation Tests
# ============================================================================

def test_ocr_provenance_preservation():
    """Verify OCR page numbers, confidence, coordinates, and extraction_method are preserved."""
    mock_ocr = MockOCREngine(
        mock_pages_words=[
            [
                {"text": "David", "bbox": (60.0, 40.0, 110.0, 55.0), "confidence": 0.97},
                {"text": "Golan", "bbox": (115.0, 40.0, 160.0, 55.0), "confidence": 0.96},
            ]
        ]
    )

    sp_doc = extract_spatial_document_with_ocr(
        b"%PDF-stub",
        filename="david_cv.pdf",
        ocr_service=mock_ocr,
    )

    assert sp_doc.metadata.get("extraction_method") == "OCR"
    assert sp_doc.total_pages == 1

    page = sp_doc.pages[0]
    assert page.page_number == 1
    assert page.extraction_method == "OCR"

    block = page.blocks[0]
    assert block.page == 1
    assert block.extraction_method == "OCR"
    assert block.bbox.x0 == 60.0
    assert block.bbox.y0 == 40.0

    word0 = block.lines[0].words[0]
    assert word0.text == "David"
    assert word0.page == 1
    assert word0.confidence == 0.97
    assert word0.x0 == 60.0
    assert word0.y0 == 40.0


# ============================================================================
# 5. Error Handling & Zero Silent Fallback Tests
# ============================================================================

def test_route_plain_text():
    text_content = "Jane Doe\nSenior Backend Engineer\nPython, Docker, FastAPI"
    raw_bytes = text_content.encode("utf-8")

    res = route_and_parse_document(raw_bytes, filename="resume.txt")
    assert res.document_type == DocumentType.TEXT
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
        route_and_parse_document(b"ID3\x03\x00\x00\x00\x00\x00\x00", filename="audio.mp3")


def test_route_scanned_pdf_ocr_disabled():
    scanned_pdf = make_in_memory_scanned_pdf()
    res = route_and_parse_document(scanned_pdf, filename="scanned.pdf", enable_ocr=False)
    assert res.document_type == DocumentType.PDF_SCANNED
    assert res.is_scanned is True
    assert res.needs_ocr is True
    assert res.ocr_used is False
    assert res.spatial_document is None
    assert "OCR engine is unavailable or disabled" in (res.error or "")


def test_is_ocr_available_safe_call():
    avail = is_ocr_available()
    assert isinstance(avail, bool)


def test_ocr_service_missing_tesseract_raises_cleanly():
    if not is_ocr_available():
        with pytest.raises(OCRExtractionError) as exc_info:
            extract_spatial_document_with_ocr(b"%PDF-stub", filename="test.pdf")
        assert "Tesseract OCR engine is not installed" in str(exc_info.value)


# ============================================================================
# 6. Full Pipeline Integration: OCR -> Layout -> Semantic -> Normalization
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

    scanned_pdf = make_in_memory_scanned_pdf()

    # 1. Route and OCR parse
    route_res = route_and_parse_document(
        scanned_pdf,
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
