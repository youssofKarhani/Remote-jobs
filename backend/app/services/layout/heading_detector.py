"""Deterministic Heading Candidate Detector.

Uses typography, geometry, vertical isolation, casing, and section keyword matching
to identify section headings (Level 1) and subheadings (Level 2) without an LLM.
"""

import re
from typing import List, Optional, Tuple
from app.schemas.spatial import BoundingBox, SpatialLine, SpatialPage
from app.schemas.layout import HeadingCandidate

# Canonical Section Heading Regexes (Level 1)
PRIMARY_SECTION_PATTERNS = [
    re.compile(r"^(?:work\s+)?experience|employment(?:\s+history)?|career(?:\s+history)?|professional\s+experience$", re.I),
    re.compile(r"^education(?:al\s+background)?|academic\s+background|qualifications$", re.I),
    re.compile(r"^(?:technical\s+|core\s+)?skills(?:\s*(&|and|\+)\s*(?:tools|technologies|competencies))?|technologies|expertise|competencies$", re.I),
    re.compile(r"^languages?(?:\s+spoken)?|spoken\s+languages?$", re.I),
    re.compile(r"^(?:courses\s*(&|and|\+)\s*)?certifications?|certificates?|licenses(?:\s*(&|and|\+)\s*certifications?)?|courses(?:\s*(&|and|\+)\s*training)?$", re.I),
    re.compile(r"^(?:key\s+|selected\s+|personal\s+)?projects?|portfolio$", re.I),
    re.compile(r"^contact(?:\s+information|\s+details)?|personal\s+details?$", re.I),
    re.compile(r"^(?:professional\s+)?summary|profile|about\s+me|career\s+objective|objective$", re.I),
    re.compile(r"^publications?|patents?|awards?(?:\s*(&|and|\+)\s*honors?)?|references|volunteer(?:\s+experience)?|interests?|hobbies$", re.I),
]

# Bullet point indicators that disqualify a line from being a heading
BULLET_PREFIX_REGEX = re.compile(r"^[\u2022\u25cf\u25cb\u25aa\u25fe\u2013\u2014\-\*\+]\s*|^\d+[\.\)]\s*|^[a-z][\.\)]\s*", re.I)


def _clean_heading_text(text: str) -> str:
    """Normalize heading text by stripping extra punctuation and whitespace."""
    cleaned = text.strip()
    cleaned = re.sub(r"[:\-_—\|&\+]+$", "", cleaned).strip()
    return cleaned


def _is_bullet_line(line: SpatialLine) -> bool:
    """Return True if line begins with a bullet point or list marker."""
    text = line.text.strip()
    return bool(BULLET_PREFIX_REGEX.match(text))


def _calculate_median_body_font_size(lines: List[SpatialLine]) -> float:
    """Calculate median font size for body text on the page."""
    sizes: List[float] = []
    for l in lines:
        if l.font_size and len(l.text.strip()) > 15:
            sizes.append(l.font_size)
    if not sizes:
        # Fallback to all sizes
        sizes = [l.font_size for l in lines if l.font_size]
    if not sizes:
        return 10.0
    sizes.sort()
    mid = len(sizes) // 2
    if len(sizes) % 2 == 1:
        return sizes[mid]
    return (sizes[mid - 1] + sizes[mid]) / 2.0


def _matches_primary_section(text: str) -> bool:
    """Check if normalized text matches known primary CV section headings."""
    normalized = _clean_heading_text(text)
    # Also handle ampersand variations e.g. "Courses Certifications" -> "Courses & Certifications"
    normalized_variants = [
        normalized,
        re.sub(r"\s+", " ", normalized),
        re.sub(r"(\w+)\s+(\w+)", r"\1 & \2", normalized),
    ]
    for variant in normalized_variants:
        for pat in PRIMARY_SECTION_PATTERNS:
            if pat.match(variant):
                return True
    return False


