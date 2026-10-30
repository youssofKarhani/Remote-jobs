"""Test Suite for Phase 3 — Column Detection, Block Reconstruction, and Reading Order.

Verifies:
1. Single-column reading order and block reconstruction.
2. Two-column reading order (ensuring left region is never interleaved with right region).
3. Left sidebar + main body layout detection.
4. Top header band isolation across multi-column body.
5. Multi-line heading merging into single SourceBlocks.
6. Wrapped paragraph content preservation.
7. Stable source block identifiers (BLOCK_001, BLOCK_002, ...) and strict provenance.
8. Real Youssof generated CV layout reconstruction regression test.
"""

from pathlib import Path
import re
import pytest
import pymupdf

from app.schemas.spatial import BoundingBox, SpatialDocument
from app.schemas.layout import ColumnLayout, LayoutDocument, SourceBlock
from app.services.spatial_parser import extract_spatial_document
from app.services.layout.column_detector import detect_page_columns
from app.services.layout.heading_detector import detect_heading_candidates
from app.services.layout.block_builder import build_source_blocks
from app.services.layout.reading_order import reconstruct_reading_order
from app.services.document_parser import reconstruct_layout_pdf


def _create_test_pdf(pages_spec: list[dict]) -> bytes:
    """Helper to build an in-memory PDF from a declarative list of pages and text items."""
    doc = pymupdf.open()
    for p_spec in pages_spec:
        w = p_spec.get("width", 612.0)
        h = p_spec.get("height", 792.0)
        page = doc.new_page(width=w, height=h)
        for item in p_spec.get("text_items", []):
            pt = pymupdf.Point(item["x"], item["y"])
            font = item.get("font", "helv")
            size = item.get("size", 10.0)
            page.insert_text(pt, item["text"], fontsize=size, fontname=font)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ============================================================================
# 1. Single-Column CV Layout & Reading Order
# ============================================================================

class TestSingleColumnLayoutAndReadingOrder:
    """Verify single-column documents are correctly classified and ordered top-to-bottom."""

    def test_single_column_flow_and_headings(self):
        """Single-column CV should be classified as single_column and blocks ordered top-to-bottom."""
        pdf_bytes = _create_test_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 50.0, "text": "Jane Doe", "font": "hebo", "size": 18.0},
                    {"x": 50.0, "y": 75.0, "text": "Senior Machine Learning Engineer", "size": 11.0},
                    {"x": 50.0, "y": 140.0, "text": "Experience", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 165.0, "text": "AI Labs — Senior Engineer (2022 - Present)", "font": "hebo", "size": 11.0},
                    {"x": 65.0, "y": 185.0, "text": "• Architected distributed fine-tuning pipeline.", "size": 10.0},
                    {"x": 65.0, "y": 205.0, "text": "• Reduced inference latency by 45%.", "size": 10.0},
                    {"x": 50.0, "y": 260.0, "text": "Education", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 285.0, "text": "B.S. in Computer Science — Stanford University", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "single_col.pdf")
        layout_doc = reconstruct_reading_order(s_doc)

        assert layout_doc.total_pages == 1
        page_layout = layout_doc.layouts_by_page[1]
        assert page_layout.layout_type == "single_column"
        assert page_layout.num_columns == 1

        blocks = layout_doc.source_blocks
        assert len(blocks) >= 5

        # Check reading order sequence is strictly ascending
        reading_orders = [b.reading_order for b in blocks]
        assert reading_orders == list(range(1, len(blocks) + 1))

        # Check headings are detected
        headings = layout_doc.get_headings()
        heading_texts = [h.text for h in headings]
        assert "Experience" in heading_texts
        assert "Education" in heading_texts

        # Verify Experience precedes Education in reading order
        exp_block = next(b for b in blocks if b.text == "Experience")
        edu_block = next(b for b in blocks if b.text == "Education")
        assert exp_block.reading_order < edu_block.reading_order


# ============================================================================
# 2. Two-Column CV Reading Order & No Interleaving
# ============================================================================

