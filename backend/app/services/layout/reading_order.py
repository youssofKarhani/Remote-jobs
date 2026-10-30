"""Logical Reading Order Reconstruction.

Sequences SourceBlocks across pages according to human reading flow:
Header -> Left Sidebar / Column 0 -> Main Body / Column 1 -> Footer.
Ensures multi-column CV content is not interleaved horizontally.
"""

from typing import Dict, List
from app.schemas.spatial import SpatialDocument, SpatialPage
from app.schemas.layout import ColumnLayout, LayoutDocument, SourceBlock
from app.services.layout.column_detector import detect_page_columns
from app.services.layout.block_builder import build_source_blocks


def _sort_blocks_in_page_reading_order(
    blocks: List[SourceBlock], layout: ColumnLayout
) -> List[SourceBlock]:
    """Sort blocks within a single page according to the detected column structure."""
    if not blocks:
        return []

    header_blocks = [b for b in blocks if b.region_type == "header"]
    footer_blocks = [b for b in blocks if b.region_type == "footer"]

    # Header and footer are ordered top-to-bottom, then left-to-right
    sorted_header = sorted(header_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
    sorted_footer = sorted(footer_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))

    # Body ordering depends on column layout
    sorted_body: List[SourceBlock] = []

    if layout.layout_type == "single_column":
        body_blocks = [b for b in blocks if b.region_type not in ("header", "footer")]
        sorted_body = sorted(body_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))

    elif layout.layout_type == "left_sidebar":
        sidebar_blocks = [b for b in blocks if b.region_type == "left_sidebar"]
        main_blocks = [b for b in blocks if b.region_type == "main_body"]
        sorted_sidebar = sorted(sidebar_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
        sorted_main = sorted(main_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
        # Left region read first, followed by main body region
        sorted_body = sorted_sidebar + sorted_main

    elif layout.layout_type == "right_sidebar":
        main_blocks = [b for b in blocks if b.region_type == "main_body"]
        sidebar_blocks = [b for b in blocks if b.region_type == "right_sidebar"]
        sorted_main = sorted(main_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
        sorted_sidebar = sorted(sidebar_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
        # Main body read first, followed by right sidebar
        sorted_body = sorted_main + sorted_sidebar

    elif layout.layout_type == "two_column":
        col0_blocks = [b for b in blocks if b.region_type == "column_0" or b.column == 0 and b.region_type not in ("header", "footer")]
        col1_blocks = [b for b in blocks if b.region_type == "column_1" or b.column == 1 and b.region_type not in ("header", "footer")]
        sorted_col0 = sorted(col0_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
        sorted_col1 = sorted(col1_blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
        # Column 0 read first, followed by Column 1
        sorted_body = sorted_col0 + sorted_col1

    else:
        # Multi-column (>= 3 columns)
        body_blocks = [b for b in blocks if b.region_type not in ("header", "footer")]
        # Group by column index
        cols: Dict[int, List[SourceBlock]] = {}
        for b in body_blocks:
            cols.setdefault(b.column, []).append(b)
        for col_idx in sorted(cols.keys()):
            sorted_body.extend(sorted(cols[col_idx], key=lambda b: (b.bbox.y0, b.bbox.x0)))

    return sorted_header + sorted_body + sorted_footer


def reconstruct_reading_order(spatial_doc: SpatialDocument) -> LayoutDocument:
    """Reconstruct logical reading order and structured source blocks from a SpatialDocument."""
    all_ordered_blocks: List[SourceBlock] = []
    layouts_by_page: Dict[int, ColumnLayout] = {}
    current_block_idx = 1
    reading_order_counter = 1

    for page in spatial_doc.pages:
        # 1. Detect column layout
        layout = detect_page_columns(page)
        layouts_by_page[page.page_number] = layout

        # 2. Build source blocks
        raw_blocks, current_block_idx = build_source_blocks(
            page, layout, start_block_index=current_block_idx
        )

        # 3. Sort page blocks into reading order
        page_ordered_blocks = _sort_blocks_in_page_reading_order(raw_blocks, layout)

        # 4. Assign document-wide reading order index
        for block in page_ordered_blocks:
            block.reading_order = reading_order_counter
            reading_order_counter += 1
            all_ordered_blocks.append(block)

    # 5. Build joined reading order text
    reading_order_text = "\n\n".join(b.text for b in all_ordered_blocks if b.text.strip())

    return LayoutDocument(
        filename=spatial_doc.filename,
        total_pages=spatial_doc.total_pages,
        source_blocks=all_ordered_blocks,
        layouts_by_page=layouts_by_page,
        reading_order_text=reading_order_text,
        extraction_mode=spatial_doc.extraction_mode,
        metadata=spatial_doc.metadata,
    )
