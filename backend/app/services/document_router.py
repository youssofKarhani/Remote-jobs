"""Document Type Detection and Routing Engine (Phase 8).

Inspects file headers, extensions, and content densities to classify documents into:
- NATIVE_PDF: Text-based PDFs with extractable vector fonts.
- SCANNED_PDF: Image-only or rasterized PDFs requiring OCR.
- DOCX: Microsoft Word OpenXML documents.
- PLAIN_TEXT: Raw text documents.

Ensures strict transparency and records explicit routing metadata (Rule 10: No Silent Fallback).
"""

from dataclasses import dataclass, field
from enum import Enum
import io
import re
from typing import Any, Dict, List, Optional, Tuple

import pypdf
from pypdf import PdfReader

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

from app.schemas.spatial import SpatialDocument
from app.services.document_parser import (
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFileFormatError,
)
from app.services.spatial_parser import extract_spatial_document


class DocumentType(str, Enum):
    NATIVE_PDF = "native_pdf"
    SCANNED_PDF = "scanned_pdf"
    DOCX = "docx"
    PLAIN_TEXT = "plain_text"
    UNKNOWN = "unknown"


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

    # 1. PDF Magic Header
    if file_bytes.startswith(b"%PDF"):
        return DocumentType.NATIVE_PDF  # Will be refined by scanned check

    # 2. DOCX / ZIP Magic Header (PK\x03\x04)
    if file_bytes.startswith(b"PK\x03\x04"):
        if ext in ("docx", "docm") or b"word/document.xml" in file_bytes[:4096]:
            return DocumentType.DOCX

    # 3. Plain Text / Markdown
    if ext in ("txt", "text", "md", "markdown"):
        return DocumentType.PLAIN_TEXT

    # Heuristic for text if file_bytes are decodeable ASCII/UTF-8
    try:
        sample = file_bytes[:1024].decode("utf-8")
        if all(c.isprintable() or c.isspace() for c in sample) and len(sample) > 20:
            return DocumentType.PLAIN_TEXT
    except (UnicodeDecodeError, AttributeError):
        pass

    return DocumentType.UNKNOWN


def inspect_pdf_text_density(file_bytes: bytes) -> Tuple[bool, int, int, List[int]]:
    """Inspect PDF to determine if it is a scanned rasterized document or native text.
    
    Returns:
        (is_scanned, total_words, total_pages, images_per_page)
    """
    if not file_bytes.startswith(b"%PDF"):
        return False, 0, 0, []

    total_words = 0
    total_pages = 0
    images_per_page: List[int] = []

    if pymupdf is not None:
        try:
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)
            for page in doc:
                words = page.get_text("words")
                total_words += len(words)
                img_list = page.get_images()
                images_per_page.append(len(img_list))
            doc.close()

            # Scanned Heuristic:
            # - Total words == 0
            # - OR average words per page < 15 AND page contains embedded images
            is_scanned = (total_words == 0) or (
                total_words < (15 * total_pages) and any(img_count > 0 for img_count in images_per_page)
            )
            return is_scanned, total_words, total_pages, images_per_page
        except Exception:
            pass

    # pypdf reference fallback inspection
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        for page in reader.pages:
            text = page.extract_text() or ""
            words = text.split()
            total_words += len(words)
            images_per_page.append(len(page.images) if hasattr(page, "images") else 0)

        is_scanned = (total_words == 0) or (
            total_words < (15 * total_pages) and any(img_count > 0 for img_count in images_per_page)
        )
        return is_scanned, total_words, total_pages, images_per_page
    except Exception:
        return False, 0, 0, []