class TestTwoColumnReadingOrder:
    """Verify two-column CV layouts resolve left region completely before right region.

    Expected Result per Master Spec:
    LEFT REGION: Contact, Languages, Technical Skills
    RIGHT REGION: Education, Certifications, Projects
    rather than reading horizontally across both columns.
    """

    def test_two_column_youssof_synthetic_reading_order_no_interleaving(self):
        """Technical skills must NEVER interleave with Education, Certifications, or Projects."""
        pdf_bytes = _create_test_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    # Left column (x: 50..220)
                    {"x": 50.0, "y": 60.0, "text": "Contact Info", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 85.0, "text": "Email: youssof@example.com", "size": 10.0},
                    {"x": 50.0, "y": 105.0, "text": "Phone: +961-76-071579", "size": 10.0},

                    {"x": 50.0, "y": 160.0, "text": "Languages", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 185.0, "text": "English: Fluent (C1)", "size": 10.0},
                    {"x": 50.0, "y": 205.0, "text": "Arabic: Native", "size": 10.0},

                    {"x": 50.0, "y": 260.0, "text": "Technical Skills", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 285.0, "text": "Python, FastAPI, Docker, SQL", "size": 10.0},
                    {"x": 50.0, "y": 305.0, "text": "PyTorch, Machine Learning, Ollama", "size": 10.0},

                    # Right column (x: 270..550)
                    {"x": 270.0, "y": 60.0, "text": "Education", "font": "hebo", "size": 14.0},
                    {"x": 270.0, "y": 85.0, "text": "B.S. in Computer Science", "size": 11.0},
                    {"x": 270.0, "y": 105.0, "text": "Lebanese American University", "size": 10.0},

                    {"x": 270.0, "y": 160.0, "text": "Certifications", "font": "hebo", "size": 14.0},
                    {"x": 270.0, "y": 185.0, "text": "AWS Certified Solutions Architect", "size": 10.0},
                    {"x": 270.0, "y": 205.0, "text": "TensorFlow Developer Certificate", "size": 10.0},

                    {"x": 270.0, "y": 260.0, "text": "Projects", "font": "hebo", "size": 14.0},
                    {"x": 270.0, "y": 285.0, "text": "Sentimental Chatbot Engine", "size": 10.0},
                    {"x": 270.0, "y": 305.0, "text": "Automated Agent Orchestrator", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "youssof_twocol.pdf")
        layout_doc = reconstruct_reading_order(s_doc)

        assert layout_doc.total_pages == 1
        page_layout = layout_doc.layouts_by_page[1]
        assert page_layout.layout_type in ("two_column", "left_sidebar")
        assert page_layout.num_columns == 2
        assert len(page_layout.gutters) == 1

        blocks = layout_doc.source_blocks
        assert len(blocks) >= 10

        # Extract reading order indices for key sections
        contact_idx = next(b.reading_order for b in blocks if "Contact" in b.text)
        lang_idx = next(b.reading_order for b in blocks if "Languages" in b.text)
        skills_idx = next(b.reading_order for b in blocks if "Technical Skills" in b.text)
        edu_idx = next(b.reading_order for b in blocks if "Education" in b.text)
        cert_idx = next(b.reading_order for b in blocks if "Certifications" in b.text)
        proj_idx = next(b.reading_order for b in blocks if "Projects" in b.text)

        # 1. Left column must be ordered internally: Contact -> Languages -> Technical Skills
        assert contact_idx < lang_idx < skills_idx

        # 2. Right column must be ordered internally: Education -> Certifications -> Projects
        assert edu_idx < cert_idx < proj_idx

        # 3. CRITICAL INVARIANT: The entire Left column must precede the entire Right column!
        # Technical skills (bottom of left column) must be read BEFORE Education (top of right column)
        assert skills_idx < edu_idx, (
            f"Interleaving detected! Technical Skills (order {skills_idx}) must precede "
            f"Education (order {edu_idx}) in a two-column CV reading order."
        )

        # 4. Check no right-column block is interleaved inside the left column
        left_blocks = [b for b in blocks if b.column == 0 and b.region_type not in ("header", "footer")]
        right_blocks = [b for b in blocks if b.column == 1 and b.region_type not in ("header", "footer")]

        max_left_order = max(b.reading_order for b in left_blocks)
        min_right_order = min(b.reading_order for b in right_blocks)
        assert max_left_order < min_right_order


# ============================================================================
# 3. Left Sidebar + Main Body Layout
# ============================================================================

