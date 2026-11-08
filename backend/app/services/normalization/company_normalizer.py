"""Deterministic Company and Organization Name Normalizer.

Cleans common legal entity designations (Inc., LLC, GmbH, AG, Ltd., Corp.)
and trailing punctuation while strictly preserving verbatim raw text claims (Rule 3 & 4).
"""

import re
from typing import Optional, Tuple

from app.schemas.semantic_cv import RawNormalizedValue

# Common legal corporate designations (case-insensitive, bounded words)
LEGAL_ENTITY_PATTERNS = [
    r",?\s*\b(?:inc(?:\.|\b)|incorporated)\b",
    r",?\s*\b(?:llc|l\.l\.c\.)\b",
    r",?\s*\b(?:gmbh\s*&\s*co\.?\s*kg|gmbh)\b",
    r",?\s*\b(?:ag|aktiengesellschaft)\b",
    r",?\s*\b(?:se|societas\s+europaea)\b",
    r",?\s*\b(?:ltd(?:\.|\b)|limited)\b",
    r",?\s*\b(?:corp(?:\.|\b)|corporation)\b",
    r",?\s*\b(?:co(?:\.|\b)|company)\b",
    r",?\s*\b(?:plc|public\s+limited\s+company)\b",
    r",?\s*\b(?:ug\s*\(haftungsbeschränkt\)|ug)\b",
    r",?\s*\b(?:s\.a\.?|s\.r\.l\.?|s\.a\.s\.?|bv|nv)\b",
]

# Canonical enterprise mappings
ENTERPRISE_CANONICAL = {
    "google": "Google",
    "alphabet": "Google",
    "meta": "Meta",
    "facebook": "Meta",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "aws": "Amazon Web Services",
    "apple": "Apple",
    "ibm": "IBM",
    "siemens": "Siemens",
    "sap": "SAP",
    "bmw": "BMW Group",
}


def normalize_company_name(company_raw: Optional[str]) -> Tuple[Optional[str], float, str]:
    """Normalize a raw company / organization name string.

    Returns:
        (canonical_name, confidence, normalization_method)
    """
    if not company_raw or not company_raw.strip():
        return None, 0.0, "none"

    raw = company_raw.strip()

    # 1. Check known enterprise aliases
    cleaned_lower = re.sub(r"[^\w\s]", "", raw.lower()).strip()
    if cleaned_lower in ENTERPRISE_CANONICAL:
        return ENTERPRISE_CANONICAL[cleaned_lower], 1.0, "known_enterprise_alias"

    # 2. Strip legal entity designations
    normalized = raw
    for pat in LEGAL_ENTITY_PATTERNS:
        normalized = re.sub(pat, "", normalized, flags=re.IGNORECASE)

    # 3. Clean trailing punctuation and redundant whitespace
    normalized = re.sub(r"[,;:\.\-]+$", "", normalized).strip()
    normalized = re.sub(r"\s+", " ", normalized).strip()

    if not normalized:
        return raw, 0.6, "raw_fallback"

    if normalized != raw:
        return normalized, 0.95, "legal_entity_normalization"

    return normalized, 0.90, "exact_verbatim"


def normalize_raw_normalized_company(val: Optional[RawNormalizedValue]) -> Optional[RawNormalizedValue]:
    """Normalize a company name RawNormalizedValue in-place, preserving raw_value."""
    if not val or not val.raw_value:
        return val

    norm_company, conf, method = normalize_company_name(val.raw_value)
    val.normalized_value = norm_company
    val.confidence = conf
    if not val.metadata:
        val.metadata = {}
    val.metadata["normalization_method"] = method
    val.metadata["normalization_confidence"] = conf
    return val
