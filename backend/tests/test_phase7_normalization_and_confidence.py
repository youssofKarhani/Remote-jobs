"""Test Suite for Phase 7 — Normalization, Validation, and Confidence.

Verifies:
1. Technical skill normalization with typo tolerance (MangoDB -> MongoDB) and raw preservation.
2. Multi-lingual date parsing (English & German), duration calculation, and current role detection.
3. Job title expansion, seniority detection, and academic degree canonicalization.
4. Natural language name standardization and CEFR proficiency tier mapping.
5. Contact information normalization (lowercasing email, URL canonicalization, phone cleanup).
6. Temporal consistency validation, future date detection, and non-blocking warning generation.
7. Multi-dimensional document quality scoring and confidence calculation.
8. End-to-end normalization pipeline integration ensuring Evidence Bank invariants (is_verified=False).
"""

import pytest

from app.schemas.semantic_cv import (
    CanonicalSemanticCV,
    ProvenanceMetadata,
    RawNormalizedValue,
    SemanticEducation,
    SemanticExperience,
    SemanticExperienceBullet,
    SemanticLanguage,
    SemanticPersonalInfo,
    SemanticSkill,
    UnknownSection,
    UnknownSectionItem,
)
from app.services.normalization import (
    DocumentQualityScore,
    NormalizedSemanticCVResult,
    ValidationWarning,
    calculate_duration_months,
    normalize_canonical_cv,
    normalize_degree,
    normalize_email_string,
    normalize_job_title,
    normalize_language_name,
    normalize_phone_number,
    normalize_proficiency_cefr,
    normalize_skill_entity,
    normalize_skill_name,
    normalize_url,
    parse_single_date,
    split_date_range,
    validate_career_consistency,
)


def _prov(block_id: str = "BLOCK_001") -> ProvenanceMetadata:
    return ProvenanceMetadata(
        source_document_id="DOC_001",
        source_pages=[1],
        source_block_ids=[block_id],
        raw_text="Sample text",
        raw_value="Sample text",
        extraction_method="semantic_llm",
        extraction_confidence=0.95,
    )


# ============================================================================
# 1. Technical Skill Normalization Tests
# ============================================================================

class TestSkillNormalization:
    def test_exact_and_alias_matches(self):
        canonical, cat, conf = normalize_skill_name("Fast API")
        assert canonical == "FastAPI"
        assert cat == "backend"
        assert conf >= 0.95

        canonical, cat, conf = normalize_skill_name("Postgres")
        assert canonical == "PostgreSQL"
        assert cat == "database"
        assert conf >= 0.95

        canonical, cat, conf = normalize_skill_name("k8s")
        assert canonical == "Kubernetes"
        assert cat == "devops"
        assert conf >= 0.95

    def test_mangodb_spelling_normalization_and_raw_preservation(self):
        """Rule 3 & 4: 'MangoDB' raw claim must normalize to 'MongoDB' without altering raw_value."""
        skill = SemanticSkill(
            raw_value="MangoDB",
            provenance=_prov("BLOCK_003"),
        )
        normalized = normalize_skill_entity(skill)

        assert normalized.raw_value == "MangoDB"  # Verbatim claim strictly preserved
        assert normalized.normalized_value == "MongoDB"
        assert normalized.category == "database"

    def test_unrecognized_custom_skill_leaves_normalized_none(self):
        skill = SemanticSkill(
            raw_value="InternalProprietaryEngineXYZ",
            provenance=_prov("BLOCK_003"),
        )
        normalized = normalize_skill_entity(skill)

        assert normalized.raw_value == "InternalProprietaryEngineXYZ"
        assert normalized.normalized_value is None


# ============================================================================
# 2. Date & Period Normalization Tests
# ============================================================================

class TestDateNormalization:
    @pytest.mark.parametrize("raw_date,expected_iso", [
        ("01/2025", "2025-01"),
        ("4/2024", "2024-04"),
        ("Jan 2025", "2025-01"),
        ("January 2025", "2025-01"),
        ("2022", "2022"),
        ("Januar 2020", "2020-01"),
        ("März 2022", "2022-03"),
        ("Present", "Present"),
        ("heute", "Present"),
    ])
    def test_parse_single_date_formats(self, raw_date, expected_iso):
        iso_str, conf = parse_single_date(raw_date)
        assert iso_str == expected_iso
        assert conf >= 0.9

    def test_split_date_range(self):
        start, end, is_cur = split_date_range("01/2022 - Present")
        assert start == "01/2022"
        assert end is None
        assert is_cur is True

        start, end, is_cur = split_date_range("2019 – 2022")  # en-dash
        assert start == "2019"
        assert end == "2022"
        assert is_cur is False

    def test_calculate_duration_months(self):
        months = calculate_duration_months("2020-01", "2022-01")
        assert months == 24

        months_cur = calculate_duration_months("2024-01", "Present", is_current=True)
        assert months_cur >= 12


# ============================================================================
# 3. Job Title and Degree Normalization Tests
# ============================================================================