class TestLeftSidebarLayout:
    """Verify asymmetric sidebar layouts (sidebar <= 38% width) are detected and ordered properly."""

    def test_left_sidebar_and_main_body_partitioning(self):
        """Asymmetric layout with left sidebar should sequence sidebar first, then main body."""
        pdf_bytes = _create_test_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    # Left sidebar (narrow: x=40..170)
                    {"x": 40.0, "y": 60.0, "text": "Contact", "font": "hebo", "size": 13.0},
                    {"x": 40.0, "y": 80.0, "text": "Email: user@example.com", "size": 9.0},
                    {"x": 40.0, "y": 95.0, "text": "Location: Berlin, Germany", "size": 9.0},
                    {"x": 40.0, "y": 140.0, "text": "Skills", "font": "hebo", "size": 13.0},
                    {"x": 40.0, "y": 160.0, "text": "Python, SQL, FastApi, Docker", "size": 9.0},

                    # Main body (wide: x=210..570)
                    {"x": 210.0, "y": 60.0, "text": "Professional Experience", "font": "hebo", "size": 14.0},
                    {"x": 210.0, "y": 85.0, "text": "Senior Software Architect — Cloud Native Systems", "size": 11.0},
                    {"x": 210.0, "y": 105.0, "text": "Led the end-to-end modernization of enterprise data infrastructure.", "size": 10.0},
                    {"x": 210.0, "y": 125.0, "text": "Implemented distributed caching reducing database load by 60 percent.", "size": 10.0},
                    {"x": 210.0, "y": 160.0, "text": "Education", "font": "hebo", "size": 14.0},
                    {"x": 210.0, "y": 185.0, "text": "Master of Science in Distributed Computing", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "sidebar.pdf")
        layout_doc = reconstruct_reading_order(s_doc)

        page_layout = layout_doc.layouts_by_page[1]
        assert page_layout.num_columns == 2
        assert len(page_layout.gutters) == 1

        blocks = layout_doc.source_blocks
        skills_block = next(b for b in blocks if "Skills" in b.text)
        exp_block = next(b for b in blocks if "Professional Experience" in b.text)

        # Sidebar content comes before main body
        assert skills_block.reading_order < exp_block.reading_order


# ============================================================================
# 4. Header Band Detection
# ============================================================================

class TestHeaderBandDetection:
    """Verify full-width top header bands are isolated from two-column bodies."""

    def test_top_header_band_across_two_columns(self):
        """Header spanning across the page top must be assigned region_type='header' and read first."""
        pdf_bytes = _create_test_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    # Wide header
                    {"x": 100.0, "y": 40.0, "text": "Alex Morgan — Principal AI Architect", "font": "hebo", "size": 18.0},
                    {"x": 150.0, "y": 65.0, "text": "Email: alex@example.com • Phone: +1-555-0199", "size": 10.0},

                    # Column 0 below header
                    {"x": 50.0, "y": 150.0, "text": "Technical Skills", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 175.0, "text": "Python, PyTorch, Kubernetes", "size": 10.0},

                    # Column 1 below header
                    {"x": 270.0, "y": 150.0, "text": "Experience", "font": "hebo", "size": 14.0},
                    {"x": 270.0, "y": 175.0, "text": "Principal Architect at NeuralCorp", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "header_cols.pdf")
        layout_doc = reconstruct_reading_order(s_doc)

        page_layout = layout_doc.layouts_by_page[1]
        assert page_layout.has_header_band is True
        assert page_layout.header_boundary_y is not None
        assert 65.0 < page_layout.header_boundary_y < 150.0

        header_blocks = layout_doc.get_blocks_by_region("header")
        assert len(header_blocks) >= 1
        assert "Alex Morgan" in header_blocks[0].text
        assert header_blocks[0].reading_order == 1


# ============================================================================
# 5. Multi-line Headings & Wrapped Paragraphs
# ============================================================================

