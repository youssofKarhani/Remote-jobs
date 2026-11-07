"""OCR Fallback Extraction Service (Phase 8).

Extracts spatial geometry and text from scanned/rasterized documents using
PyMuPDF OCR (Tesseract bindings) or pluggable OCR drivers.
Produces valid SpatialDocument instances with coordinate bounding boxes.
"""

from dataclasses import dataclass
import io
import logging
from typing import Any, Dict, List, Optional, Protocol

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
from app.services.document_parser import DocumentParsingError

logger = logging.getLogger(__name__)


class OCRExtractionError(DocumentParsingError):
    """Raised when OCR extraction fails or OCR dependencies are missing."""
    pass


class OCREngineProtocol(Protocol):
    """Protocol for pluggable or mocked OCR engines."""

    def extract_spatial_pages(self, file_bytes: bytes) -> List[SpatialPage]:
        ...


def is_ocr_available() -> bool:
    """Check if PyMuPDF OCR engine (Tesseract) is installed and operational."""
    if pymupdf is None or not hasattr(pymupdf.Page, "get_textpage_ocr"):
        return False

    try:
        doc = pymupdf.open()
        page = doc.new_page()
        # Probe call to detect missing tessdata
        _ = page.get_textpage_ocr(language="eng", dpi=72)
        doc.close()
        return True
    except Exception as exc:
        logger.debug(f"PyMuPDF OCR is not available on this system: {exc}")
        return False


@dataclass
class MockOCREngine:
    """Mock OCR driver for deterministic unit testing without external Tesseract binaries."""
    mock_pages_words: List[List[Dict[str, Any]]]

    def extract_spatial_pages(self, file_bytes: bytes) -> List[SpatialPage]:
        pages: List[SpatialPage] = []
        for page_idx, words_data in enumerate(self.mock_pages_words):
            page_num = page_idx + 1
            spatial_words: List[SpatialWord] = []
            lines_map: Dict[int, List[SpatialWord]] = {}

            for w_idx, w in enumerate(words_data):
                text = w.get("text", "")
                bbox_tuple = w.get("bbox", (50.0, 50.0 + (w_idx * 15.0), 100.0, 62.0 + (w_idx * 15.0)))
                line_idx = w.get("line_idx", 0)
                line_id = f"ocr_p{page_num}_l{line_idx}"
                word_id = f"ocr_p{page_num}_w{w_idx}"

                sw = SpatialWord(
                    word_id=word_id,
                    line_id=line_id,
                    page=page_num,
                    text=text,
                    x0=round(bbox_tuple[0], 2),
                    y0=round(bbox_tuple[1], 2),
                    x1=round(bbox_tuple[2], 2),
                    y1=round(bbox_tuple[3], 2),
                    font_name="OCR-Engine",
                    font_size=10.0,
                    is_bold=w.get("is_bold", False),
                )
                spatial_words.append(sw)
                lines_map.setdefault(line_idx, []).append(sw)

            spatial_lines: List[SpatialLine] = []
            for line_idx, line_words in lines_map.items():
                line_id = f"ocr_p{page_num}_l{line_idx}"
                lx0 = min(sw.x0 for sw in line_words)
                ly0 = min(sw.y0 for sw in line_words)
                lx1 = max(sw.x1 for sw in line_words)
                ly1 = max(sw.y1 for sw in line_words)
                spatial_lines.append(
                    SpatialLine(
                        line_id=line_id,
                        block_id=f"ocr_p{page_num}_b0",
                        page=page_num,
                        bbox=BoundingBox(x0=lx0, y0=ly0, x1=lx1, y1=ly1),
                        text=" ".join(sw.text for sw in line_words),
                        words=line_words,
                        font_name="OCR-Engine",
                        font_size=10.0,
                    )
                )

            block_text = "\n".join(l.text for l in spatial_lines)
            bx0 = min((l.bbox.x0 for l in spatial_lines), default=50.0)
            by0 = min((l.bbox.y0 for l in spatial_lines), default=50.0)
            bx1 = max((l.bbox.x1 for l in spatial_lines), default=500.0)
            by1 = max((l.bbox.y1 for l in spatial_lines), default=700.0)

            block = SpatialBlock(
                block_id=f"ocr_p{page_num}_b0",
                page=page_num,
                bbox=BoundingBox(x0=bx0, y0=by0, x1=bx1, y1=by1),
                raw_text=block_text,
                lines=spatial_lines,
            )

            pages.append(
                SpatialPage(
                    page_number=page_num,
                    width=612.0,
                    height=792.0,
                    bbox=BoundingBox(x0=0.0, y0=0.0, x1=612.0, y1=792.0),
                    blocks=[block],
                    raw_text=block_text,
                )
            )

        return pages