def detect_heading_candidates(page: SpatialPage) -> List[HeadingCandidate]:
    """Detect section heading candidates on a page using deterministic typographic and layout signals."""
    lines = page.all_lines
    if not lines:
        return []

    # Filter out empty or bullet lines for heading evaluation
    sorted_lines = sorted(lines, key=lambda l: (l.bbox.y0, l.bbox.x0))
    median_font = _calculate_median_body_font_size(sorted_lines)

    candidates: List[HeadingCandidate] = []
    skip_indices = set()

    for i, line in enumerate(sorted_lines):
        if i in skip_indices:
            continue

        text = line.text.strip()
        if not text or len(text) < 2:
            continue

        # Disqualify bullets, emails, URLs, long sentences
        if _is_bullet_line(line):
            continue
        if "@" in text or "http" in text.lower() or "www." in text.lower():
            continue
        words = text.split()
        if len(words) > 7:
            continue
        # Disqualify lines with trailing sentence periods (unless it's just abbreviations)
        if text.endswith(".") and not text.endswith("..") and len(words) > 3:
            continue

        reasons: List[str] = []

        # Vertical isolation calculation
        gap_before = 999.0
        if i > 0:
            gap_before = round(line.bbox.y0 - sorted_lines[i - 1].bbox.y1, 2)
        gap_after = 999.0
        if i < len(sorted_lines) - 1:
            gap_after = round(sorted_lines[i + 1].bbox.y0 - line.bbox.y1, 2)

        has_isolation = gap_before >= 8.0
        if has_isolation:
            reasons.append(f"vertical_gap_before_{gap_before:.1f}pt")

        font_size = line.font_size or median_font
        is_larger_font = font_size >= median_font * 1.12 or font_size >= median_font + 1.0
        if is_larger_font:
            reasons.append(f"larger_font_{font_size:.1f}pt_vs_median_{median_font:.1f}pt")

        bold_words_count = sum(1 for w in line.words if w.is_bold)
        is_predominantly_bold = line.is_bold and (bold_words_count >= len(line.words) * 0.6)
        if is_predominantly_bold:
            reasons.append("bold_typography")

        is_all_caps = text.isupper() and len(text) > 3
        if is_all_caps:
            reasons.append("uppercase_casing")

        # Check multi-line heading combination (e.g. "Courses &" \n "Certifications")
        combined_text = text
        combined_raw = line.text
        combined_bbox = line.bbox
        combined_line_ids = [line.line_id]
        if i < len(sorted_lines) - 1:
            next_l = sorted_lines[i + 1]
            next_t = next_l.text.strip()
            is_vertically_below = next_l.bbox.y0 >= (line.bbox.y0 + 4.0)
            is_horizontally_aligned = abs(next_l.bbox.x0 - line.bbox.x0) < 45.0
            has_no_horizontal_gap = line.bbox.horizontal_distance_to(next_l.bbox) == 0.0

            if (
                gap_after <= 6.0
                and is_vertically_below
                and is_horizontally_aligned
                and has_no_horizontal_gap
                and not _is_bullet_line(next_l)
                and "@" not in next_t
                and "http" not in next_t.lower()
                and "www." not in next_t.lower()
                and (next_l.is_bold == line.is_bold or (next_l.font_size and abs(next_l.font_size - font_size) < 1.0))
            ):
                candidate_multi = f"{text} {next_t}"
                if _matches_primary_section(candidate_multi) or (
                    (is_predominantly_bold or is_larger_font) and len(candidate_multi.split()) <= 6
                ):
                    combined_text = candidate_multi
                    combined_raw = f"{line.text} {next_l.text}"
                    combined_bbox = BoundingBox(
                        x0=min(line.bbox.x0, next_l.bbox.x0),
                        y0=min(line.bbox.y0, next_l.bbox.y0),
                        x1=max(line.bbox.x1, next_l.bbox.x1),
                        y1=max(line.bbox.y1, next_l.bbox.y1),
                    )
                    combined_line_ids.append(next_l.line_id)
                    reasons.append("multi_line_heading_merged")
                    skip_indices.add(i + 1)

        is_primary_kw = _matches_primary_section(combined_text) or _matches_primary_section(text)
        if is_primary_kw:
            reasons.append("matches_primary_section_keyword")

        # Top of page 1 name/title is document header, not a section heading
        if page.page_number == 1 and line.bbox.y0 < 120.0 and not is_primary_kw:
            continue

        # Classification decision
        confidence = 0.0
        heading_level = 1

        if is_primary_kw:
            confidence = 0.98
            heading_level = 1
        elif (is_larger_font or is_all_caps) and is_predominantly_bold and has_isolation:
            confidence = 0.88
            heading_level = 1
        elif is_larger_font and (is_predominantly_bold or has_isolation):
            confidence = 0.80
            heading_level = 1
        elif is_predominantly_bold and has_isolation and len(words) <= 5:
            # Could be Level 2 subheading (e.g. company/job title or custom section)
            confidence = 0.72
            heading_level = 2
            reasons.append("subheading_level_2")
        elif is_all_caps and has_isolation and len(words) <= 4:
            confidence = 0.70
            heading_level = 1

        if confidence >= 0.70:
            candidates.append(
                HeadingCandidate(
                    text=_clean_heading_text(combined_text),
                    raw_text=combined_raw,
                    page=page.page_number,
                    bbox=combined_bbox,
                    confidence=confidence,
                    heading_level=heading_level,
                    font_size=font_size,
                    is_bold=is_predominantly_bold,
                    source_line_ids=combined_line_ids,
                    detection_reasons=reasons,
                )
            )

    return candidates
