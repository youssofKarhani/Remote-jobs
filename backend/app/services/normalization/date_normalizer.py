"""Deterministic Date and Employment Period Normalizer.

Standardizes raw career and academic date strings into ISO format (YYYY-MM or YYYY),
computes duration, and detects ongoing/current roles.
Preserves raw date text claims in raw_value (Rule 3 & 4).
"""

from datetime import datetime
import re
from typing import Optional, Tuple

from app.schemas.semantic_cv import RawNormalizedValue

# Multi-lingual month mapping (English & German)
MONTH_MAPPING = {
    "jan": "01", "january": "01", "januar": "01",
    "feb": "02", "february": "02", "februar": "02",
    "mar": "03", "march": "03", "märz": "03", "maerz": "03",
    "apr": "04", "april": "04",
    "may": "05", "mai": "05",
    "jun": "06", "june": "06", "juni": "06",
    "jul": "07", "july": "07", "juli": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09", "sept": "09",
    "oct": "10", "october": "10", "oktober": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12", "dezember": "12", "dez": "12",
}

CURRENT_MARKERS = {
    "present", "current", "now", "ongoing", "heute", "aktuell", "gegenwart", "bis heute", "to present"
}


def is_current_period(text: Optional[str]) -> bool:
    """Return True if text signifies an ongoing/current role."""
    if not text:
        return False
    t = text.lower().strip()
    return any(marker in t for marker in CURRENT_MARKERS)


def parse_single_date(raw_date: Optional[str]) -> Tuple[Optional[str], float]:
    """Parse a single date expression into ISO format (YYYY-MM or YYYY).
    
    Returns:
        (iso_string, confidence)
    """
    if not raw_date or not raw_date.strip():
        return None, 0.0

    t = raw_date.strip()
    if is_current_period(t):
        return "Present", 1.0

    # 1. MM/YYYY or M/YYYY (e.g. 01/2025, 4/2024)
    m = re.match(r"^(\d{1,2})[/\.-](\d{4})$", t)
    if m:
        month = int(m.group(1))
        year = int(m.group(2))
        if 1 <= month <= 12 and 1950 <= year <= 2050:
            return f"{year:04d}-{month:02d}", 1.0

    # 2. Month Name + Year (e.g. "Jan 2025", "January 2025", "März 2022")
    m = re.match(r"^([A-Za-zÄÖÜäöü]+)[,\s]+(\d{4})$", t)
    if m:
        month_name = m.group(1).lower()
        year = int(m.group(2))
        if month_name in MONTH_MAPPING and 1950 <= year <= 2050:
            return f"{year:04d}-{MONTH_MAPPING[month_name]}", 1.0

    # 3. YYYY-MM (e.g. 2024-04)
    m = re.match(r"^(\d{4})-(\d{1,2})$", t)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        if 1 <= month <= 12 and 1950 <= year <= 2050:
            return f"{year:04d}-{month:02d}", 1.0

    # 4. Standalone Year (e.g. "2020", "2024")
    m = re.match(r"^(\d{4})$", t)
    if m:
        year = int(m.group(1))
        if 1950 <= year <= 2050:
            return f"{year:04d}", 0.9

    return None, 0.4


def split_date_range(raw_range: str) -> Tuple[Optional[str], Optional[str], bool]:
    """Split a date range string like '01/2022 - Present' or '2019 – 2022'.
    
    Returns:
        (raw_start, raw_end, is_current)
    """
    if not raw_range:
        return None, None, False

    # Normalize dashes and separators
    cleaned = re.sub(r"[\u2013\u2014\u2212]", "-", raw_range)
    parts = re.split(r"\s*(?:-|to|bis)\s*", cleaned, maxsplit=1)

    if len(parts) == 2:
        start_raw = parts[0].strip()
        end_raw = parts[1].strip()
        is_cur = is_current_period(end_raw)
        return start_raw, (None if is_cur else end_raw), is_cur

    if len(parts) == 1:
        if is_current_period(parts[0]):
            return None, None, True
        return parts[0].strip(), None, False

    return None, None, False


def normalize_raw_normalized_date(value: Optional[RawNormalizedValue]) -> Optional[RawNormalizedValue]:
    """Normalize a RawNormalizedValue date in-place, preserving raw_value."""
    if not value or not value.raw_value:
        return value

    iso_str, conf = parse_single_date(value.raw_value)
    if iso_str:
        value.normalized_value = iso_str
        value.confidence = conf
    return value


def calculate_duration_months(start_iso: Optional[str], end_iso: Optional[str], is_current: bool = False) -> Optional[int]:
    """Calculate career duration in months between start and end ISO dates."""
    if not start_iso:
        return None

    def _parse_iso(iso_str: str) -> Optional[Tuple[int, int]]:
        parts = iso_str.split("-")
        try:
            year = int(parts[0])
            month = int(parts[1]) if len(parts) > 1 else 1
            return year, month
        except ValueError:
            return None

    start_ym = _parse_iso(start_iso)
    if not start_ym:
        return None

    if is_current or end_iso == "Present" or not end_iso:
        now = datetime.now()
        end_ym = (now.year, now.month)
    else:
        end_ym = _parse_iso(end_iso)
        if not end_ym:
            return None

    s_year, s_month = start_ym
    e_year, e_month = end_ym

    diff = (e_year - s_year) * 12 + (e_month - s_month)
    return max(0, diff)
