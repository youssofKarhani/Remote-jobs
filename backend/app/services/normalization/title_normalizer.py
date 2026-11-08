"""Deterministic Job Title and Academic Degree Normalizer.

Standardizes common abbreviations, seniority prefixes, and degree formats
while strictly preserving raw text claims in raw_value.
"""

import re
from typing import Optional, Tuple

from app.schemas.semantic_cv import RawNormalizedValue

# Standard degree dictionary: pattern -> (Canonical Name, Level)
DEGREE_TAXONOMY = [
    (r"\b(?:b\.?sc\.?|bachelor of science|b\.?s\.?|bsc)\b", "Bachelor of Science", "bachelor"),
    (r"\b(?:b\.?a\.?|bachelor of arts|ba)\b", "Bachelor of Arts", "bachelor"),
    (r"\b(?:bachelor|b\.?eng\.?|bachelor of engineering)\b", "Bachelor of Engineering", "bachelor"),
    (r"\b(?:m\.?sc\.?|master of science|m\.?s\.?|msc)\b", "Master of Science", "master"),
    (r"\b(?:m\.?a\.?|master of arts|ma)\b", "Master of Arts", "master"),
    (r"\b(?:m\.?eng\.?|master of engineering)\b", "Master of Engineering", "master"),
    (r"\b(?:mba|master of business administration)\b", "Master of Business Administration", "master"),
    (r"\b(?:ph\.?d\.?|doctor of philosophy|phd|doctorate)\b", "Doctor of Philosophy", "doctorate"),
    (r"\b(?:associate degree|associate of science|a\.?s\.?)\b", "Associate Degree", "associate"),
]

# Seniority level markers
SENIORITY_MARKERS = [
    (r"\b(?:intern|internship|working student|werkstudent)\b", "Intern"),
    (r"\b(?:jr\.?|junior|entry level|associate)\b", "Junior"),
    (r"\b(?:mid|mid-level|intermediate)\b", "Mid-Level"),
    (r"\b(?:sr\.?|senior)\b", "Senior"),
    (r"\b(?:lead|team lead|tech lead)\b", "Lead"),
    (r"\b(?:staff)\b", "Staff"),
    (r"\b(?:principal)\b", "Principal"),
    (r"\b(?:head of|director|vp|vice president)\b", "Executive"),
]

# Title abbreviation expansion
TITLE_EXPANSIONS = [
    (r"\bsr(?:\.|\b)", "Senior"),
    (r"\bjr(?:\.|\b)", "Junior"),
    (r"\bdev\b", "Developer"),
    (r"\beng(?:\.|\b)", "Engineer"),
    (r"\bswe\b", "Software Engineer"),
    (r"\bml\b", "Machine Learning"),
    (r"\bai\b", "AI"),
    (r"\bqa\b", "Quality Assurance"),
]


def normalize_job_title(title_raw: Optional[str]) -> Tuple[Optional[str], Optional[str], float]:
    """Normalize a raw job title string.
    
    Returns:
        (canonical_title, seniority_level, confidence)
    """
    if not title_raw or not title_raw.strip():
        return None, None, 0.0

    t = title_raw.strip()
    
    # Detect seniority
    seniority = None
    for pattern, level in SENIORITY_MARKERS:
        if re.search(pattern, t, re.IGNORECASE):
            seniority = level
            break

    # Expand abbreviations
    normalized = t
    for pattern, replacement in TITLE_EXPANSIONS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # Clean redundant spaces
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized, seniority, 0.9 if seniority else 0.8


def normalize_degree(degree_raw: Optional[str]) -> Tuple[Optional[str], Optional[str], float]:
    """Normalize a raw academic degree string.
    
    Returns:
        (canonical_degree, degree_level, confidence)
    """
    if not degree_raw or not degree_raw.strip():
        return None, None, 0.0

    d = degree_raw.strip()
    for pattern, canonical_name, level in DEGREE_TAXONOMY:
        if re.search(pattern, d, re.IGNORECASE):
            return canonical_name, level, 1.0

    return d, None, 0.6


def normalize_raw_normalized_title(val: Optional[RawNormalizedValue]) -> Optional[RawNormalizedValue]:
    """Normalize a role title RawNormalizedValue in-place, preserving raw_value."""
    if not val or not val.raw_value:
        return val

    norm_title, seniority, conf = normalize_job_title(val.raw_value)
    val.normalized_value = norm_title
    val.confidence = conf
    if seniority:
        val.metadata["seniority"] = seniority
    return val


def normalize_raw_normalized_degree(val: Optional[RawNormalizedValue]) -> Optional[RawNormalizedValue]:
    """Normalize a degree RawNormalizedValue in-place, preserving raw_value."""
    if not val or not val.raw_value:
        return val

    norm_degree, level, conf = normalize_degree(val.raw_value)
    val.normalized_value = norm_degree
    val.confidence = conf
    if not val.metadata:
        val.metadata = {}
    if level:
        val.metadata["degree_level"] = level
    val.metadata["normalization_method"] = "academic_degree_canonicalization"
    val.metadata["normalization_confidence"] = conf
    return val


# Academic Institution Acronyms and Aliases
INSTITUTION_TAXONOMY = {
    "tu berlin": "Technical University of Berlin",
    "tub": "Technical University of Berlin",
    "tu munich": "Technical University of Munich",
    "tum": "Technical University of Munich",
    "lmu": "Ludwig Maximilian University of Munich",
    "lmu munich": "Ludwig Maximilian University of Munich",
    "mit": "Massachusetts Institute of Technology",
    "eth zurich": "ETH Zurich",
    "eth": "ETH Zurich",
    "epfl": "École Polytechnique Fédérale de Lausanne",
    "stanford": "Stanford University",
    "harvard": "Harvard University",
    "oxford": "University of Oxford",
    "cambridge": "University of Cambridge",
    "ucla": "University of California, Los Angeles",
    "uc berkeley": "University of California, Berkeley",
    "caltech": "California Institute of Technology",
}


def normalize_institution(institution_raw: Optional[str]) -> Tuple[Optional[str], float, str]:
    """Normalize a raw university or educational institution string.

    Returns:
        (canonical_institution, confidence, normalization_method)
    """
    if not institution_raw or not institution_raw.strip():
        return None, 0.0, "none"

    raw = institution_raw.strip()
    cleaned_lower = re.sub(r"[^\w\s]", "", raw.lower()).strip()

    if cleaned_lower in INSTITUTION_TAXONOMY:
        return INSTITUTION_TAXONOMY[cleaned_lower], 0.98, "known_academic_institution_alias"

    # Substring check for standard university patterns
    for alias, canonical in INSTITUTION_TAXONOMY.items():
        if alias in cleaned_lower.split():
            return canonical, 0.95, "known_academic_institution_alias"

    # Clean redundant punctuation and spaces
    normalized = re.sub(r"[,;:\.\-]+$", "", raw).strip()
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized, 0.85, "verbatim_cleaned"


def normalize_raw_normalized_institution(val: Optional[RawNormalizedValue]) -> Optional[RawNormalizedValue]:
    """Normalize an institution RawNormalizedValue in-place, preserving raw_value."""
    if not val or not val.raw_value:
        return val

    norm_inst, conf, method = normalize_institution(val.raw_value)
    val.normalized_value = norm_inst
    val.confidence = conf
    if not val.metadata:
        val.metadata = {}
    val.metadata["normalization_method"] = method
    val.metadata["normalization_confidence"] = conf
    return val

