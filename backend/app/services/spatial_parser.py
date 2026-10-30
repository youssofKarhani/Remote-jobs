"""Spatial PDF Document Parser.

Extracts coordinate-aware layout geometry (blocks, lines, words, typography, bounding boxes)
using PyMuPDF (fitz) with a pypdf reference fallback path.
Never discards raw content, and maintains strict separation from semantic CV extraction.
"""

from collections import defaultdict
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


def _infer_typography(span: Dict[str, Any]) -> Tuple[str, Optional[float], bool, bool, str, int, Optional[int]]:
    """Extract font name, size, bold/italic flags, font style string, weight, and color from a PyMuPDF span."""
    font_name = str(span.get("font", "unknown"))
    raw_size = span.get("size")
    font_size = round(float(raw_size), 2) if raw_size is not None else None
    flags = int(span.get("flags", 0))

    # Bit 4 (16) is bold, bit 1 (2) is italic in MuPDF
    is_bold = bool(flags & 16) or any(k in font_name.lower() for k in ["bold", "black", "heavy", "medium", "semibold"])
    is_italic = bool(flags & 2) or any(k in font_name.lower() for k in ["italic", "oblique", "slanted"])

    if is_bold and is_italic:
        style = "bold_italic"
    elif is_bold:
        style = "bold"
    elif is_italic:
        style = "italic"
    else:
        style = "normal"

    weight = 700 if is_bold else 400
    color = span.get("color")

    return font_name, font_size, is_bold, is_italic, style, weight, color


