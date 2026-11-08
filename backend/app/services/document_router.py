"""Document Type Detection, Native Text Quality Assessment, and OCR Routing Engine (Phase 8).

Inspects file headers, extensions, and content densities to classify documents into:
- PDF_NATIVE_TEXT: Vector font PDFs with high quality extractable text.
- PDF_SCANNED: Rasterized/image-only PDFs requiring OCR across all pages.
- PDF_HYBRID: Multi-page PDFs containing native text on some pages and scanned images elsewhere.
- DOCX: Microsoft Word OpenXML documents parsed preserving document structure (headings, tables, runs).
- IMAGE: Standalone image CVs (PNG, JPEG, TIFF, WEBP) routed through OCR.
- TEXT: Plain text and markdown documents directly mapped to spatial coordinates.

Enforces extraction quality rules and selective OCR triggering (Rule 10: No Silent Fallback).
"""

from dataclasses import dataclass, field
from enum import Enum
import io
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import docx
import pypdf
from pypdf import PdfReader

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

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
from app.services.spatial_parser import extract_spatial_document


class DocumentType(str, Enum):
    PDF_NATIVE_TEXT = "pdf_native_text"
    PDF_SCANNED = "pdf_scanned"
    PDF_HYBRID = "pdf_hybrid"
    DOCX = "docx"
    IMAGE = "image"
    TEXT = "text"
    UNKNOWN = "unknown"

    # Backward compatibility aliases
    NATIVE_PDF = "pdf_native_text"
    SCANNED_PDF = "pdf_scanned"
    PLAIN_TEXT = "text"


@dataclass
class PageQualityMetrics:
    """Extraction quality signals for a single document page."""
    page_number: int
    character_count: int
    word_count: int
    printable_ratio: float
    block_count: int
    image_count: int
    suspicious_encoding: bool
    is_image_only: bool
    quality_grade: str  # "good", "poor", "image_only"
    needs_ocr: bool
    reason: str = ""


@dataclass
class DocumentQualityAssessment:
    """Document-wide text quality assessment across all pages."""
    total_pages: int
    pages_metrics: List[PageQualityMetrics]
    classification: DocumentType
    needs_ocr: bool
    pages_needing_ocr: List[int] = field(default_factory=list)
    pages_native_good: List[int] = field(default_factory=list)
    is_hybrid: bool = False
    average_printable_ratio: float = 1.0
    text_coverage_across_pages: float = 1.0


@dataclass
class DocumentRoutingResult:
    """Outcome of document classification and extraction routing."""
    document_type: DocumentType
    is_scanned: bool = False
    native_word_count: int = 0
    total_pages: int = 1
    needs_ocr: bool = False
    ocr_used: bool = False
    ocr_engine: Optional[str] = None
    spatial_document: Optional[SpatialDocument] = None
    routing_reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


def detect_file_extension(filename: str) -> str:
    """Extract lowercase file extension without leading dot."""
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower().strip()
    return ""


def sniff_document_type(file_bytes: bytes, filename: str = "") -> DocumentType:
    """Sniff document format from binary magic bytes and file extension."""
    if not file_bytes:
        return DocumentType.UNKNOWN

    ext = detect_file_extension(filename)

    # 1. PDF Magic Header (%PDF)
    if file_bytes.startswith(b"%PDF"):
        return DocumentType.PDF_NATIVE_TEXT  # Refined by text density assessment

    # 2. DOCX / ZIP Magic Header (PK\x03\x04)
    if file_bytes.startswith(b"PK\x03\x04"):
        if ext in ("docx", "docm") or b"word/document.xml" in file_bytes[:4096]:
            return DocumentType.DOCX

    # 3. Image Magic Bytes & Extensions
    if (
        file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        or file_bytes.startswith(b"\xff\xd8\xff")  # JPEG
        or file_bytes.startswith(b"II*\x00")  # TIFF little-endian
        or file_bytes.startswith(b"MM\x00*")  # TIFF big-endian
        or file_bytes.startswith(b"RIFF") and b"WEBP" in file_bytes[:16]
        or ext in ("png", "jpg", "jpeg", "tiff", "tif", "webp", "bmp")
    ):
        return DocumentType.IMAGE

    # 4. Plain Text / Markdown
    if ext in ("txt", "text", "md", "markdown"):
        return DocumentType.TEXT

    # Heuristic for text if file_bytes are decodeable ASCII/UTF-8
    try:
        sample = file_bytes[:1024].decode("utf-8")
        if all(c.isprintable() or c.isspace() for c in sample) and len(sample) > 20:
            return DocumentType.TEXT
    except (UnicodeDecodeError, AttributeError):
        pass

    return DocumentType.UNKNOWN