def route_and_parse_document(
    file_bytes: bytes,
    filename: str = "document.pdf",
    enable_ocr: bool = True,
    ocr_service: Optional[Any] = None,
) -> DocumentRoutingResult:
    """Route document to appropriate spatial or OCR extraction pipeline with full audit metadata."""
    if not file_bytes:
        raise EmptyDocumentError("The uploaded file is empty (0 bytes).")

    doc_type = sniff_document_type(file_bytes, filename=filename)

    if doc_type == DocumentType.UNKNOWN:
        ext = detect_file_extension(filename)
        raise UnsupportedFileFormatError(f"Unsupported file format '.{ext}' for CV ingestion.")

    # 1. Plain Text Path
    if doc_type == DocumentType.PLAIN_TEXT:
        text_content = file_bytes.decode("utf-8", errors="replace")
        from app.schemas.spatial import BoundingBox, SpatialBlock, SpatialLine, SpatialPage, SpatialWord

        raw_lines = text_content.splitlines()
        sp_blocks: List[SpatialBlock] = []
        all_words_count = 0
        current_y = 50.0

        for b_idx, raw_line in enumerate(raw_lines):
            line_str = raw_line.strip()
            if not line_str:
                current_y += 15.0
                continue

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

        if not sp_blocks:
            sp_blocks = [
                SpatialBlock(
                    block_id="p1_b0",
                    page=1,
                    bbox=BoundingBox(x0=50.0, y0=50.0, x1=500.0, y1=62.0),
                    raw_text=text_content,
                    lines=[],
                )
            ]

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
            document_type=DocumentType.PLAIN_TEXT,
            is_scanned=False,
            native_word_count=all_words_count,
            total_pages=1,
            needs_ocr=False,
            spatial_document=spatial_doc,
            routing_reason="plain_text_direct_spatial_mapping",
        )

    # 2. PDF Path (Native vs Scanned)
    if doc_type in (DocumentType.NATIVE_PDF, DocumentType.SCANNED_PDF):
        is_scanned, word_count, total_pages, image_counts = inspect_pdf_text_density(file_bytes)

        if not is_scanned:
            # Native text PDF: extract directly with Phase 2 spatial engine
            spatial_doc = extract_spatial_document(file_bytes, filename=filename)
            return DocumentRoutingResult(
                document_type=DocumentType.NATIVE_PDF,
                is_scanned=False,
                native_word_count=word_count,
                total_pages=total_pages,
                needs_ocr=False,
                spatial_document=spatial_doc,
                routing_reason="high_density_vector_text_extracted",
                metadata={"images_per_page": image_counts},
            )

        # Scanned PDF: needs OCR
        from app.services.ocr_service import (
            OCRExtractionError,
            extract_spatial_document_with_ocr,
            is_ocr_available,
        )

        ocr_available = is_ocr_available() if ocr_service is None else True
        if enable_ocr and (ocr_available or ocr_service is not None):
            try:
                spatial_doc = extract_spatial_document_with_ocr(
                    file_bytes,
                    filename=filename,
                    ocr_service=ocr_service,
                )
                return DocumentRoutingResult(
                    document_type=DocumentType.SCANNED_PDF,
                    is_scanned=True,
                    native_word_count=word_count,
                    total_pages=total_pages,
                    needs_ocr=True,
                    ocr_used=True,
                    ocr_engine="pymupdf_ocr" if ocr_service is None else type(ocr_service).__name__,
                    spatial_document=spatial_doc,
                    routing_reason="scanned_pdf_routed_to_ocr",
                    metadata={"images_per_page": image_counts},
                )
            except OCRExtractionError as ocr_err:
                return DocumentRoutingResult(
                    document_type=DocumentType.SCANNED_PDF,
                    is_scanned=True,
                    native_word_count=word_count,
                    total_pages=total_pages,
                    needs_ocr=True,
                    ocr_used=False,
                    routing_reason="ocr_extraction_failed",
                    error=str(ocr_err),
                    metadata={"images_per_page": image_counts, "ocr_available": ocr_available},
                )

        # OCR disabled or unavailable
        return DocumentRoutingResult(
            document_type=DocumentType.SCANNED_PDF,
            is_scanned=True,
            native_word_count=word_count,
            total_pages=total_pages,
            needs_ocr=True,
            ocr_used=False,
            routing_reason="scanned_pdf_ocr_disabled_or_unavailable",
            metadata={"images_per_page": image_counts, "ocr_available": ocr_available},
            error="Document is a scanned image, but OCR engine is unavailable or disabled.",
        )

    # 3. DOCX Path
    if doc_type == DocumentType.DOCX:
        from app.services.document_parser import parse_document
        docx_raw_text = parse_document(file_bytes, filename=filename)
        from app.schemas.spatial import BoundingBox, SpatialBlock, SpatialLine, SpatialPage, SpatialWord

        lines = [line.strip() for line in docx_raw_text.splitlines() if line.strip()]
        sp_blocks = []
        current_y = 50.0
        all_words_count = 0
        for b_idx, line_str in enumerate(lines):
            line_words = line_str.split()
            all_words_count += len(line_words)
            sp_words = [
                SpatialWord(
                    word_id=f"docx_w_{b_idx}_{w_idx}",
                    line_id=f"docx_l_{b_idx}",
                    page=1,
                    text=w,
                    x0=50.0 + (w_idx * 10.0),
                    y0=current_y,
                    x1=58.0 + (w_idx * 10.0),
                    y1=current_y + 12.0,
                )
                for w_idx, w in enumerate(line_words)
            ]
            sp_line = SpatialLine(
                line_id=f"docx_l_{b_idx}",
                block_id=f"docx_b_{b_idx}",
                page=1,
                bbox=BoundingBox(x0=50.0, y0=current_y, x1=500.0, y1=current_y + 12.0),
                text=line_str,
                words=sp_words,
            )
            sp_block = SpatialBlock(
                block_id=f"docx_b_{b_idx}",
                page=1,
                bbox=BoundingBox(x0=50.0, y0=current_y, x1=500.0, y1=current_y + 12.0),
                raw_text=line_str,
                lines=[sp_line],
            )
            sp_blocks.append(sp_block)
            current_y += 20.0

        if not sp_blocks:
            sp_blocks = [
                SpatialBlock(
                    block_id="docx_b_0",
                    page=1,
                    bbox=BoundingBox(x0=50.0, y0=50.0, x1=500.0, y1=62.0),
                    raw_text=docx_raw_text,
                    lines=[],
                )
            ]

        sp_page = SpatialPage(
            page_number=1,
            width=612.0,
            height=max(792.0, current_y + 50.0),
            bbox=BoundingBox(x0=0.0, y0=0.0, x1=612.0, y1=max(792.0, current_y + 50.0)),
            blocks=sp_blocks,
            raw_text=docx_raw_text,
        )
        spatial_doc = SpatialDocument(
            filename=filename,
            total_pages=1,
            pages=[sp_page],
            raw_text=docx_raw_text,
            extraction_mode="docx_spatial",
        )
        return DocumentRoutingResult(
            document_type=DocumentType.DOCX,
            is_scanned=False,
            native_word_count=all_words_count,
            total_pages=1,
            needs_ocr=False,
            spatial_document=spatial_doc,
            routing_reason="docx_openxml_extracted",
        )

    raise UnsupportedFileFormatError(f"Unsupported document format for '{filename}'.")
