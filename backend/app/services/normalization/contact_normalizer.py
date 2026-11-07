"""Deterministic Contact Information Normalizer.

Standardizes email, phone numbers, and profile URLs (LinkedIn, GitHub, Portfolio)
while strictly preserving verbatim text claims in raw_value.
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse

from app.schemas.semantic_cv import RawNormalizedValue, SemanticPersonalInfo


def normalize_email_string(email_raw: Optional[str]) -> Tuple[Optional[str], float]:
    """Normalize an email address (lowercased, whitespace trimmed)."""
    if not email_raw or not email_raw.strip():
        return None, 0.0

    cleaned = email_raw.strip().lower()
    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", cleaned):
        return cleaned, 1.0
    return cleaned, 0.5


def normalize_phone_number(phone_raw: Optional[str]) -> Tuple[Optional[str], float]:
    """Normalize phone number to standardized spacing and clean international prefix."""
    if not phone_raw or not phone_raw.strip():
        return None, 0.0

    raw = phone_raw.strip()
    # Strip invalid surrounding characters
    cleaned = re.sub(r"[^\d\+\-\s\(\)\.]", "", raw)
    # Collapse multi-spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # If it starts with + or valid digits
    if re.match(r"^\+?\d[\d\s\-\(\)\.]{6,20}$", cleaned):
        return cleaned, 0.95

    return raw, 0.5


def normalize_url(url_raw: Optional[str]) -> Tuple[Optional[str], float]:
    """Normalize a profile or website URL (enforcing https, stripping tracking params)."""
    if not url_raw or not url_raw.strip():
        return None, 0.0

    u = url_raw.strip()
    if not u.startswith("http://") and not u.startswith("https://"):
        u = "https://" + u

    try:
        parsed = urlparse(u)
        netloc = parsed.netloc.lower()
        # Ensure www. on linkedin if omitted
        if netloc == "linkedin.com":
            netloc = "www.linkedin.com"
        
        # Rebuild without query params (strip UTM tracking tags)
        cleaned_url = urlunparse((
            parsed.scheme.lower(),
            netloc,
            parsed.path.rstrip("/"),
            "",  # params
            "",  # query
            "",  # fragment
        ))
        return cleaned_url, 1.0
    except Exception:
        return u, 0.5


def normalize_personal_info_entity(info: SemanticPersonalInfo) -> SemanticPersonalInfo:
    """Normalize candidate personal info fields in-place, preserving raw values."""
    if info.email and info.email.raw_value:
        norm_email, conf = normalize_email_string(info.email.raw_value)
        info.email.normalized_value = norm_email
        info.email.confidence = conf

    if info.phone and info.phone.raw_value:
        norm_phone, conf = normalize_phone_number(info.phone.raw_value)
        info.phone.normalized_value = norm_phone
        info.phone.confidence = conf

    if info.linkedin_url and info.linkedin_url.raw_value:
        norm_url, conf = normalize_url(info.linkedin_url.raw_value)
        info.linkedin_url.normalized_value = norm_url
        info.linkedin_url.confidence = conf

    if info.github_url and info.github_url.raw_value:
        norm_url, conf = normalize_url(info.github_url.raw_value)
        info.github_url.normalized_value = norm_url
        info.github_url.confidence = conf

    if info.portfolio_url and info.portfolio_url.raw_value:
        norm_url, conf = normalize_url(info.portfolio_url.raw_value)
        info.portfolio_url.normalized_value = norm_url
        info.portfolio_url.confidence = conf

    return info