def extract_spatial_document_with_ocr(
    file_bytes: bytes,
    filename: str = "scanned.pdf",
    ocr_service: Optional[Any] = None,
) -> SpatialDocument:
    """Perform coordinate-aware OCR extraction and produce a valid SpatialDocument."""
    # 1. Custom / Mock OCR Engine Path
    if ocr_service is not None and hasattr(ocr_service, "extract_spatial_pages"):
        try:
            pages = ocr_service.extract_spatial_pages(file_bytes)
            full_text = "\n\f\n".join(p.raw_text for p in pages).strip()
            return SpatialDocument(
                filename=filename,
                total_pages=len(pages),
                pages=pages,
                raw_text=full_text,
                extraction_mode="mock_ocr_spatial",
                metadata={"ocr_engine": type(ocr_service).__name__},
            )
        except Exception as exc:
            raise OCRExtractionError(f"Mock OCR driver failed: {exc}") from exc

    # 2. Native PyMuPDF OCR Path
    if not is_ocr_available():
        raise OCRExtractionError(
            f"Document '{filename}' is a scanned rasterized PDF, but the Tesseract OCR engine "
            "is not installed or tessdata is unavailable on this system. "
            "Please install Tesseract or upload a vector/text-based PDF."
        )

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        pages: List[SpatialPage] = []
        raw_doc_text_parts: List[str] = []

        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            page_rect = page.rect
            page_w = round(float(page_rect.width), 2)
            page_h = round(float(page_rect.height), 2)

            textpage = page.get_textpage_ocr(language="eng", dpi=150)
            words = textpage.extractWORDS()
            page_raw = textpage.extractTEXT()
            raw_doc_text_parts.append(page_raw)

            spatial_words: List[SpatialWord] = []
            for w_idx, (x0, y0, x1, y1, word_str, block_no, line_no, word_no) in enumerate(words):
                line_id = f"ocr_p{page_num}_b{block_no}_l{line_no}"
                word_id = f"{line_id}_w{word_no}"
                sw = SpatialWord(
                    word_id=word_id,
                    line_id=line_id,
                    page=page_num,
                    text=word_str,
                    x0=round(x0, 2),
                    y0=round(y0, 2),
                    x1=round(x1, 2),
                    y1=round(y1, 2),
                    font_name="OCR-Tesseract",
                    font_size=10.0,
                )
                spatial_words.append(sw)

            # Group into lines and blocks
            lines_by_id: Dict[str, List[SpatialWord]] = {}
            for sw in spatial_words:
                lines_by_id.setdefault(sw.line_id, []).append(sw)

            spatial_lines: List[SpatialLine] = []
            for lid, lwords in lines_by_id.items():
                lx0 = min(sw.x0 for sw in lwords)
                ly0 = min(sw.y0 for sw in lwords)
                lx1 = max(sw.x1 for sw in lwords)
                ly1 = max(sw.y1 for sw in lwords)
                spatial_lines.append(
                    SpatialLine(
                        line_id=lid,
                        block_id=lid.rsplit("_l", 1)[0],
                        page=page_num,
                        bbox=BoundingBox(x0=lx0, y0=ly0, x1=lx1, y1=ly1),
                        text=" ".join(sw.text for sw in lwords),
                        words=lwords,
                        font_name="OCR-Tesseract",
                        font_size=10.0,
                    )
                )

            blocks_by_id: Dict[str, List[SpatialLine]] = {}
            for sl in spatial_lines:
                blocks_by_id.setdefault(sl.block_id, []).append(sl)

            spatial_blocks: List[SpatialBlock] = []
            for bid, blines in blocks_by_id.items():
                bx0 = min(sl.bbox.x0 for sl in blines)
                by0 = min(sl.bbox.y0 for sl in blines)
                bx1 = max(sl.bbox.x1 for sl in blines)
                by1 = max(sl.bbox.y1 for sl in blines)
                spatial_blocks.append(
                    SpatialBlock(
                        block_id=bid,
                        page=page_num,
                        bbox=BoundingBox(x0=bx0, y0=by0, x1=bx1, y1=by1),
                        raw_text="\n".join(sl.text for sl in blines),
                        lines=blines,
                    )
                )

            pages.append(
                SpatialPage(
                    page_number=page_num,
                    width=page_w,
                    height=page_h,
                    bbox=BoundingBox(x0=0.0, y0=0.0, x1=page_w, y1=page_h),
                    blocks=spatial_blocks,
                    raw_text=page_raw.strip(),
                )
            )

        doc.close()
        full_text = "\n\f\n".join(raw_doc_text_parts).strip()
        return SpatialDocument(
            filename=filename,
            total_pages=len(pages),
            pages=pages,
            raw_text=full_text,
            extraction_mode="pymupdf_ocr_spatial",
            metadata={"ocr_engine": "pymupdf_ocr"},
        )
    except Exception as exc:
        raise OCRExtractionError(f"PyMuPDF OCR extraction failed: {exc}") from exc
