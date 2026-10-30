"""Phase 2 Test Suite — Spatial PDF Document Representation.

Verifies:
1. Coordinate-aware extraction using PyMuPDF (fitz)
2. Hierarchy and typing of SpatialDocument, SpatialPage, SpatialBlock, SpatialLine, SpatialWord, BoundingBox
3. Words in separate columns remain spatially distinguishable
4. Blocks retain valid page coordinates and geometry
5. Reading source does not accidentally merge visually distant content
6. Single-column PDFs extract correctly with vertical reading order
7. Youssof's two-column CV produces distinct left/right spatial regions
8. Typography metadata (font size, style, bold/weight) is accurately captured
9. Reference fallback path via pypdf
10. Resilience under empty, corrupted, and invalid files
11. Raw text preservation without semantic classification
"""

import io
from pathlib import Path
import pytest
import pymupdf

from app.schemas.spatial import (
    BoundingBox,
    SpatialBlock,
    SpatialDocument,
    SpatialLine,
    SpatialPage,
    SpatialWord,
)
from app.services.document_parser import (
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFileFormatError,
)
from app.services.spatial_parser import (
    extract_spatial_document,
)


def create_in_memory_pdf(
    pages_spec: list[dict],
) -> bytes:
    """Helper to generate in-memory PDFs with precise layout positioning for tests."""
    doc = pymupdf.open()
    for spec in pages_spec:
        w = spec.get("width", 612.0)
        h = spec.get("height", 792.0)
        page = doc.new_page(width=w, height=h)
        for item in spec.get("text_items", []):
            pos = pymupdf.Point(item["x"], item["y"])
            font = item.get("font", "helv")
            size = item.get("size", 11.0)
            text = item["text"]
            page.insert_text(pos, text, fontname=font, fontsize=size)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ============================================================================
# 1. BoundingBox Geometry & Math
# ============================================================================

class TestBoundingBoxGeometry:
    """Test 2D bounding box math, centroids, containment, and distance calculations."""

    def test_bounding_box_dimensions_and_centroids(self):
        """BoundingBox must accurately calculate width, height, center_x, and center_y."""
        box = BoundingBox(x0=50.0, y0=100.0, x1=250.0, y1=150.0)
        assert box.width == 200.0
        assert box.height == 50.0
        assert box.center_x == 150.0
        assert box.center_y == 125.0

    def test_bounding_box_overlaps_and_contains(self):
        """Overlapping and containment logic must evaluate correctly."""
        box_a = BoundingBox(x0=0.0, y0=0.0, x1=100.0, y1=100.0)
        box_b = BoundingBox(x0=50.0, y0=50.0, x1=150.0, y1=150.0)
        box_c = BoundingBox(x0=200.0, y0=200.0, x1=300.0, y1=300.0)
        box_inner = BoundingBox(x0=20.0, y0=20.0, x1=80.0, y1=80.0)

        assert box_a.overlaps(box_b) is True
        assert box_a.overlaps(box_c) is False
        assert box_a.contains(box_inner) is True
        assert box_a.contains(box_b) is False

    def test_bounding_box_distances(self):
        """Horizontal and vertical distance calculations between non-overlapping boxes."""
        left = BoundingBox(x0=50.0, y0=100.0, x1=150.0, y1=200.0)
        right = BoundingBox(x0=300.0, y0=100.0, x1=400.0, y1=200.0)
        bottom = BoundingBox(x0=50.0, y0=250.0, x1=150.0, y1=350.0)

        assert left.horizontal_distance_to(right) == 150.0
        assert right.horizontal_distance_to(left) == 150.0
        assert left.vertical_distance_to(right) == 0.0  # Align horizontally
        assert left.vertical_distance_to(bottom) == 50.0


# ============================================================================
# 2. Multi-Column Spatial Distinguishability
# ============================================================================

class TestSpatialColumnDistinguishability:
    """Verify words in separate columns remain spatially distinguishable and do not merge."""

    def test_words_in_separate_columns_remain_spatially_distinguishable(self):
        """Words placed side-by-side in left and right columns must retain distinct coordinates."""
        pdf_bytes = create_in_memory_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 100.0, "text": "Senior Machine Learning Engineer", "size": 12.0},
                    {"x": 380.0, "y": 100.0, "text": "Phone: +961-76-071579", "size": 12.0},
                    {"x": 50.0, "y": 130.0, "text": "Experience at RUYA Advisory", "size": 11.0},
                    {"x": 380.0, "y": 130.0, "text": "Skills: Python, FastAPI", "size": 11.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "two_column_test.pdf")
        assert s_doc.total_pages == 1
        page = s_doc.pages[0]

        words = page.all_words
        words_left = [w for w in words if w.x1 < 300.0]
        words_right = [w for w in words if w.x0 > 350.0]

        assert len(words_left) > 0
        assert len(words_right) > 0
        assert any(w.text == "Senior" for w in words_left)
        assert any(w.text == "+961-76-071579" for w in words_right)

        # Distinguishability invariant: every left word must be strictly left of every right word
        for wl in words_left:
            for wr in words_right:
                assert wl.x1 < wr.x0
                assert wl.bbox.horizontal_distance_to(wr.bbox) > 50.0

    def test_reading_source_does_not_accidentally_merge_visually_distant_content(self):
        """Content separated by a visual gutter must remain in separate SpatialBlocks."""
        pdf_bytes = create_in_memory_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 100.0, "text": "Left Header", "size": 14.0},
                    {"x": 420.0, "y": 100.0, "text": "Right Contact Info", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "distant_blocks.pdf")
        page = s_doc.pages[0]

        # Must produce at least 2 distinct blocks
        assert len(page.blocks) >= 2
        block_left = next(b for b in page.blocks if "Left" in b.raw_text)
        block_right = next(b for b in page.blocks if "Right" in b.raw_text)

        assert block_left.block_id != block_right.block_id
        assert block_left.bbox.horizontal_distance_to(block_right.bbox) >= 200.0
        assert not block_left.bbox.overlaps(block_right.bbox)