# ============================================================================
# 1. Native Text Quality Detection Rules
# ============================================================================

def assess_page_text_quality(
    page_text: str,
    words_count: int,
    blocks_count: int,
    images_count: int,
    page_num: int,
) -> PageQualityMetrics:
    """Evaluate native extraction quality signals for a single page.

    Signals:
    - extracted character count
    - printable-character ratio
    - number of text blocks
    - suspicious encoding (e.g. unmapped CID fonts or replacement chars)
    - pages containing images but almost no text
    """
    char_count = len(page_text)
    clean_chars = sum(1 for c in page_text if c.isprintable() or c.isspace())
    printable_ratio = (clean_chars / max(1, char_count)) if char_count > 0 else 1.0

    # Suspicious encoding: low printable ratio, unmapped CIDs, replacement chars (\ufffd), or PUA glyphs
    replacement_count = page_text.count("\ufffd")
    cid_count = page_text.count("(cid:")
    pua_chars = sum(1 for c in page_text if 0xE000 <= ord(c) <= 0xF8FF)
    consecutive_replacements = len(re.findall(r"[·•\ufffd]{3,}", page_text))

    suspicious_encoding = (
        (char_count > 10 and printable_ratio < 0.85)
        or (replacement_count > 2)
        or (cid_count >= 2)
        or (pua_chars > 2)
        or (consecutive_replacements > 0)
    )

    # Image-only detection: page has images and negligible extractable text
    is_image_only = (words_count < 10 or char_count < 50) and (images_count > 0)

    if suspicious_encoding:
        grade = "poor"
        needs_ocr = True
        reason = "suspicious_encoding_or_unprintable_glyphs"
    elif is_image_only:
        grade = "image_only"
        needs_ocr = True
        reason = "embedded_images_with_negligible_text"
    elif words_count == 0:
        grade = "image_only" if images_count > 0 else "poor"
        needs_ocr = True
        reason = "zero_extractable_text"
    elif words_count < 20 and images_count > 0:
        grade = "poor"
        needs_ocr = True
        reason = "low_text_density_with_embedded_images"
    else:
        grade = "good"
        needs_ocr = False
        reason = "sufficient_native_vector_text"

    return PageQualityMetrics(
        page_number=page_num,
        character_count=char_count,
        word_count=words_count,
        printable_ratio=round(printable_ratio, 2),
        block_count=blocks_count,
        image_count=images_count,
        suspicious_encoding=suspicious_encoding,
        is_image_only=is_image_only,
        quality_grade=grade,
        needs_ocr=needs_ocr,
        reason=reason,
    )


