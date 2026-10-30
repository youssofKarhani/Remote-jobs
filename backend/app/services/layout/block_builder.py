"""Source Block Builder with Strict Provenance.

Groups lines into cohesive logical SourceBlocks respecting column boundaries,
section headings, list items, and paragraph breaks. Assigns stable sequential identifiers.
"""

from typing import Dict, List, Optional
from app.schemas.spatial import BoundingBox, SpatialLine, SpatialPage, SpatialWord
from app.schemas.layout import ColumnLayout, HeadingCandidate, SourceBlock
from app.services.layout.heading_detector import (
    BULLET_PREFIX_REGEX,
    detect_heading_candidates,
)


def _compute_enclosing_bbox(lines: List[SpatialLine]) -> BoundingBox:
    """Compute minimal bounding box enclosing all lines in a block."""
    if not lines:
        return BoundingBox(x0=0.0, y0=0.0, x1=0.0, y1=0.0)
    x0 = min(l.bbox.x0 for l in lines)
    y0 = min(l.bbox.y0 for l in lines)
    x1 = max(l.bbox.x1 for l in lines)
    y1 = max(l.bbox.y1 for l in lines)
    return BoundingBox(x0=round(x0, 2), y0=round(y0, 2), x1=round(x1, 2), y1=round(y1, 2))


def _assign_line_region_and_column(
    line: SpatialLine, layout: ColumnLayout
) -> tuple[str, int]:
    """Determine the region and column index of a line based on page layout."""
    center_y = line.bbox.center_y
    center_x = line.bbox.center_x

    # Header check
    if layout.has_header_band and layout.header_boundary_y is not None:
        if center_y < layout.header_boundary_y:
            return "header", 0

    # Footer check
    if layout.has_footer_band and layout.footer_boundary_y is not None:
        if center_y > layout.footer_boundary_y:
            return "footer", 0

    # Body columns
    if layout.layout_type == "single_column" or not layout.columns:
        return "body", 0

    if layout.layout_type == "left_sidebar" and len(layout.columns) >= 2:
        col0_right = layout.columns[0].x1
        if center_x <= col0_right + 5.0:
            return "left_sidebar", 0
        return "main_body", 1

    if layout.layout_type == "right_sidebar" and len(layout.columns) >= 2:
        col0_right = layout.columns[0].x1
        if center_x <= col0_right + 5.0:
            return "main_body", 0
        return "right_sidebar", 1

    if layout.layout_type == "two_column" and len(layout.columns) >= 2:
        col0_right = layout.columns[0].x1
        if center_x <= col0_right + 5.0:
            return "column_0", 0
        return "column_1", 1

    # Multi-column fallback: find closest column by center_x
    best_col_idx = 0
    best_dist = float("inf")
    for idx, col_box in enumerate(layout.columns):
        dist = abs(center_x - col_box.center_x)
        if dist < best_dist:
            best_dist = dist
            best_col_idx = idx

    return f"column_{best_col_idx}", best_col_idx