def _find_matching_span(
    w_bbox: Tuple[float, float, float, float],
    spans: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Find the span in a line that encloses or is closest to a word bounding box."""
    if not spans:
        return None
    if len(spans) == 1:
        return spans[0]

    w_x0, _, w_x1, _ = w_bbox
    w_cx = (w_x0 + w_x1) / 2.0

    # 1. Direct horizontal containment
    for s in spans:
        s_bbox = s.get("bbox", (0, 0, 0, 0))
        if s_bbox[0] - 1.5 <= w_cx <= s_bbox[2] + 1.5:
            return s

    # 2. Closest span by horizontal boundary distance
    def _dist(s: Dict[str, Any]) -> float:
        sb = s.get("bbox", (0, 0, 0, 0))
        if sb[2] < w_x0:
            return w_x0 - sb[2]
        if sb[0] > w_x1:
            return sb[0] - w_x1
        return 0.0

    return min(spans, key=_dist)


def _split_words_into_line_runs(
    words: List[SpatialWord], max_word_gap: float = 30.0
) -> List[List[SpatialWord]]:
    """Partition words on a common baseline into distinct line runs if separated by a visual gutter."""
    if not words:
        return []
    sorted_words = sorted(words, key=lambda w: w.x0)
    runs: List[List[SpatialWord]] = []
    current_run: List[SpatialWord] = [sorted_words[0]]
    for w in sorted_words[1:]:
        gap = w.x0 - current_run[-1].x1
        if gap > max_word_gap:
            runs.append(current_run)
            current_run = [w]
        else:
            current_run.append(w)
    runs.append(current_run)
    return runs


def _cluster_lines_into_blocks(
    lines: List[SpatialLine],
    block_id_prefix: str,
    page_num: int,
) -> List[SpatialBlock]:
    """Cluster lines into cohesive SpatialBlocks by horizontal continuity to avoid merging visually distant content."""
    if not lines:
        return []
    if len(lines) == 1:
        return [
            SpatialBlock(
                block_id=block_id_prefix,
                page=page_num,
                bbox=lines[0].bbox,
                block_type="text",
                raw_text=lines[0].text,
                lines=lines,
            )
        ]

    n = len(lines)
    parent = list(range(n))

    def find(i: int) -> int:
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        for j in range(i + 1, n):
            h_dist = lines[i].bbox.horizontal_distance_to(lines[j].bbox)
            if h_dist <= 35.0:
                union(i, j)

    clusters_dict: Dict[int, List[SpatialLine]] = defaultdict(list)
    for i in range(n):
        clusters_dict[find(i)].append(lines[i])

    clusters = list(clusters_dict.values())
    # Sort clusters by reading order: top-to-bottom, left-to-right
    clusters.sort(key=lambda c: (min(l.bbox.y0 for l in c), min(l.bbox.x0 for l in c)))

    blocks: List[SpatialBlock] = []
    for c_idx, c_lines in enumerate(clusters):
        c_id = block_id_prefix if len(clusters) == 1 else f"{block_id_prefix}_{c_idx}"
        c_x0 = min(l.bbox.x0 for l in c_lines)
        c_y0 = min(l.bbox.y0 for l in c_lines)
        c_x1 = max(l.bbox.x1 for l in c_lines)
        c_y1 = max(l.bbox.y1 for l in c_lines)
        c_bbox = BoundingBox(x0=c_x0, y0=c_y0, x1=c_x1, y1=c_y1)
        c_text = "\n".join(l.text for l in c_lines).strip()
        blocks.append(
            SpatialBlock(
                block_id=c_id,
                page=page_num,
                bbox=c_bbox,
                block_type="text",
                raw_text=c_text,
                lines=c_lines,
            )
        )
    return blocks


def _extract_with_pymupdf(file_bytes: bytes, filename: str) -> SpatialDocument:
    """Extract spatial document structure using PyMuPDF."""
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise DocumentParsingError(f"PyMuPDF failed to open PDF document: {str(e)}") from e

    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        raise EmptyDocumentError("The uploaded PDF contains no pages.")

    pages: List[SpatialPage] = []
    raw_doc_text_parts: List[str] = []
    total_words_count = 0

    try:
        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            rect = page.rect
            page_w = round(float(rect.width), 2)
            page_h = round(float(rect.height), 2)
            page_bbox = BoundingBox(x0=0.0, y0=0.0, x1=page_w, y1=page_h)

            dict_data = page.get_text("dict")
            words_data = page.get_text("words")
            page_raw_text = page.get_text("text") or ""
            raw_doc_text_parts.append(page_raw_text)

            # Group words by (block_no, line_no)
            words_by_line: Dict[Tuple[int, int], List[Tuple]] = defaultdict(list)
            for w in words_data:
                # w is (x0, y0, x1, y1, word_text, block_no, line_no, word_no)
                words_by_line[(int(w[5]), int(w[6]))].append(w)

            spatial_blocks: List[SpatialBlock] = []
            dict_blocks = dict_data.get("blocks", [])

            for b_idx, b in enumerate(dict_blocks):
                # type 0: text block
                b_type_code = b.get("type", 0)
                if b_type_code != 0:
                    continue

                b_bbox_raw = b.get("bbox", (0, 0, 0, 0))
                b_bbox = BoundingBox(
                    x0=round(float(b_bbox_raw[0]), 2),
                    y0=round(float(b_bbox_raw[1]), 2),
                    x1=round(float(b_bbox_raw[2]), 2),
                    y1=round(float(b_bbox_raw[3]), 2),
                )
                block_id = f"p{page_num}_b{b_idx}"

                lines_data = b.get("lines", [])
                spatial_lines: List[SpatialLine] = []
                block_text_runs: List[str] = []

                for l_idx, line in enumerate(lines_data):
                    l_bbox_raw = line.get("bbox", (0, 0, 0, 0))
                    l_bbox = BoundingBox(
                        x0=round(float(l_bbox_raw[0]), 2),
                        y0=round(float(l_bbox_raw[1]), 2),
                        x1=round(float(l_bbox_raw[2]), 2),
                        y1=round(float(l_bbox_raw[3]), 2),
                    )
                    line_id = f"{block_id}_l{l_idx}"
                    spans = line.get("spans", [])

                    line_words: List[SpatialWord] = []
                    raw_line_words = words_by_line.get((b_idx, l_idx), [])

                    for w_idx, w in enumerate(raw_line_words):
                        w_bbox = (float(w[0]), float(w[1]), float(w[2]), float(w[3]))
                        matched_span = _find_matching_span(w_bbox, spans)
                        if matched_span:
                            font_name, font_size, is_bold, is_italic, style, weight, color = _infer_typography(matched_span)
                        else:
                            font_name, font_size, is_bold, is_italic, style, weight, color = ("unknown", None, False, False, "normal", 400, None)

                        word_id = f"{line_id}_w{w_idx}"
                        spatial_word = SpatialWord(
                            text=str(w[4]),
                            page=page_num,
                            x0=round(float(w[0]), 2),
                            y0=round(float(w[1]), 2),
                            x1=round(float(w[2]), 2),
                            y1=round(float(w[3]), 2),
                            block_id=block_id,
                            line_id=line_id,
                            word_id=word_id,
                            font_name=font_name,
                            font_size=font_size,
                            is_bold=is_bold,
                            is_italic=is_italic,
                            font_style=style,
                            weight=weight,
                            color=color,
                        )
                        line_words.append(spatial_word)
                        total_words_count += 1

                    # Split words if they cross a prominent horizontal gutter (> 30 pt)
                    word_runs = _split_words_into_line_runs(line_words, max_word_gap=30.0)
                    if not word_runs and spans:
                        # Fallback to span text if words_data omitted single symbols
                        fallback_text = "".join(s.get("text", "") for s in spans).strip()
                        if fallback_text:
                            block_text_runs.append(fallback_text)
                            spatial_lines.append(
                                SpatialLine(
                                    line_id=line_id,
                                    block_id=block_id,
                                    page=page_num,
                                    bbox=l_bbox,
                                    text=fallback_text,
                                    words=[],
                                    font_name=spans[0].get("font") if spans else None,
                                    font_size=round(float(spans[0].get("size", 10.0)), 2) if spans else None,
                                    is_bold=False,
                                    is_italic=False,
                                )
                            )
                    else:
                        for run_idx, run_words in enumerate(word_runs):
                            run_text = " ".join(sw.text for sw in run_words).strip()
                            if not run_text:
                                continue
                            run_line_id = f"{line_id}_{run_idx}" if len(word_runs) > 1 else line_id
                            # Re-assign line_id and word_id on spatial_words if split
                            if len(word_runs) > 1:
                                for widx, sw in enumerate(run_words):
                                    sw.line_id = run_line_id
                                    sw.word_id = f"{run_line_id}_w{widx}"

                            rx0 = min(sw.x0 for sw in run_words)
                            ry0 = min(sw.y0 for sw in run_words)
                            rx1 = max(sw.x1 for sw in run_words)
                            ry1 = max(sw.y1 for sw in run_words)
                            run_bbox = BoundingBox(x0=rx0, y0=ry0, x1=rx1, y1=ry1)

                            predominant_font = run_words[0].font_name if run_words else None
                            predominant_size = run_words[0].font_size if run_words else None
                            line_is_bold = any(sw.is_bold for sw in run_words)
                            line_is_italic = any(sw.is_italic for sw in run_words)

                            block_text_runs.append(run_text)
                            spatial_lines.append(
                                SpatialLine(
                                    line_id=run_line_id,
                                    block_id=block_id,
                                    page=page_num,
                                    bbox=run_bbox,
                                    text=run_text,
                                    words=run_words,
                                    font_name=predominant_font,
                                    font_size=predominant_size,
                                    is_bold=line_is_bold,
                                    is_italic=line_is_italic,
                                )
                            )

                if spatial_lines:
                    spatial_blocks.extend(_cluster_lines_into_blocks(spatial_lines, block_id, page_num))
                elif block_text_runs:
                    block_raw_text = "\n".join(block_text_runs).strip()
                    spatial_blocks.append(
                        SpatialBlock(
                            block_id=block_id,
                            page=page_num,
                            bbox=b_bbox,
                            block_type="text",
                            raw_text=block_raw_text,
                            lines=[],
                        )
                    )

            pages.append(
                SpatialPage(
                    page_number=page_num,
                    width=page_w,
                    height=page_h,
                    bbox=page_bbox,
                    blocks=spatial_blocks,
                    raw_text=page_raw_text.strip(),
                )
            )

        metadata: Dict[str, Any] = {}
        try:
            if doc.metadata:
                metadata = {
                    k: v for k, v in doc.metadata.items()
                    if v and isinstance(v, (str, int, float, bool))
                }
        except Exception:
            metadata = {}
    finally:
        doc.close()

    full_raw_text = "\n\f\n".join(raw_doc_text_parts).strip()
    if total_words_count == 0 and not full_raw_text:
        raise EmptyDocumentError(
            "The document contains no readable text or is a scanned image. "
            "Please provide a text-based PDF resume."
        )

    return SpatialDocument(
        filename=filename,
        total_pages=total_pages,
        pages=pages,
        raw_text=full_raw_text,
        extraction_mode="pymupdf_spatial",
        metadata=metadata,
    )


def _extract_with_pypdf_fallback(file_bytes: bytes, filename: str) -> SpatialDocument:
    """Fallback spatial extraction path using pypdf when PyMuPDF is unavailable or fails."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        raise DocumentParsingError(f"Failed to read PDF with pypdf: {str(e)}") from e

    total_pages = len(reader.pages)
    if total_pages == 0:
        raise EmptyDocumentError("The uploaded PDF contains no pages.")

    pages: List[SpatialPage] = []
    raw_doc_text_parts: List[str] = []
    total_words_count = 0

    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        page_w = 612.0
        page_h = 792.0
        try:
            mediabox = page.mediabox
            page_w = round(float(mediabox.width), 2)
            page_h = round(float(mediabox.height), 2)
        except Exception:
            pass

        page_bbox = BoundingBox(x0=0.0, y0=0.0, x1=page_w, y1=page_h)

        # Attempt layout extraction first, then plain
        page_raw_text: Optional[str] = None
        try:
            page_raw_text = page.extract_text(extraction_mode="layout")
        except Exception:
            page_raw_text = None

        if not page_raw_text or not page_raw_text.strip():
            page_raw_text = page.extract_text() or ""

        raw_doc_text_parts.append(page_raw_text)

        # Deconstruct lines and estimate geometry
        raw_lines = [ln for ln in page_raw_text.splitlines() if ln.strip()]
        line_height = 14.0
        curr_y = 50.0

        spatial_lines: List[SpatialLine] = []
        block_id = f"p{page_num}_b0"

        for l_idx, ln in enumerate(raw_lines):
            line_id = f"{block_id}_l{l_idx}"
            tokens = ln.split()
            l_words: List[SpatialWord] = []
            curr_x = 50.0

            for w_idx, tok in enumerate(tokens):
                tok_len = len(tok) * 7.0
                word_id = f"{line_id}_w{w_idx}"
                s_word = SpatialWord(
                    text=tok,
                    page=page_num,
                    x0=round(curr_x, 2),
                    y0=round(curr_y, 2),
                    x1=round(curr_x + tok_len, 2),
                    y1=round(curr_y + line_height, 2),
                    block_id=block_id,
                    line_id=line_id,
                    word_id=word_id,
                    font_name="Helvetica",
                    font_size=10.0,
                    is_bold=False,
                    is_italic=False,
                    font_style="normal",
                    weight=400,
                )
                l_words.append(s_word)
                total_words_count += 1
                curr_x += tok_len + 5.0

            l_bbox = BoundingBox(
                x0=50.0,
                y0=round(curr_y, 2),
                x1=round(max(curr_x, 50.0), 2),
                y1=round(curr_y + line_height, 2),
            )
            spatial_lines.append(
                SpatialLine(
                    line_id=line_id,
                    block_id=block_id,
                    page=page_num,
                    bbox=l_bbox,
                    text=" ".join(tokens),
                    words=l_words,
                    font_name="Helvetica",
                    font_size=10.0,
                    is_bold=False,
                    is_italic=False,
                )
            )
            curr_y += line_height + 4.0

        block_bbox = BoundingBox(
            x0=50.0,
            y0=50.0,
            x1=round(max((l.bbox.x1 for l in spatial_lines), default=page_w), 2),
            y1=round(curr_y, 2),
        )
        spatial_block = SpatialBlock(
            block_id=block_id,
            page=page_num,
            bbox=block_bbox,
            block_type="text",
            raw_text="\n".join(l.text for l in spatial_lines),
            lines=spatial_lines,
        )

        pages.append(
            SpatialPage(
                page_number=page_num,
                width=page_w,
                height=page_h,
                bbox=page_bbox,
                blocks=[spatial_block] if spatial_lines else [],
                raw_text=page_raw_text.strip(),
            )
        )

    full_raw_text = "\n\f\n".join(raw_doc_text_parts).strip()
    if total_words_count == 0 and not full_raw_text:
        raise EmptyDocumentError(
            "The document contains no readable text or is a scanned image. "
            "Please provide a text-based PDF resume."
        )

    return SpatialDocument(
        filename=filename,
        total_pages=total_pages,
        pages=pages,
        raw_text=full_raw_text,
        extraction_mode="pypdf_fallback",
        metadata={"producer": "pypdf_fallback"},
    )


def extract_spatial_document(
    file_bytes: bytes,
    filename: str = "resume.pdf",
    force_fallback: bool = False,
) -> SpatialDocument:
    """Extract coordinate-aware SpatialDocument from a PDF binary.

    Uses PyMuPDF as primary spatial engine with automatic pypdf fallback.
    Preserves all raw text, page boundaries, and bounding box geometry.
    """
    if not file_bytes:
        raise EmptyDocumentError("The uploaded file is empty (0 bytes).")

    ext = filename.lower().split(".")[-1] if "." in filename else ""
    if ext and ext != "pdf":
        raise UnsupportedFileFormatError(
            f"Spatial extraction currently requires a PDF document, received '.{ext}'."
        )

    # Validate PDF magic header
    if not file_bytes.startswith(b"%PDF"):
        raise DocumentParsingError("Invalid file header: Not a valid PDF document.")

    if not force_fallback and pymupdf is not None:
        try:
            return _extract_with_pymupdf(file_bytes, filename)
        except (EmptyDocumentError, UnsupportedFileFormatError):
            raise
        except Exception:
            # Safe fallback to pypdf reference path
            pass

    return _extract_with_pypdf_fallback(file_bytes, filename)