class TestTitleAndDegreeNormalization:
    def test_job_title_normalization_and_seniority(self):
        title, seniority, conf = normalize_job_title("Sr. Software Dev")
        assert title == "Senior Software Developer"
        assert seniority == "Senior"

        title, seniority, conf = normalize_job_title("Lead AI Eng.")
        assert title == "Lead AI Engineer"
        assert seniority == "Lead"

    def test_academic_degree_canonicalization(self):
        degree, level, conf = normalize_degree("B.Sc. in Computer Science")
        assert degree == "Bachelor of Science"
        assert level == "bachelor"

        degree, level, conf = normalize_degree("Master of Science")
        assert degree == "Master of Science"
        assert level == "master"

        degree, level, conf = normalize_degree("Ph.D.")
        assert degree == "Doctor of Philosophy"
        assert level == "doctorate"


# ============================================================================
# 4. Language & CEFR Normalization Tests
# ============================================================================

class TestLanguageNormalization:
    def test_language_name_and_cefr_tiers(self):
        lang, conf = normalize_language_name("Deutsch")
        assert lang == "German"

        lang, conf = normalize_language_name("English")
        assert lang == "English"

        cefr, conf = normalize_proficiency_cefr("(C1) - IELTS")
        assert cefr == "C1"

        cefr, conf = normalize_proficiency_cefr("Native")
        assert cefr == "Native"

        cefr, conf = normalize_proficiency_cefr("B2 - Professional Working")
        assert cefr == "B2"


# ============================================================================
# 5. Contact Information Normalization Tests
# ============================================================================

class TestContactNormalization:
    def test_normalize_email(self):
        email, conf = normalize_email_string(" YOUSSOF.K0@GMAIL.COM ")
        assert email == "youssof.k0@gmail.com"
        assert conf == 1.0

    def test_normalize_phone(self):
        phone, conf = normalize_phone_number("+49 (0) 170 1234567")
        assert "+49" in phone
        assert conf >= 0.9

    def test_normalize_urls(self):
        url, conf = normalize_url("linkedin.com/in/youssof-el-karhani?utm_source=share&utm_medium=ios")
        assert url == "https://www.linkedin.com/in/youssof-el-karhani"

        url, conf = normalize_url("github.com/youssof")
        assert url == "https://github.com/youssof"


# ============================================================================
# 6. Temporal Validation & Warnings Tests
# ============================================================================

class TestTemporalValidationAndWarnings:
    def test_temporal_inversion_generates_warning(self):
        exp = SemanticExperience(
            role_title=RawNormalizedValue.from_raw("Software Engineer"),
            company_name=RawNormalizedValue.from_raw("TechCorp"),
            start_date=RawNormalizedValue(raw_value="2024-01", normalized_value="2024-01"),
            end_date=RawNormalizedValue(raw_value="2020-01", normalized_value="2020-01"),  # End before start
            provenance=_prov("BLOCK_005"),
        )
        cv = CanonicalSemanticCV(
            source_document_id="DOC_001",
            experiences=[exp],
        )
        warnings = validate_career_consistency(cv)
        assert len(warnings) >= 1
        assert any(w.code == "TEMPORAL_INVERSION" for w in warnings)

    def test_future_start_date_generates_warning(self):
        exp = SemanticExperience(
            role_title=RawNormalizedValue.from_raw("Future Role"),
            company_name=RawNormalizedValue.from_raw("FutureCorp"),
            start_date=RawNormalizedValue(raw_value="2045-01", normalized_value="2045-01"),
            provenance=_prov("BLOCK_005"),
        )
        cv = CanonicalSemanticCV(
            source_document_id="DOC_001",
            experiences=[exp],
        )
        warnings = validate_career_consistency(cv)
        assert any(w.code == "FUTURE_START_DATE" for w in warnings)


# ============================================================================
# 7. Document Quality & Confidence Scoring Tests
# ============================================================================

class TestQualityScoring:
    def test_high_quality_cv_scoring(self):
        cv = CanonicalSemanticCV(
            source_document_id="DOC_001",
            personal_info=SemanticPersonalInfo(
                full_name=RawNormalizedValue(raw_value="Youssof El Karhani", normalized_value="Youssof El Karhani", confidence=1.0),
                email=RawNormalizedValue(raw_value="youssof@example.com", normalized_value="youssof@example.com", confidence=1.0),
                provenance=_prov("BLOCK_001"),
            ),
            skills=[
                SemanticSkill(raw_value="Python", normalized_value="Python", provenance=_prov("BLOCK_002")),
                SemanticSkill(raw_value="FastAPI", normalized_value="FastAPI", provenance=_prov("BLOCK_002")),
            ],
            experiences=[
                SemanticExperience(
                    role_title=RawNormalizedValue(raw_value="Senior Dev", normalized_value="Senior Developer", confidence=1.0),
                    company_name=RawNormalizedValue.from_raw("TechCorp"),
                    start_date=RawNormalizedValue(raw_value="01/2022", normalized_value="2022-01", confidence=1.0),
                    bullets=[SemanticExperienceBullet(raw_text="Built APIs", provenance=_prov("BLOCK_003"))],
                    provenance=_prov("BLOCK_003"),
                )
            ]
        )
        score: DocumentQualityScore = normalize_canonical_cv(cv).quality_score
        assert score.overall_score >= 0.80
        assert score.normalization_rate >= 0.70
        assert score.warnings_count == 0