class TestMultiLineHeadingsAndWrappedContent:
    """Verify headings spanning multiple lines and wrapped body paragraphs."""

    def test_multiline_heading_merging(self):
        """Headings spanning consecutive tight lines must merge into a single SourceBlock."""
        pdf_bytes = _create_test_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    # Multi-line heading
                    {"x": 50.0, "y": 60.0, "text": "Courses &", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 75.0, "text": "Certifications", "font": "hebo", "size": 14.0},
                    # Content below
                    {"x": 50.0, "y": 105.0, "text": "AWS Solutions Architect Professional", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "multiline_heading.pdf")
        layout_doc = reconstruct_reading_order(s_doc)

        headings = layout_doc.get_headings()
        assert len(headings) >= 1
        primary_heading = headings[0]

        # The combined heading should contain both words
        assert "Courses" in primary_heading.text
        assert "Certifications" in primary_heading.text
        # Both line IDs should be tracked for provenance
        assert len(primary_heading.source_line_ids) == 2

    def test_wrapped_paragraph_block_clustering(self):
        """Multi-line body paragraph within a column must form a cohesive SourceBlock."""
        pdf_bytes = _create_test_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 60.0, "text": "Summary", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 90.0, "text": "Seasoned software engineer with 8+ years experience designing", "size": 10.0},
                    {"x": 50.0, "y": 105.0, "text": "high-throughput distributed microservices in Python and Rust.", "size": 10.0},
                    {"x": 50.0, "y": 120.0, "text": "Proven track record delivering mission critical enterprise platforms.", "size": 10.0},
                ],
            }
        ])

        s_doc = extract_spatial_document(pdf_bytes, "wrapped_paragraph.pdf")
        layout_doc = reconstruct_reading_order(s_doc)

        blocks = layout_doc.source_blocks
        summary_heading = next(b for b in blocks if b.is_heading)
        summary_body = next(b for b in blocks if not b.is_heading and "Seasoned" in b.text)

        assert "8+ years" in summary_body.text
        assert "Rust." in summary_body.text
        assert "enterprise platforms." in summary_body.text
        assert len(summary_body.source_line_ids) == 3


# ============================================================================
# 6. Stable SourceBlock Identifiers & Strict Provenance
# ============================================================================

class TestStableSourceBlockProvenance:
    """Verify source blocks have persistent IDs (BLOCK_xxx) and full spatial provenance."""

    def test_source_block_identifiers_and_provenance_integrity(self):
        """Every SourceBlock must retain stable ID, valid BoundingBox, and line/word references."""
        pdf_bytes = _create_test_pdf([
            {
                "width": 612.0,
                "height": 792.0,
                "text_items": [
                    {"x": 50.0, "y": 50.0, "text": "Youssof El Karhani", "font": "hebo", "size": 18.0},
                    {"x": 50.0, "y": 100.0, "text": "Experience", "font": "hebo", "size": 14.0},
                    {"x": 50.0, "y": 125.0, "text": "Lead Engineer at RUYA Advisory", "size": 11.0},
                ],
            }
        ])

        layout_doc = reconstruct_layout_pdf(pdf_bytes, "provenance_test.pdf")
        blocks = layout_doc.source_blocks

        block_id_regex = re.compile(r"^BLOCK_\d{3}$")
        seen_ids = set()

        for b in blocks:
            # 1. ID format
            assert block_id_regex.match(b.id), f"Invalid block ID format: {b.id}"
            assert b.id not in seen_ids, f"Duplicate block ID: {b.id}"
            seen_ids.add(b.id)

            # 2. Coordinates
            assert isinstance(b.bbox, BoundingBox)
            assert b.bbox.width > 0
            assert b.bbox.height > 0
            assert b.bbox.x0 >= 0
            assert b.bbox.y0 >= 0

            # 3. Provenance
            assert b.page == 1
            assert len(b.source_line_ids) > 0
            assert len(b.source_word_ids) > 0
            assert len(b.text.strip()) > 0
            assert len(b.raw_text.strip()) > 0

            # 4. Lookup integrity
            lookup_block = layout_doc.find_block_by_id(b.id)
            assert lookup_block is not None
            assert lookup_block.id == b.id


# ============================================================================
# 7. Real Youssof Generated CV Layout Reconstruction Regression
# ============================================================================

class TestRealYoussofCVLayoutReconstruction:
    """Verify real generated Youssof CVs parse cleanly through the layout pipeline."""

    def test_real_youssof_generated_cv_layout_reconstruction(self):
        """Real Youssof CV from remotejobs-cli must produce structured layout blocks."""
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
        layout_doc = reconstruct_layout_pdf(sample_pdf.read_bytes(), sample_pdf.name)

        assert layout_doc.total_pages >= 1
        assert len(layout_doc.source_blocks) >= 10

        # Check that reading order indices are strictly sequential 1..N
        orders = [b.reading_order for b in layout_doc.source_blocks]
        assert orders == list(range(1, len(layout_doc.source_blocks) + 1))

        # Check reading order text is non-empty
        assert len(layout_doc.reading_order_text) > 100
        assert "Youssof El Karhani" in layout_doc.reading_order_text

        # Verify headings are extracted
        headings = layout_doc.get_headings()
        heading_texts = [h.text for h in headings]
        assert any("Experience" in h for h in heading_texts)
