"""Deterministic Column and Layout Detector.

Analyzes horizontal text projections, whitespace gutters, and vertical bands
to detect single-column, two-column, sidebar, and multi-column document layouts.
"""

from typing import List, Optional, Tuple
from app.schemas.spatial import BoundingBox, SpatialLine, SpatialPage
from app.schemas.layout import ColumnLayout


def _find_gutters_in_lines(lines: List[SpatialLine], min_gutter_width: float = 14.0) -> Tuple[float, float, List[Tuple[float, float]]]:
    """Find empty vertical whitespace channels (gutters) across a set of lines.

    Returns (min_x, max_x, list of (gutter_x0, gutter_x1) tuples).
    """
    if not lines or len(lines) < 3:
        return 0.0, 0.0, []

    min_x = min(l.bbox.x0 for l in lines)
    max_x = max(l.bbox.x1 for l in lines)
    content_width = max_x - min_x

    if content_width < 120.0:
        return min_x, max_x, []

    # Discretize X axis into 1-point intervals from min_x to max_x
    start_int = int(min_x)
    end_int = int(max_x) + 1
    total_slots = end_int - start_int + 1
    if total_slots <= 0:
        return min_x, max_x, []

    coverage = [0] * total_slots

    for l in lines:
        lx0 = max(start_int, int(l.bbox.x0))
        lx1 = min(end_int, int(l.bbox.x1))
        for x in range(lx0, lx1 + 1):
            idx = x - start_int
            if 0 <= idx < total_slots:
                coverage[idx] += 1

    # Find contiguous intervals where coverage is 0 (or at most 1 outlier line)
    # Gutters must not lie on the extreme outer 12% margins of the content
    margin_threshold = 0.12 * content_width
    valid_gutter_min_x = min_x + margin_threshold
    valid_gutter_max_x = max_x - margin_threshold

    max_allowed_coverage = 0
    if len(lines) >= 30:
        # For large documents, allow at most 1 divider/outlier line
        max_allowed_coverage = 1

    candidate_gutters: List[Tuple[float, float]] = []
    in_gutter = False
    g_start = 0

    for x in range(start_int, end_int + 1):
        idx = x - start_int
        val = coverage[idx] if idx < total_slots else 999
        is_empty = (val <= max_allowed_coverage)

        if is_empty and not in_gutter:
            in_gutter = True
            g_start = x
        elif not is_empty and in_gutter:
            in_gutter = False
            g_end = x - 1
            # Check gutter bounds
            if g_end > g_start and (g_end - g_start) >= min_gutter_width:
                if g_start >= valid_gutter_min_x and g_end <= valid_gutter_max_x:
                    candidate_gutters.append((float(g_start), float(g_end)))

    if in_gutter:
        g_end = end_int
        if (g_end - g_start) >= min_gutter_width:
            if g_start >= valid_gutter_min_x and g_end <= valid_gutter_max_x:
                candidate_gutters.append((float(g_start), float(g_end)))

    # Filter out gutters that leave one side with almost no text
    verified_gutters: List[Tuple[float, float]] = []
    for gx0, gx1 in candidate_gutters:
        left_count = sum(1 for l in lines if l.bbox.x1 <= gx0 + 3.0)
        right_count = sum(1 for l in lines if l.bbox.x0 >= gx1 - 3.0)
        # Both columns must have at least 2 lines (or >= 10% of total lines)
        if left_count >= 2 and right_count >= 2:
            verified_gutters.append((gx0, gx1))

    return min_x, max_x, verified_gutters