def inspect_pdf_text_quality(file_bytes: bytes) -> DocumentQualityAssessment:
    """Inspect all pages in a PDF and return a comprehensive quality assessment."""
    if not file_bytes.startswith(b"%PDF"):
        return DocumentQualityAssessment(
            total_pages=0,
            pages_metrics=[],
            classification=DocumentType.UNKNOWN,
            needs_ocr=False,
        )

    metrics_list: List[PageQualityMetrics] = []

    # 1. Prefer PyMuPDF for fine-grained per-page analysis
    if pymupdf is not None:
        try:
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)
            for page_idx, page in enumerate(doc):
                text = page.get_text() or ""
                words = page.get_text("words") or []
                blocks = page.get_text("blocks") or []
                images = page.get_images() or []

                m = assess_page_text_quality(
                    page_text=text,
                    words_count=len(words),
                    blocks_count=len(blocks),
                    images_count=len(images),
                    page_num=page_idx + 1,
                )
                metrics_list.append(m)
            doc.close()
        except Exception:
            pass

    # 2. PyPDF fallback if PyMuPDF fails or is unavailable
    if not metrics_list:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                words = text.split()
                images = getattr(page, "images", [])
                m = assess_page_text_quality(
                    page_text=text,
                    words_count=len(words),
                    blocks_count=len(text.split("\n\n")),
                    images_count=len(images),
                    page_num=page_idx + 1,
                )
                metrics_list.append(m)
        except Exception:
            pass

    if not metrics_list:
        return DocumentQualityAssessment(
            total_pages=1,
            pages_metrics=[],
            classification=DocumentType.PDF_SCANNED,
            needs_ocr=True,
            pages_needing_ocr=[1],
        )

    pages_ocr = [m.page_number for m in metrics_list if m.needs_ocr]
    pages_good = [m.page_number for m in metrics_list if not m.needs_ocr]
    total_pages = len(metrics_list)

    if len(pages_ocr) == 0:
        classification = DocumentType.PDF_NATIVE_TEXT
        is_hybrid = False
        needs_ocr = False
    elif len(pages_good) == 0:
        classification = DocumentType.PDF_SCANNED
        is_hybrid = False
        needs_ocr = True
    else:
        classification = DocumentType.PDF_HYBRID
        is_hybrid = True
        needs_ocr = True

    avg_printable = (
        round(sum(m.printable_ratio for m in metrics_list) / len(metrics_list), 2)
        if metrics_list else 1.0
    )
    coverage = round(len(pages_good) / max(1, total_pages), 2)

    return DocumentQualityAssessment(
        total_pages=total_pages,
        pages_metrics=metrics_list,
        classification=classification,
        needs_ocr=needs_ocr,
        pages_needing_ocr=pages_ocr,
        pages_native_good=pages_good,
        is_hybrid=is_hybrid,
        average_printable_ratio=avg_printable,
        text_coverage_across_pages=coverage,
    )


def inspect_pdf_text_density(file_bytes: bytes) -> Tuple[bool, int, int, List[int]]:
    """Legacy helper maintained for backward compatibility.

    Returns:
        (is_scanned, total_words, total_pages, images_per_page)
    """
    qa = inspect_pdf_text_quality(file_bytes)
    total_words = sum(m.word_count for m in qa.pages_metrics)
    total_pages = qa.total_pages
    images = [m.image_count for m in qa.pages_metrics]
    is_scanned = qa.classification in (DocumentType.PDF_SCANNED, DocumentType.PDF_HYBRID)
    return is_scanned, total_words, total_pages, images


# ============================================================================
# 2. Structured DOCX Spatial Extractor (Preserving Structure)
# ============================================================================