def build_source_blocks(
    page: SpatialPage,
    column_layout: ColumnLayout,
    start_block_index: int = 1,
) -> tuple[List[SourceBlock], int]:
    """Construct logical SourceBlocks for a page with stable IDs and provenance.

    Returns (list of SourceBlocks, next_available_block_index).
    """
    lines = [l for l in page.all_lines if l.text.strip()]
    if not lines:
        return [], start_block_index

    # 1. Detect headings on this page
    headings = detect_heading_candidates(page)
    line_id_to_heading: Dict[str, HeadingCandidate] = {}
    processed_heading_candidates = set()
    for h in headings:
        for lid in h.source_line_ids:
            line_id_to_heading[lid] = h

    # 2. Partition lines into regions and columns
    # Format: region_key -> list of SpatialLine
    regions: Dict[str, List[SpatialLine]] = {}
    line_metadata: Dict[str, tuple[str, int]] = {}

    for l in lines:
        reg, col = _assign_line_region_and_column(l, column_layout)
        line_metadata[l.line_id] = (reg, col)
        if reg not in regions:
            regions[reg] = []
        regions[reg].append(l)

    # 3. Process each region to form SourceBlocks
    built_blocks: List[SourceBlock] = []
    current_idx = start_block_index

    for region_name, reg_lines in regions.items():
        sorted_reg_lines = sorted(reg_lines, key=lambda l: (l.bbox.y0, l.bbox.x0))
        open_group: List[SpatialLine] = []
        open_col_idx = line_metadata[sorted_reg_lines[0].line_id][1]

        def flush_open_group():
            nonlocal current_idx, open_group
            if not open_group:
                return
            block_id = f"BLOCK_{current_idx:03d}"
            current_idx += 1
            bbox = _compute_enclosing_bbox(open_group)
            clean_text = "\n".join(l.text.strip() for l in open_group if l.text.strip())
            raw_text = "\n".join(l.text for l in open_group)
            line_ids = [l.line_id for l in open_group]
            word_ids = [w.word_id for l in open_group for w in l.words if w.word_id]

            font_sizes = [l.font_size for l in open_group if l.font_size]
            dominant_size = font_sizes[0] if font_sizes else None
            is_bold = any(l.is_bold for l in open_group)

            built_blocks.append(
                SourceBlock(
                    id=block_id,
                    page=page.page_number,
                    column=open_col_idx,
                    region_type=region_name,
                    bbox=bbox,
                    text=clean_text,
                    raw_text=raw_text,
                    reading_order=0,  # Will be assigned by reading_order reconstructor
                    is_heading=False,
                    heading_level=None,
                    font_size=dominant_size,
                    is_bold=is_bold,
                    source_line_ids=line_ids,
                    source_word_ids=word_ids,
                )
            )
            open_group = []

        i = 0
        while i < len(sorted_reg_lines):
            line = sorted_reg_lines[i]
            lid = line.line_id
            reg, col = line_metadata[lid]

            # Case A: Line is part of a detected Heading Candidate
            if lid in line_id_to_heading:
                heading = line_id_to_heading[lid]
                flush_open_group()

                # Collect all lines for this heading candidate
                heading_lines = [l for l in sorted_reg_lines if l.line_id in heading.source_line_ids]
                if not heading_lines:
                    heading_lines = [line]

                block_id = f"BLOCK_{current_idx:03d}"
                current_idx += 1
                built_blocks.append(
                    SourceBlock(
                        id=block_id,
                        page=page.page_number,
                        column=col,
                        region_type=region_name,
                        bbox=heading.bbox,
                        text=heading.text,
                        raw_text=heading.raw_text,
                        reading_order=0,
                        is_heading=True,
                        heading_level=heading.heading_level,
                        font_size=heading.font_size,
                        is_bold=heading.is_bold,
                        source_line_ids=heading.source_line_ids,
                        source_word_ids=[w.word_id for l in heading_lines for w in l.words if w.word_id],
                    )
                )
                # Advance past all lines consumed by this heading
                for hl in heading_lines:
                    if hl in sorted_reg_lines:
                        pass
                i += len(heading_lines)
                continue

            # Case B: Standard body line
            if not open_group:
                open_group.append(line)
                open_col_idx = col
            else:
                prev_line = open_group[-1]
                v_gap = line.bbox.y0 - prev_line.bbox.y1
                prev_is_bullet = bool(BULLET_PREFIX_REGEX.match(prev_line.text.strip()))
                curr_is_bullet = bool(BULLET_PREFIX_REGEX.match(line.text.strip()))

                # Significant vertical gap indicates a new paragraph or entry
                line_height = prev_line.bbox.height or 12.0
                is_large_gap = v_gap > (1.8 * line_height)

                # Bullet points: new bullet marker begins a new block
                if curr_is_bullet:
                    flush_open_group()
                    open_group.append(line)
                    open_col_idx = col
                elif is_large_gap:
                    flush_open_group()
                    open_group.append(line)
                    open_col_idx = col
                else:
                    # Cohesive continuation of paragraph or indented list item
                    open_group.append(line)

            i += 1

        flush_open_group()

    return built_blocks, current_idx