def detect_page_columns(page: SpatialPage) -> ColumnLayout:
    """Analyze page geometry to determine column bounds, gutters, and header/footer bands."""
    lines = [l for l in page.all_lines if l.text.strip()]
    if not lines:
        return ColumnLayout(
            page_number=page.page_number,
            layout_type="single_column",
            num_columns=1,
            columns=[page.bbox],
            gutters=[],
        )

    page_h = page.height
    min_page_y = min(l.bbox.y0 for l in lines)
    max_page_y = max(l.bbox.y1 for l in lines)

    # 1. First test: Does the entire page have a continuous vertical gutter?
    full_min_x, full_max_x, full_gutters = _find_gutters_in_lines(lines)

    has_header = False
    header_cut_y: Optional[float] = None
    body_lines = lines
    active_gutters = full_gutters
    content_min_x = full_min_x
    content_max_x = full_max_x

    # 2. If no gutter across the full page, check if a top header band is obscuring the gutter
    if not full_gutters:
        # Check potential header cut points in the top 35% of the page
        candidate_cuts: List[float] = []
        sorted_by_y = sorted(lines, key=lambda l: l.bbox.y0)
        for i, l in enumerate(sorted_by_y):
            if l.bbox.y1 <= page_h * 0.35:
                # If there's a vertical gap >= 12.0 pt or next line is a section heading
                if i < len(sorted_by_y) - 1:
                    gap = sorted_by_y[i + 1].bbox.y0 - l.bbox.y1
                    if gap >= 10.0:
                        candidate_cuts.append(round((l.bbox.y1 + sorted_by_y[i + 1].bbox.y0) / 2.0, 1))

        # Test each candidate cut point
        for cut_y in candidate_cuts:
            lines_below = [l for l in lines if l.bbox.y0 >= cut_y]
            if len(lines_below) >= 4:
                b_min_x, b_max_x, b_gutters = _find_gutters_in_lines(lines_below)
                if b_gutters:
                    has_header = True
                    header_cut_y = cut_y
                    body_lines = lines_below
                    active_gutters = b_gutters
                    content_min_x = b_min_x
                    content_max_x = b_max_x
                    break

        # If still no multi-column gutter, check if page 1 has a clear top header gap (>= 22pt) before first section
        if not has_header and page.page_number == 1 and candidate_cuts:
            # Find largest gap in top 35% of page 1
            max_gap = 0.0
            best_cut = None
            sorted_by_y = sorted(lines, key=lambda l: l.bbox.y0)
            for i, l in enumerate(sorted_by_y):
                if l.bbox.y1 <= page_h * 0.35 and i < len(sorted_by_y) - 1:
                    gap = sorted_by_y[i + 1].bbox.y0 - l.bbox.y1
                    if gap >= 22.0 and gap > max_gap:
                        max_gap = gap
                        best_cut = round((l.bbox.y1 + sorted_by_y[i + 1].bbox.y0) / 2.0, 1)
            if best_cut is not None:
                has_header = True
                header_cut_y = best_cut
                body_lines = [l for l in lines if l.bbox.y0 >= best_cut]

    # 3. Check for footer band in bottom 10% of page
    has_footer = False
    footer_cut_y: Optional[float] = None
    footer_threshold = page_h * 0.90
    candidate_footer_lines = [l for l in lines if l.bbox.y0 >= footer_threshold]
    if candidate_footer_lines and active_gutters:
        # Check if any footer line spans across the gutter
        gx0, gx1 = active_gutters[0]
        if any(l.bbox.x0 < gx0 and l.bbox.x1 > gx1 for l in candidate_footer_lines):
            has_footer = True
            footer_cut_y = min(l.bbox.y0 for l in candidate_footer_lines)
            body_lines = [l for l in body_lines if l.bbox.y1 <= footer_cut_y]

    body_y0 = header_cut_y if (has_header and header_cut_y is not None) else min_page_y
    body_y1 = footer_cut_y if (has_footer and footer_cut_y is not None) else max_page_y

    # 4. Classify layout type based on detected gutters
    if not active_gutters:
        return ColumnLayout(
            page_number=page.page_number,
            layout_type="single_column",
            num_columns=1,
            columns=[
                BoundingBox(
                    x0=content_min_x,
                    y0=body_y0,
                    x1=content_max_x,
                    y1=body_y1,
                )
            ],
            gutters=[],
            has_header_band=has_header,
            header_boundary_y=header_cut_y,
            has_footer_band=has_footer,
            footer_boundary_y=footer_cut_y,
        )

    # Multi-column / 2-column / sidebar layout
    num_cols = len(active_gutters) + 1
    gutter_boxes: List[BoundingBox] = []
    column_boxes: List[BoundingBox] = []

    curr_x0 = content_min_x
    for gx0, gx1 in active_gutters:
        column_boxes.append(BoundingBox(x0=curr_x0, y0=body_y0, x1=gx0, y1=body_y1))
        gutter_boxes.append(BoundingBox(x0=gx0, y0=body_y0, x1=gx1, y1=body_y1))
        curr_x0 = gx1
    column_boxes.append(BoundingBox(x0=curr_x0, y0=body_y0, x1=content_max_x, y1=body_y1))

    layout_type = "multi_column"
    if num_cols == 2:
        col0_w = column_boxes[0].width
        col1_w = column_boxes[1].width
        total_w = col0_w + col1_w
        if total_w > 0:
            left_ratio = col0_w / total_w
            if left_ratio <= 0.38:
                layout_type = "left_sidebar"
            elif left_ratio >= 0.62:
                layout_type = "right_sidebar"
            else:
                layout_type = "two_column"
        else:
            layout_type = "two_column"

    return ColumnLayout(
        page_number=page.page_number,
        layout_type=layout_type,
        num_columns=num_cols,
        columns=column_boxes,
        gutters=gutter_boxes,
        has_header_band=has_header,
        header_boundary_y=header_cut_y,
        has_footer_band=has_footer,
        footer_boundary_y=footer_cut_y,
    )