def extract_spatial_document_from_docx(file_bytes: bytes, filename: str = "document.docx") -> SpatialDocument:
    """Extract DOCX content preserving native structure (paragraphs, headings, bold runs, tables).

    Does NOT flatten into degraded plain text before parsing.
    """
    doc = docx.Document(io.BytesIO(file_bytes))

    # Standard virtual page geometry: 612 x 792 pt (Letter) with 54pt margins
    page_w = 612.0
    page_h = 792.0
    margin_x = 54.0
    margin_top = 54.0
    content_w = page_w - (2 * margin_x)

    spatial_blocks: List[SpatialBlock] = []
    current_y = margin_top
    block_counter = 0
    all_raw_lines: List[str] = []

    # 1. Process Paragraphs
    for p_idx, p in enumerate(doc.paragraphs):
        p_text = p.text.strip()
        if not p_text:
            current_y += 12.0
            continue

        all_raw_lines.append(p_text)
        is_heading = (
            p.style.name.startswith("Heading")
            or p_text.isupper()
            or any(run.bold for run in p.runs if len(run.text.strip()) > 3)
        )
        font_size = 14.0 if is_heading else 10.5

        # Build words from runs to preserve bold styling
        sp_words: List[SpatialWord] = []
        word_offset_x = margin_x

        for run in p.runs:
            run_words = run.text.split()
            run_bold = bool(run.bold)
            for w in run_words:
                w_len = len(w) * (font_size * 0.55)
                sw = SpatialWord(
                    word_id=f"docx_p1_b{block_counter}_w{len(sp_words)}",
                    line_id=f"docx_p1_b{block_counter}_l0",
                    block_id=f"docx_p1_b{block_counter}",
                    page=1,
                    text=w,
                    x0=round(word_offset_x, 2),
                    y0=round(current_y, 2),
                    x1=round(word_offset_x + w_len, 2),
                    y1=round(current_y + font_size + 2.0, 2),
                    font_name=run.font.name or "Calibri",
                    font_size=font_size,
                    is_bold=run_bold or is_heading,
                )
                sp_words.append(sw)
                word_offset_x += w_len + 5.0

        if not sp_words:
            continue

        line_bbox = BoundingBox(
            x0=margin_x,
            y0=current_y,
            x1=min(page_w - margin_x, word_offset_x),
            y1=current_y + font_size + 2.0,
        )
        sp_line = SpatialLine(
            line_id=f"docx_p1_b{block_counter}_l0",
            block_id=f"docx_p1_b{block_counter}",
            page=1,
            bbox=line_bbox,
            text=p_text,
            words=sp_words,
            font_size=font_size,
            is_bold=is_heading,
        )
        sp_block = SpatialBlock(
            block_id=f"docx_p1_b{block_counter}",
            page=1,
            bbox=line_bbox,
            raw_text=p_text,
            lines=[sp_line],
        )
        spatial_blocks.append(sp_block)
        block_counter += 1
        current_y += font_size + 8.0

    # 2. Process Tables (Preserve grid cell structure)
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if not row_texts:
                continue

            row_line_str = " | ".join(row_texts)
            all_raw_lines.append(row_line_str)
            col_w = content_w / max(1, len(row.cells))

            table_words: List[SpatialWord] = []
            for c_idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()
                if not cell_text:
                    continue
                cell_x0 = margin_x + (c_idx * col_w)
                for w_idx, w in enumerate(cell_text.split()):
                    sw = SpatialWord(
                        word_id=f"docx_tbl{t_idx}_r{r_idx}_c{c_idx}_w{w_idx}",
                        line_id=f"docx_p1_b{block_counter}_l0",
                        block_id=f"docx_p1_b{block_counter}",
                        page=1,
                        text=w,
                        x0=round(cell_x0 + (w_idx * 30.0), 2),
                        y0=round(current_y, 2),
                        x1=round(cell_x0 + ((w_idx + 1) * 30.0), 2),
                        y1=round(current_y + 12.0, 2),
                        font_size=10.0,
                    )
                    table_words.append(sw)

            if table_words:
                tbl_bbox = BoundingBox(x0=margin_x, y0=current_y, x1=margin_x + content_w, y1=current_y + 14.0)
                sp_line = SpatialLine(
                    line_id=f"docx_p1_b{block_counter}_l0",
                    block_id=f"docx_p1_b{block_counter}",
                    page=1,
                    bbox=tbl_bbox,
                    text=row_line_str,
                    words=table_words,
                    font_size=10.0,
                )
                sp_block = SpatialBlock(
                    block_id=f"docx_p1_b{block_counter}",
                    page=1,
                    bbox=tbl_bbox,
                    raw_text=row_line_str,
                    lines=[sp_line],
                )
                spatial_blocks.append(sp_block)
                block_counter += 1
                current_y += 18.0

    raw_doc_text = "\n".join(all_raw_lines)
    actual_height = max(page_h, current_y + margin_top)
    sp_page = SpatialPage(
        page_number=1,
        width=page_w,
        height=actual_height,
        bbox=BoundingBox(x0=0.0, y0=0.0, x1=page_w, y1=actual_height),
        blocks=spatial_blocks,
        raw_text=raw_doc_text,
    )
    return SpatialDocument(
        filename=filename,
        total_pages=1,
        pages=[sp_page],
        raw_text=raw_doc_text,
        extraction_mode="docx_structured_spatial",
        metadata={"paragraphs_count": len(doc.paragraphs), "tables_count": len(doc.tables)},
    )


# ============================================================================
# 3. Main Document Router Engine
# ============================================================================

