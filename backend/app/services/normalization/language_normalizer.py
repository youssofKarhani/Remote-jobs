"""Deterministic Language and CEFR Proficiency Normalizer.

Standardizes natural language names and maps proficiency descriptions
to canonical CEFR tiers (A1, A2, B1, B2, C1, C2, Native) while preserving raw_value.
"""

import re
from typing import Optional, Tuple

from app.schemas.semantic_cv import RawNormalizedValue, SemanticLanguage

LANGUAGE_MAP = {
    "english": "English", "englisch": "English",
    "german": "German", "deutsch": "German",
    "french": "French", "français": "French", "französisch": "French",
    "arabic": "Arabic", "arabisch": "Arabic",
    "spanish": "Spanish", "español": "Spanish", "spanisch": "Spanish",
    "italian": "Italian", "italiano": "Italian", "italienisch": "Italian",
    "russian": "Russian", "russisch": "Russian",
    "chinese": "Chinese", "mandarin": "Chinese",
    "japanese": "Japanese",
    "portuguese": "Portuguese",
}

CEFR_PATTERNS = [
    (r"\b(?:native|mother tongue|muttersprache|bilingual)\b", "Native"),
    (r"\b(?:c2|proficient|fluent \(c2\))\b", "C2"),
    (r"\b(?:c1|fluent|full professional|ielts)\b", "C1"),
    (r"\b(?:b2|working knowledge|professional working)\b", "B2"),
    (r"\b(?:b1|intermediate|conversational)\b", "B1"),
    (r"\b(?:a2|elementary|basic working)\b", "A2"),
    (r"\b(?:a1|beginner|basic)\b", "A1"),
]


def normalize_language_name(lang_raw: Optional[str]) -> Tuple[Optional[str], float]:
    """Normalize a language name string."""
    if not lang_raw or not lang_raw.strip():
        return None, 0.0

    cleaned = re.sub(r"[\(\)\[\]]", "", lang_raw).lower().strip()
    # Check direct match
    for k, canonical in LANGUAGE_MAP.items():
        if k in cleaned:
            return canonical, 1.0

    return lang_raw.strip().title(), 0.7


def normalize_proficiency_cefr(prof_raw: Optional[str]) -> Tuple[Optional[str], float]:
    """Normalize a language proficiency declaration to CEFR or Native standard."""
    if not prof_raw or not prof_raw.strip():
        return None, 0.0

    p = prof_raw.lower()
    for pattern, cefr in CEFR_PATTERNS:
        if re.search(pattern, p):
            return cefr, 1.0

    return prof_raw.strip(), 0.5


def normalize_language_entity(lang: SemanticLanguage) -> SemanticLanguage:
    """Normalize a SemanticLanguage entity in-place, preserving raw values."""
    if lang.language and lang.language.raw_value:
        norm_name, conf = normalize_language_name(lang.language.raw_value)
        lang.language.normalized_value = norm_name
        lang.language.confidence = conf

    if lang.proficiency and lang.proficiency.raw_value:
        norm_cefr, conf = normalize_proficiency_cefr(lang.proficiency.raw_value)
        lang.proficiency.normalized_value = norm_cefr
        lang.proficiency.confidence = conf
    elif lang.language and lang.language.raw_value:
        # Check if proficiency was embedded in the language string (e.g. "English (Fluent)")
        m = re.search(r"\((.*?)\)", lang.language.raw_value)
        if m:
            norm_cefr, conf = normalize_proficiency_cefr(m.group(1))
            if norm_cefr:
                lang.proficiency = RawNormalizedValue(
                    raw_value=m.group(1),
                    normalized_value=norm_cefr,
                    confidence=conf,
                )

    return lang