# ============================================================================
# 3. Single-Column PDFs & Coordinate Retention
# ============================================================================

class TestSingleColumnSpatialExtraction:
    """Verify single-column documents extract with vertical ordering and valid coordinates."""

    def test_single_column_pdf_extracts_correctly(self):
        """Single-column document must preserve vertical reading order across blocks and lines."""
        pdf_bytes = create_in_memory_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 80.0, "text": "Alex Morgan", "size": 18.0},
                    {"x": 50.0, "y": 120.0, "text": "Professional Summary", "size": 14.0},
                    {"x": 50.0, "y": 150.0, "text": "Experienced Systems Engineer with 8 years track record.", "size": 11.0},
                    {"x": 50.0, "y": 200.0, "text": "Experience", "size": 14.0},
                    {"x": 50.0, "y": 230.0, "text": "QuantumCloud - Lead Platform Engineer", "size": 12.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "single_col.pdf")
        assert s_doc.total_pages == 1
        page = s_doc.pages[0]

        # Verify page coordinates
        assert page.width == 612.0
        assert page.height == 792.0
        assert page.bbox.x0 == 0.0
        assert page.bbox.y0 == 0.0

        # Blocks must be vertically ordered
        blocks = page.blocks
        assert len(blocks) >= 3
        for i in range(len(blocks) - 1):
            assert blocks[i].bbox.y0 <= blocks[i + 1].bbox.y1

        # Check line coordinates
        lines = page.all_lines
        assert len(lines) >= 4
        assert any("Alex Morgan" in l.text for l in lines)
        assert any("QuantumCloud" in l.text for l in lines)


# ============================================================================
# 4. Typography & SpatialWord Attributes
# ============================================================================

class TestSpatialWordTypography:
    """Verify font name, font size, bold weight, and style metadata retention."""

    def test_spatial_word_typography_and_weights(self):
        """Bold headings must have is_bold=True and weight=700 while body text is normal."""
        pdf_bytes = create_in_memory_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 100.0, "text": "BoldTitle", "font": "hebo", "size": 16.0},
                    {"x": 50.0, "y": 140.0, "text": "RegularText", "font": "helv", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "typography.pdf")
        words = s_doc.get_words()

        bold_word = next(w for w in words if w.text == "BoldTitle")
        regular_word = next(w for w in words if w.text == "RegularText")

        assert bold_word.is_bold is True
        assert bold_word.weight == 700
        assert bold_word.font_size == 16.0
        assert bold_word.font_style in ("bold", "bold_italic")

        assert regular_word.is_bold is False
        assert regular_word.weight == 400
        assert regular_word.font_size == 10.0
        assert regular_word.font_style == "normal"


# ============================================================================
# 5. Youssof's Two-Column CV Spatial Regions
# ============================================================================