def route_and_parse_document(
    file_bytes: bytes,
    filename: str = "document.pdf",
    enable_ocr: bool = True,
    ocr_service: Optional[Any] = None,
) -> DocumentRoutingResult:
    """Route document to native spatial, structured DOCX, image OCR, or hybrid pipeline."""
    if not file_bytes:
        raise EmptyDocumentError("The uploaded file is empty (0 bytes).")

    initial_type = sniff_document_type(file_bytes, filename=filename)

    if initial_type == DocumentType.UNKNOWN:
        ext = detect_file_extension(filename)
        raise UnsupportedFileFormatError(f"Unsupported file format '.{ext}' for CV ingestion.")

    # ------------------------------------------------------------------------
    # 1. Plain Text Path
    # ------------------------------------------------------------------------
    if initial_type == DocumentType.TEXT:
        text_content = file_bytes.decode("utf-8", errors="replace")
        raw_lines = [l for l in text_content.splitlines() if l.strip()]
        sp_blocks: List[SpatialBlock] = []
        all_words_count = 0
        current_y = 50.0

        for b_idx, line_str in enumerate(raw_lines):
            line_words = line_str.split()
            all_words_count += len(line_words)
            sp_words = [
                SpatialWord(
                    word_id=f"p1_b{b_idx}_l0_w{w_idx}",
                    line_id=f"p1_b{b_idx}_l0",
                    block_id=f"p1_b{b_idx}",
                    page=1,
                    text=w,
                    x0=50.0 + (w_idx * 10.0),
                    y0=current_y,
                    x1=58.0 + (w_idx * 10.0),
                    y1=current_y + 12.0,
                    font_size=12.0 if line_str.isupper() else 10.0,
                    is_bold=line_str.isupper(),
                )
                for w_idx, w in enumerate(line_words)
            ]
            sp_line = SpatialLine(
                line_id=f"p1_b{b_idx}_l0",
                block_id=f"p1_b{b_idx}",
                page=1,
                bbox=BoundingBox(x0=50.0, y0=current_y, x1=500.0, y1=current_y + 12.0),
                text=line_str,
                words=sp_words,
                font_size=12.0 if line_str.isupper() else 10.0,
                is_bold=line_str.isupper(),
            )
            sp_block = SpatialBlock(
                block_id=f"p1_b{b_idx}",
                page=1,
                bbox=BoundingBox(x0=50.0, y0=current_y, x1=500.0, y1=current_y + 12.0),
                raw_text=line_str,
                lines=[sp_line],
            )
            sp_blocks.append(sp_block)
            current_y += 20.0

        sp_page = SpatialPage(
            page_number=1,
            width=612.0,
            height=max(792.0, current_y + 50.0),
            bbox=BoundingBox(x0=0.0, y0=0.0, x1=612.0, y1=max(792.0, current_y + 50.0)),
            blocks=sp_blocks,
            raw_text=text_content,
        )
        spatial_doc = SpatialDocument(
            filename=filename,
            total_pages=1,
            pages=[sp_page],
            raw_text=text_content,
            extraction_mode="plain_text_spatial",
        )
        return DocumentRoutingResult(
            document_type=DocumentType.TEXT,
            is_scanned=False,
            native_word_count=all_words_count,
            total_pages=1,
            needs_ocr=False,
            spatial_document=spatial_doc,
            routing_reason="plain_text_direct_spatial_mapping",
        )

    # ------------------------------------------------------------------------
    # 2. DOCX Path (Structured OpenXML Extraction)
    # ------------------------------------------------------------------------
    if initial_type == DocumentType.DOCX:
        spatial_doc = extract_spatial_document_from_docx(file_bytes, filename=filename)
        word_count = len(spatial_doc.raw_text.split())
        return DocumentRoutingResult(
            document_type=DocumentType.DOCX,
            is_scanned=False,
            native_word_count=word_count,
            total_pages=1,
            needs_ocr=False,
            spatial_document=spatial_doc,
            routing_reason="docx_openxml_structured_extracted",
            metadata=spatial_doc.metadata,
        )

    # ------------------------------------------------------------------------
    # 3. Image CV Path (PNG, JPEG, TIFF, WEBP)
    # ------------------------------------------------------------------------
    if initial_type == DocumentType.IMAGE:
        from app.services.ocr_service import (
            OCRExtractionError,
            extract_spatial_document_with_ocr,
            is_ocr_available,
        )

        ext = detect_file_extension(filename) or "png"
        ocr_available = is_ocr_available() if ocr_service is None else True

        if enable_ocr and (ocr_available or ocr_service is not None):
            try:
                spatial_doc = extract_spatial_document_with_ocr(
                    file_bytes,
                    filename=filename,
                    ocr_service=ocr_service,
                    filetype=ext,
                )
                return DocumentRoutingResult(
                    document_type=DocumentType.IMAGE,
                    is_scanned=True,
                    native_word_count=0,
                    total_pages=len(spatial_doc.pages),
                    needs_ocr=True,
                    ocr_used=True,
                    ocr_engine="pymupdf_ocr" if ocr_service is None else type(ocr_service).__name__,
                    spatial_document=spatial_doc,
                    routing_reason="image_cv_routed_to_ocr",
                )
            except OCRExtractionError as ocr_err:
                return DocumentRoutingResult(
                    document_type=DocumentType.IMAGE,
                    is_scanned=True,
                    needs_ocr=True,
                    ocr_used=False,
                    routing_reason="image_ocr_extraction_failed",
                    error=str(ocr_err),
                )

        return DocumentRoutingResult(
            document_type=DocumentType.IMAGE,
            is_scanned=True,
            needs_ocr=True,
            ocr_used=False,
            routing_reason="image_ocr_disabled_or_unavailable",
            error="Image CV requires OCR, but OCR engine is unavailable or disabled.",
        )

    # ------------------------------------------------------------------------
    # 4. PDF Path: Native Text vs Scanned vs Hybrid
    # ------------------------------------------------------------------------
    if initial_type in (DocumentType.PDF_NATIVE_TEXT, DocumentType.NATIVE_PDF):
        qa = inspect_pdf_text_quality(file_bytes)
        total_words = sum(m.word_count for m in qa.pages_metrics)
        from app.services.ocr_service import (
            OCRExtractionError,
            extract_spatial_document_with_ocr,
            is_ocr_available,
        )

        ocr_available = is_ocr_available() if ocr_service is None else True

        # Case A: PDF_NATIVE_TEXT (All pages have high quality vector text)
        if qa.classification == DocumentType.PDF_NATIVE_TEXT:
            spatial_doc = extract_spatial_document(file_bytes, filename=filename)
            spatial_doc.metadata["extraction_method"] = "native"
            return DocumentRoutingResult(
                document_type=DocumentType.PDF_NATIVE_TEXT,
                is_scanned=False,
                native_word_count=total_words,
                total_pages=qa.total_pages,
                needs_ocr=False,
                ocr_used=False,
                spatial_document=spatial_doc,
                routing_reason="high_density_vector_text_extracted",
                metadata={"extraction_method": "native", "quality_assessment": qa.__dict__},
            )

        # Case B: PDF_HYBRID (Native text on some pages, scanned images elsewhere)
        if qa.classification == DocumentType.PDF_HYBRID:
            if not enable_ocr or (not ocr_available and ocr_service is None):
                # Fallback to native on whatever exists, but flag hybrid status
                spatial_doc = extract_spatial_document(file_bytes, filename=filename)
                return DocumentRoutingResult(
                    document_type=DocumentType.PDF_HYBRID,
                    is_scanned=True,
                    native_word_count=total_words,
                    total_pages=qa.total_pages,
                    needs_ocr=True,
                    ocr_used=False,
                    spatial_document=spatial_doc,
                    routing_reason="hybrid_pdf_ocr_disabled_partial_native_fallback",
                    metadata={"pages_needing_ocr": qa.pages_needing_ocr, "pages_native_good": qa.pages_native_good},
                    error="Hybrid PDF contains scanned pages, but OCR engine is unavailable or disabled.",
                )

            # Process Hybrid: Native on good pages, OCR on poor/scanned pages
            try:
                native_doc = extract_spatial_document(file_bytes, filename=filename)
                native_pages_map = {p.page_number: p for p in native_doc.pages}

                ocr_doc = extract_spatial_document_with_ocr(
                    file_bytes,
                    filename=filename,
                    ocr_service=ocr_service,
                    pages_to_ocr=qa.pages_needing_ocr,
                )
                ocr_pages_map = {p.page_number: p for p in ocr_doc.pages}

                combined_pages: List[SpatialPage] = []
                for p_num in range(1, qa.total_pages + 1):
                    if p_num in qa.pages_needing_ocr and p_num in ocr_pages_map:
                        combined_pages.append(ocr_pages_map[p_num])
                    elif p_num in native_pages_map:
                        combined_pages.append(native_pages_map[p_num])

                combined_raw_text = "\n\f\n".join(p.raw_text for p in combined_pages).strip()
                hybrid_spatial_doc = SpatialDocument(
                    filename=filename,
                    total_pages=len(combined_pages),
                    pages=combined_pages,
                    raw_text=combined_raw_text,
                    extraction_mode="pdf_hybrid_spatial",
                    metadata={
                        "extraction_method": "hybrid",
                        "hybrid": True,
                        "pages_native": qa.pages_native_good,
                        "pages_ocr": qa.pages_needing_ocr,
                        "ocr_engine": "pymupdf_ocr" if ocr_service is None else type(ocr_service).__name__,
                    },
                )
                return DocumentRoutingResult(
                    document_type=DocumentType.PDF_HYBRID,
                    is_scanned=True,
                    native_word_count=total_words,
                    total_pages=qa.total_pages,
                    needs_ocr=True,
                    ocr_used=True,
                    ocr_engine="pymupdf_ocr" if ocr_service is None else type(ocr_service).__name__,
                    spatial_document=hybrid_spatial_doc,
                    routing_reason="hybrid_pdf_native_plus_ocr_merged",
                    metadata={
                        "extraction_method": "hybrid",
                        "pages_ocr": qa.pages_needing_ocr,
                        "pages_native": qa.pages_native_good,
                    },
                )
            except Exception as hybrid_err:
                return DocumentRoutingResult(
                    document_type=DocumentType.PDF_HYBRID,
                    is_scanned=True,
                    native_word_count=total_words,
                    total_pages=qa.total_pages,
                    needs_ocr=True,
                    ocr_used=False,
                    routing_reason="hybrid_extraction_failed",
                    error=str(hybrid_err),
                )

        # Case C: PDF_SCANNED (All pages are image-only or poor quality)
        if enable_ocr and (ocr_available or ocr_service is not None):
            try:
                spatial_doc = extract_spatial_document_with_ocr(
                    file_bytes,
                    filename=filename,
                    ocr_service=ocr_service,
                )
                return DocumentRoutingResult(
                    document_type=DocumentType.PDF_SCANNED,
                    is_scanned=True,
                    native_word_count=total_words,
                    total_pages=qa.total_pages,
                    needs_ocr=True,
                    ocr_used=True,
                    ocr_engine="pymupdf_ocr" if ocr_service is None else type(ocr_service).__name__,
                    spatial_document=spatial_doc,
                    routing_reason="scanned_pdf_routed_to_ocr",
                )
            except OCRExtractionError as ocr_err:
                return DocumentRoutingResult(
                    document_type=DocumentType.PDF_SCANNED,
                    is_scanned=True,
                    native_word_count=total_words,
                    total_pages=qa.total_pages,
                    needs_ocr=True,
                    ocr_used=False,
                    routing_reason="ocr_extraction_failed",
                    error=str(ocr_err),
                )

        return DocumentRoutingResult(
            document_type=DocumentType.PDF_SCANNED,
            is_scanned=True,
            native_word_count=total_words,
            total_pages=qa.total_pages,
            needs_ocr=True,
            ocr_used=False,
            routing_reason="scanned_pdf_ocr_disabled_or_unavailable",
            error="Document is a scanned image, but OCR engine is unavailable or disabled.",
        )

    raise UnsupportedFileFormatError(f"Unsupported document format for '{filename}'.")