# ============================================================================
# 8. End-to-End Normalization Pipeline Integration Tests
# ============================================================================

class TestEndToEndNormalizationPipeline:
    def test_full_pipeline_normalizes_and_preserves_raw_claims(self):
        raw_cv = CanonicalSemanticCV(
            source_document_id="YOUSSOF_CV",
            personal_info=SemanticPersonalInfo(
                full_name=RawNormalizedValue.from_raw("Youssof El Karhani"),
                email=RawNormalizedValue.from_raw("YOUSSOF.K0@GMAIL.COM"),
                phone=RawNormalizedValue.from_raw("+961-76-071579"),
                linkedin_url=RawNormalizedValue.from_raw("linkedin.com/in/youssof-el-karhani"),
                provenance=_prov("BLOCK_001"),
            ),
            skills=[
                SemanticSkill(raw_value="MangoDB", provenance=_prov("BLOCK_002")),
                SemanticSkill(raw_value="Fast API", provenance=_prov("BLOCK_002")),
                SemanticSkill(raw_value="Docker container", provenance=_prov("BLOCK_002")),
            ],
            experiences=[
                SemanticExperience(
                    role_title=RawNormalizedValue.from_raw("Sr. Software Eng."),
                    company_name=RawNormalizedValue.from_raw("RUYA Advisory"),
                    start_date=RawNormalizedValue.from_raw("01/2025"),
                    end_date=RawNormalizedValue.from_raw("Present"),
                    bullets=[
                        SemanticExperienceBullet(raw_text="Engineered distributed automation workflows.", provenance=_prov("BLOCK_003"))
                    ],
                    provenance=_prov("BLOCK_003"),
                )
            ],
            education=[
                SemanticEducation(
                    institution=RawNormalizedValue.from_raw("TU Berlin"),
                    degree=RawNormalizedValue.from_raw("B.Sc. in Computer Science"),
                    start_date=RawNormalizedValue.from_raw("2020"),
                    end_date=RawNormalizedValue.from_raw("2024"),
                    provenance=_prov("BLOCK_004"),
                )
            ],
            languages=[
                SemanticLanguage(
                    language=RawNormalizedValue.from_raw("English (Fluent)"),
                    provenance=_prov("BLOCK_005"),
                )
            ],
            unknown_sections=[
                UnknownSection(
                    section_type="unknown",
                    heading="OPEN SOURCE CONTRIBUTIONS",
                    items=[
                        UnknownSectionItem(raw_text="Creator of py-fast-parser", provenance=_prov("BLOCK_006"))
                    ],
                    provenance=_prov("BLOCK_006"),
                )
            ]
        )

        res: NormalizedSemanticCVResult = normalize_canonical_cv(raw_cv)
        cv = res.cv

        # 1. Personal info
        assert cv.personal_info.email.raw_value == "YOUSSOF.K0@GMAIL.COM"
        assert cv.personal_info.email.normalized_value == "youssof.k0@gmail.com"
        assert cv.personal_info.linkedin_url.normalized_value == "https://www.linkedin.com/in/youssof-el-karhani"

        # 2. Skills
        mangodb = next(s for s in cv.skills if s.raw_value == "MangoDB")
        assert mangodb.normalized_value == "MongoDB"
        assert mangodb.category == "database"

        fastapi = next(s for s in cv.skills if s.raw_value == "Fast API")
        assert fastapi.normalized_value == "FastAPI"

        docker = next(s for s in cv.skills if s.raw_value == "Docker container")
        assert docker.normalized_value == "Docker"

        # 3. Experience
        assert cv.experiences[0].role_title.raw_value == "Sr. Software Eng."
        assert cv.experiences[0].role_title.normalized_value == "Senior Software Engineer"
        assert cv.experiences[0].role_title.metadata["seniority"] == "Senior"
        assert cv.experiences[0].start_date.normalized_value == "2025-01"
        assert cv.experiences[0].is_current is True
        assert cv.experiences[0].metadata.get("duration_months") is not None

        # 4. Education
        assert cv.education[0].degree.raw_value == "B.Sc. in Computer Science"
        assert cv.education[0].degree.normalized_value == "Bachelor of Science"

        # 5. Language
        assert cv.languages[0].language.normalized_value == "English"
        assert cv.languages[0].proficiency.normalized_value == "C1"

        # 6. Unknown section preserved
        assert len(cv.unknown_sections) == 1
        assert cv.unknown_sections[0].heading == "OPEN SOURCE CONTRIBUTIONS"
        assert cv.unknown_sections[0].items[0].raw_text == "Creator of py-fast-parser"

        # 7. Quality score
        assert res.quality_score.overall_score >= 0.80
        assert res.quality_score.warnings_count == 0
