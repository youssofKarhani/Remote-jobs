"""Deterministic Contact Information Normalizer.

Standardizes email, phone numbers, and profile URLs (LinkedIn, GitHub, Portfolio)
while strictly preserving verbatim text claims in raw_value (Rule 3 & 4).
Detects date ranges mistaken for phone numbers and malformed contact entries.
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse

from app.schemas.semantic_cv import RawNormalizedValue, SemanticPersonalInfo

# Pattern detecting date ranges mistakenly extracted as phone numbers
DATE_RANGE_PHONE_PATTERN = re.compile(
    r"^\s*(?:19\d\d|20\d\d)\s*[-–—/]\s*(?:19\d\d|20\d\d|present|heute|current|now)\s*$",
    re.IGNORECASE,
)

# Standard email regex: local-part @ domain . tld
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


def normalize_email_string(email_raw: Optional[str]) -> Tuple[Optional[str], float, str]:
    """Normalize an email address (lowercased, whitespace trimmed, mailto: stripped).

    Returns:
        (canonical_email, confidence, normalization_method)
    """
    if not email_raw or not email_raw.strip():
        return None, 0.0, "none"

    cleaned = email_raw.strip().lower()
    if cleaned.startswith("mailto:"):
        cleaned = cleaned[len("mailto:") :].strip()

    if EMAIL_REGEX.match(cleaned):
        return cleaned, 1.0, "standard_email_normalization"

    # Malformed email
    return None, 0.0, "malformed_email_rejected"


def normalize_phone_number(phone_raw: Optional[str]) -> Tuple[Optional[str], float, str]:
    """Normalize phone number to standardized spacing and clean international prefix.

    Detects and rejects date ranges mistaken for phone numbers (e.g. '2019 - 2022').

    Returns:
        (canonical_phone, confidence, normalization_method)
    """
    if not phone_raw or not phone_raw.strip():
        return None, 0.0, "none"

    raw = phone_raw.strip()

    # 1. Check if this is a date range mistaken for a phone number
    if DATE_RANGE_PHONE_PATTERN.match(raw):
        return None, 0.0, "date_range_mistaken_for_phone_rejected"

    # 2. Strip invalid surrounding characters except plus and digits
    cleaned = re.sub(r"[^\d\+\-\s\(\)\.]", "", raw)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Reject if too short (e.g. a lone 4-digit year like "2022")
    digits_only = re.sub(r"\D", "", cleaned)
    if len(digits_only) < 7:
        return None, 0.0, "insufficient_digits_rejected"

    # Standard international or local phone number format
    if re.match(r"^\+?\d[\d\s\-\(\)\.]{6,20}$", cleaned):
        return cleaned, 0.95, "standard_phone_normalization"

    return raw, 0.5, "unnormalized_phone_fallback"


def normalize_url(url_raw: Optional[str]) -> Tuple[Optional[str], float, str]:
    """Normalize a profile or website URL (enforcing https, stripping tracking params).

    Returns:
        (canonical_url, confidence, normalization_method)
    """
    if not url_raw or not url_raw.strip():
        return None, 0.0, "none"

    u = url_raw.strip()
    if " " in u or "\n" in u:
        return None, 0.0, "malformed_url_rejected"

    if not u.startswith("http://") and not u.startswith("https://"):
        u = "https://" + u

    try:
        parsed = urlparse(u)
        netloc = parsed.netloc.lower()
        if not netloc or "." not in netloc:
            return None, 0.0, "malformed_url_rejected"

        # Ensure www. on linkedin if omitted
        if netloc == "linkedin.com":
            netloc = "www.linkedin.com"

        # Rebuild without query params (strip UTM and referral tags)
        cleaned_url = urlunparse((
            parsed.scheme.lower(),
            netloc,
            parsed.path.rstrip("/"),
            "",  # params
            "",  # query
            "",  # fragment
        ))
        return cleaned_url, 1.0, "canonical_url_normalization"
    except Exception:
        return None, 0.0, "malformed_url_rejected"


def normalize_personal_info_entity(info: SemanticPersonalInfo) -> SemanticPersonalInfo:
    """Normalize candidate personal info fields in-place, preserving verbatim raw values."""
    if info.email and info.email.raw_value:
        norm_email, conf, method = normalize_email_string(info.email.raw_value)
        info.email.normalized_value = norm_email
        info.email.confidence = conf
        if not info.email.metadata:
            info.email.metadata = {}
        info.email.metadata["normalization_method"] = method
        info.email.metadata["normalization_confidence"] = conf

    if info.phone and info.phone.raw_value:
        norm_phone, conf, method = normalize_phone_number(info.phone.raw_value)
        info.phone.normalized_value = norm_phone
        info.phone.confidence = conf
        if not info.phone.metadata:
            info.phone.metadata = {}
        info.phone.metadata["normalization_method"] = method
        info.phone.metadata["normalization_confidence"] = conf

    for url_field in (info.linkedin_url, info.github_url, info.portfolio_url):
        if url_field and url_field.raw_value:
            norm_url, conf, method = normalize_url(url_field.raw_value)
            url_field.normalized_value = norm_url
            url_field.confidence = conf
            if not url_field.metadata:
                url_field.metadata = {}
            url_field.metadata["normalization_method"] = method
            url_field.metadata["normalization_confidence"] = conf

    return info