class TestYoussofTwoColumnCVSpatialRegions:
    """Verify Youssof's two-column CV produces distinct left and right spatial regions."""

    def test_two_column_youssof_synthetic_cv_spatial_regions(self):
        """A two-column CV layout must partition cleanly into left and right spatial regions."""
        pdf_bytes = create_in_memory_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    # Left column header
                    {"x": 50.0, "y": 50.0, "text": "Youssof El Karhani", "font": "hebo", "size": 18.0},
                    {"x": 50.0, "y": 75.0, "text": "AI & Data Engineer", "size": 12.0},
                    # Right column header (Contact)
                    {"x": 380.0, "y": 50.0, "text": "Phone: +961-76-071579", "size": 10.0},
                    {"x": 380.0, "y": 65.0, "text": "Email: youssof.k0@gmail.com", "size": 10.0},
                    {"x": 380.0, "y": 80.0, "text": "https://www.linkedin.com/in/youssof-el-karhani", "size": 10.0},
                    # Left column body (Experience)
                    {"x": 50.0, "y": 140.0, "text": "Experience", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 165.0, "text": "RUYA Advisory - AI & Automation Lead", "size": 11.0},
                    {"x": 50.0, "y": 185.0, "text": "Architected event-driven automation middleware in Python.", "size": 10.0},
                    # Right column body (Skills)
                    {"x": 380.0, "y": 140.0, "text": "Skills", "font": "hebo", "size": 14.0},
                    {"x": 380.0, "y": 165.0, "text": "Python, FastAPI, SQL, MangoDB", "size": 10.0},
                    {"x": 380.0, "y": 185.0, "text": "Reinforcement Learning, TensorFlow", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "youssof_synthetic.pdf")
        page = s_doc.pages[0]

        # Bounding boxes of left items vs right items
        left_blocks = [b for b in page.blocks if b.bbox.center_x < 300.0]
        right_blocks = [b for b in page.blocks if b.bbox.center_x >= 300.0]

        assert len(left_blocks) >= 2
        assert len(right_blocks) >= 2

        left_text = " ".join(b.raw_text for b in left_blocks)
        right_text = " ".join(b.raw_text for b in right_blocks)

        assert "Youssof El Karhani" in left_text
        assert "RUYA Advisory" in left_text
        assert "+961-76-071579" in right_text
        assert "MangoDB" in right_text
        assert "Reinforcement" in right_text

    def test_real_youssof_generated_cv_pdf_if_present(self):
        """Test on actual Youssof generated PDF fixture if present in workspace."""
        generated_dir = (
            Path(__file__).resolve().parents[3]
            / "remotejobs-cli"
            / "data"
            / "CV"
            / "Generated"
        )
        if not generated_dir.exists():
            pytest.skip("remotejobs-cli Generated CV directory not present")

        pdf_files = list(generated_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No generated PDFs found in remotejobs-cli")

        sample_pdf = pdf_files[0]
        pdf_bytes = sample_pdf.read_bytes()

        s_doc = extract_spatial_document(pdf_bytes, sample_pdf.name)
        assert s_doc.total_pages >= 1
        page1 = s_doc.pages[0]

        # Verify page dimensions
        assert page1.width > 500.0
        assert page1.height > 700.0

        # Verify header split: Left name/title vs Right email/phone/address
        mid_x = page1.width / 2.0
        left_blocks = [b for b in page1.blocks if b.bbox.center_x < mid_x]
        right_blocks = [b for b in page1.blocks if b.bbox.center_x >= mid_x]

        assert len(left_blocks) >= 2
        assert len(right_blocks) >= 2

        # Header contact blocks are on the right
        right_text = " ".join(b.raw_text for b in right_blocks)
        assert any(k in right_text.lower() for k in ["email", "phone", "address", "social links"])


# ============================================================================
# 6. Fallback Path via pypdf
# ============================================================================

class TestSpatialPyPDFFallbackPath:
    """Verify the pypdf reference fallback path functions properly."""

    def test_pypdf_fallback_path_produces_valid_spatial_document(self):
        """Calling extract_spatial_document with force_fallback=True must use pypdf and build valid structures."""
        pdf_bytes = create_in_memory_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 80.0, "text": "Candidate Fallback Test", "size": 16.0},
                    {"x": 50.0, "y": 120.0, "text": "Python FastAPI Postgres", "size": 11.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "fallback.pdf", force_fallback=True)
        assert s_doc.extraction_mode == "pypdf_fallback"
        assert s_doc.total_pages == 1
        page = s_doc.pages[0]

        words = page.all_words
        assert len(words) >= 4
        assert any(w.text == "Candidate" for w in words)
        assert any(w.text == "Python" for w in words)

        for w in words:
            assert w.x0 < w.x1
            assert w.y0 < w.y1
            assert w.page == 1


# ============================================================================
# 7. Robust Error Handling & Boundaries
# ============================================================================

class TestSpatialParserErrorHandling:
    """Verify empty files, corrupt data, and unsupported extensions raise standard exceptions."""

    def test_empty_zero_bytes_raises_empty_document_error(self):
        """0-byte file raises EmptyDocumentError."""
        with pytest.raises(EmptyDocumentError):
            extract_spatial_document(b"", "resume.pdf")

    def test_corrupted_pdf_bytes_raises_parsing_error(self):
        """Corrupt PDF stream raises DocumentParsingError."""
        corrupt_bytes = b"%PDF-1.5 corrupt binary content \xff\xfe\x00\x01\x02"
        with pytest.raises(DocumentParsingError):
            extract_spatial_document(corrupt_bytes, "corrupt.pdf")

    def test_unsupported_file_extension_raises_unsupported_error(self):
        """Non-PDF extension raises UnsupportedFileFormatError."""
        with pytest.raises(UnsupportedFileFormatError):
            extract_spatial_document(b"%PDF-1.4 mock", "resume.docx")

    def test_raw_content_is_never_discarded(self):
        """raw_text must be preserved on SpatialDocument, SpatialPage, and SpatialBlock."""
        pdf_bytes = create_in_memory_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 100.0, "text": "Raw Text Content Must Be Preserved", "size": 12.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "raw_preserve.pdf")
        assert "Raw Text Content Must Be Preserved" in s_doc.raw_text
        assert "Raw Text Content Must Be Preserved" in s_doc.pages[0].raw_text
        assert "Raw Text Content Must Be Preserved" in s_doc.pages[0].blocks[0].raw_text
