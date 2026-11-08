"""Test Suite for Phase 7 — Normalization, Validation, and Confidence (Prompt 9).

Verifies all requirements:
1. Normalized technology aliases & typo tolerance (MangoDB -> MongoDB, Fast API -> FastAPI).
2. Raw value preservation (raw_value remains verbatim; normalized_value is distinct).
3. Invalid date ranges (start date after end date -> TEMPORAL_INVERSION warning).
4. Duplicate records (duplicate skills, certifications, projects; deduplication with provenance merging).
5. Missing provenance detection (empty source_block_ids or missing ProvenanceMetadata).
6. Malformed contact information:
   - Malformed email -> MALFORMED_EMAIL warning
   - Date ranges mistaken for phone numbers (e.g. "2019-2022") -> DATE_RANGE_AS_PHONE warning
   - Malformed URLs -> MALFORMED_URL warning
7. Unsupported inferred skill rejection (FastAPI must NOT synthesize a Python skill claim).
8. Company & Academic Institution normalization (legal suffix stripping, institution alias expansion).
9. Multi-signal confidence breakdown (extraction quality, layout, semantic, consistency, validation outcome).
10. Invariant: Confidence is never presented as verification (is_verified = False).
"""

import pytest

from app.schemas.semantic_cv import (
    CanonicalSemanticCV,
    ProvenanceMetadata,
    RawNormalizedValue,
    SemanticCertification,
    SemanticEducation,
    SemanticExperience,
    SemanticExperienceBullet,
    SemanticLanguage,
    SemanticPersonalInfo,
    SemanticProject,
    SemanticSkill,
    UnknownSection,
    UnknownSectionItem,
)
from app.services.normalization import (
    DocumentQualityScore,
    NormalizedSemanticCVResult,
    ValidationWarning,
    calculate_duration_months,
    deduplicate_cv_records,
    normalize_canonical_cv,
    normalize_company_name,
    normalize_degree,
    normalize_email_string,
    normalize_institution,
    normalize_job_title,
    normalize_language_name,
    normalize_personal_info_entity,
    normalize_phone_number,
    normalize_proficiency_cefr,
    normalize_raw_normalized_company,
    normalize_raw_normalized_date,
    normalize_raw_normalized_degree,
    normalize_raw_normalized_institution,
    normalize_raw_normalized_title,
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
# 1. Normalized Technology Aliases & Typo Tolerance Tests
# ============================================================================

class TestTechnologyAliasesAndNormalization:
    def test_mangodb_spelling_normalization_and_method_metadata(self):
        """Rule: 'MangoDB' raw claim must normalize to 'MongoDB' with known_technology_alias_or_typo."""
        skill = SemanticSkill(
            raw_value="MangoDB",
            provenance=_prov("BLOCK_003"),
        )
        normalized = normalize_skill_entity(skill)

        assert normalized.raw_value == "MangoDB"  # Verbatim claim strictly preserved
        assert normalized.normalized_value == "MongoDB"
        assert normalized.category == "database"
        assert normalized.metadata.get("normalization_method") == "known_technology_alias_or_typo"
        assert normalized.metadata.get("normalization_confidence") >= 0.85

    def test_technology_alias_mappings(self):
        canonical, cat, conf, method, _ = normalize_skill_name("Fast API")
        assert canonical == "FastAPI"
        assert cat == "backend"
        assert method == "known_technology_alias_or_typo"
        assert conf >= 0.95

        canonical, cat, conf, method, _ = normalize_skill_name("k8s")
        assert canonical == "Kubernetes"
        assert cat == "devops"
        assert method == "known_technology_alias_or_typo"
        assert conf >= 0.95

        canonical, cat, conf, method, _ = normalize_skill_name("Postgres")
        assert canonical == "PostgreSQL"
        assert cat == "database"
        assert method == "known_technology_alias_or_typo"
        assert conf >= 0.95


# ============================================================================
# 2. Raw Value Preservation Tests
# ============================================================================

class TestRawValuePreservation:
    def test_raw_values_remain_intact_across_all_entities(self):
        raw_cv = CanonicalSemanticCV(
            source_document_id="DOC_RAW_001",
            personal_info=SemanticPersonalInfo(
                full_name=RawNormalizedValue.from_raw("YOUSSOF EL KARHANI"),
                email=RawNormalizedValue.from_raw("YOUSSOF.K0@GMAIL.COM"),
                phone=RawNormalizedValue.from_raw("+49 (0) 170 1234567"),
                provenance=_prov("BLOCK_001"),
            ),
            skills=[
                SemanticSkill(raw_value="MangoDB", provenance=_prov("BLOCK_002")),
                SemanticSkill(raw_value="Docker container", provenance=_prov("BLOCK_002")),
            ],
            experiences=[
                SemanticExperience(
                    role_title=RawNormalizedValue.from_raw("Sr. Software Dev"),
                    company_name=RawNormalizedValue.from_raw("TechCorp Inc."),
                    start_date=RawNormalizedValue.from_raw("01/2022"),
                    provenance=_prov("BLOCK_003"),
                )
            ]
        )

        res = normalize_canonical_cv(raw_cv)
        cv = res.cv

        # Verify raw values are 100% verbatim
        assert cv.personal_info.full_name.raw_value == "YOUSSOF EL KARHANI"
        assert cv.personal_info.email.raw_value == "YOUSSOF.K0@GMAIL.COM"
        assert cv.personal_info.email.normalized_value == "youssof.k0@gmail.com"

        assert cv.skills[0].raw_value == "MangoDB"
        assert cv.skills[0].normalized_value == "MongoDB"

        assert cv.experiences[0].role_title.raw_value == "Sr. Software Dev"
        assert cv.experiences[0].role_title.normalized_value == "Senior Software Developer"

        assert cv.experiences[0].company_name.raw_value == "TechCorp Inc."
        assert cv.experiences[0].company_name.normalized_value == "TechCorp"


# ============================================================================
# 3. Invalid Date Ranges & Temporal Inversion Tests
# ============================================================================

class TestInvalidDateRanges:
    def test_start_date_after_end_date_generates_temporal_inversion_warning(self):
        exp = SemanticExperience(
            role_title=RawNormalizedValue.from_raw("Backend Engineer"),
            company_name=RawNormalizedValue.from_raw("Acme Corp"),
            start_date=RawNormalizedValue(raw_value="2024-06", normalized_value="2024-06"),
            end_date=RawNormalizedValue(raw_value="2021-01", normalized_value="2021-01"),  # End before start
            provenance=_prov("BLOCK_005"),
        )
        cv = CanonicalSemanticCV(experiences=[exp])
        warnings = validate_career_consistency(cv)

        assert any(w.code == "TEMPORAL_INVERSION" for w in warnings)
        inv_warn = next(w for w in warnings if w.code == "TEMPORAL_INVERSION")
        assert "precedes start date" in inv_warn.message

    def test_education_temporal_inversion(self):
        edu = SemanticEducation(
            institution=RawNormalizedValue.from_raw("University of Berlin"),
            degree=RawNormalizedValue.from_raw("B.Sc."),
            start_date=RawNormalizedValue(raw_value="2024", normalized_value="2024"),
            end_date=RawNormalizedValue(raw_value="2020", normalized_value="2020"),
            provenance=_prov("BLOCK_006"),
        )
        cv = CanonicalSemanticCV(education=[edu])
        warnings = validate_career_consistency(cv)

        assert any(w.code == "EDUCATION_TEMPORAL_INVERSION" for w in warnings)


# ============================================================================
# 4. Duplicate Records Tests (Skills, Certs, Projects)
# ============================================================================

class TestDuplicateRecords:
    def test_duplicate_skills_generate_warning_and_deduplicate_with_merged_provenance(self):
        skill_1 = SemanticSkill(
            raw_value="Python",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=["BLOCK_002"],
                raw_text="Python",
            ),
        )
        skill_2 = SemanticSkill(
            raw_value="python",  # Duplicate casing
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=["BLOCK_010"],
                raw_text="python",
            ),
        )
        cv = CanonicalSemanticCV(skills=[skill_1, skill_2])

        res = normalize_canonical_cv(cv, deduplicate=True)
        # 1. Validation warning emitted
        assert any(w.code == "DUPLICATE_SKILLS" for w in res.warnings)

        # 2. Deduplicated to 1 item
        assert len(res.cv.skills) == 1
        # 3. Provenance block IDs merged (BLOCK_002 and BLOCK_010)
        assert "BLOCK_002" in res.cv.skills[0].provenance.source_block_ids
        assert "BLOCK_010" in res.cv.skills[0].provenance.source_block_ids

    def test_duplicate_certifications_and_projects(self):
        cert_1 = SemanticCertification(
            name=RawNormalizedValue.from_raw("AWS Solutions Architect"),
            issuing_organization=RawNormalizedValue.from_raw("Amazon"),
            provenance=_prov("BLOCK_020"),
        )
        cert_2 = SemanticCertification(
            name=RawNormalizedValue.from_raw("AWS Solutions Architect"),
            issuing_organization=RawNormalizedValue.from_raw("Amazon"),
            provenance=_prov("BLOCK_021"),
        )
        proj_1 = SemanticProject(
            title=RawNormalizedValue.from_raw("Job Platform"),
            description="Automated job application and matching platform.",
            provenance=_prov("BLOCK_030"),
        )
        proj_2 = SemanticProject(
            title=RawNormalizedValue.from_raw("Job Platform"),
            description="Automated job application and matching platform.",
            provenance=_prov("BLOCK_031"),
        )
        cv = CanonicalSemanticCV(certifications=[cert_1, cert_2], projects=[proj_1, proj_2])

        res = normalize_canonical_cv(cv, deduplicate=True)
        assert any(w.code == "DUPLICATE_CERTIFICATIONS" for w in res.warnings)
        assert any(w.code == "DUPLICATE_PROJECTS" for w in res.warnings)

        assert len(res.cv.certifications) == 1
        assert "BLOCK_020" in res.cv.certifications[0].provenance.source_block_ids
        assert "BLOCK_021" in res.cv.certifications[0].provenance.source_block_ids

        assert len(res.cv.projects) == 1
        assert "BLOCK_030" in res.cv.projects[0].provenance.source_block_ids
        assert "BLOCK_031" in res.cv.projects[0].provenance.source_block_ids


# ============================================================================
# 5. Missing Provenance & Unsupported Facts Tests
# ============================================================================

class TestMissingProvenanceAndUnsupportedFacts:
    def test_missing_source_block_ids_generates_missing_provenance_warning(self):
        skill = SemanticSkill(
            raw_value="PostgreSQL",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=[],  # Empty!
                raw_text="PostgreSQL",
            ),
        )
        cv = CanonicalSemanticCV(skills=[skill])
        warnings = validate_career_consistency(cv)
        assert any(w.code == "MISSING_PROVENANCE" for w in warnings)

    def test_impossible_source_references_and_invalid_block_ids(self):
        skill = SemanticSkill(
            raw_value="Docker",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=["INVALID_BLOCK_FORMAT_XYZ"],  # Malformed ID
                raw_text="Docker",
            ),
        )
        cv = CanonicalSemanticCV(skills=[skill])
        warnings = validate_career_consistency(cv)
        assert any(w.code == "IMPOSSIBLE_SOURCE_REFERENCE" for w in warnings)

    def test_unsupported_facts_with_empty_raw_text_and_raw_value(self):
        skill = SemanticSkill(
            raw_value="",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=["BLOCK_005"],
                raw_text="",
                raw_value="",
            ),
        )
        cv = CanonicalSemanticCV(skills=[skill])
        warnings = validate_career_consistency(cv)
        assert any(w.code == "UNSUPPORTED_FACT" for w in warnings)


# ============================================================================
# 6. Malformed Contact Information Tests
# ============================================================================

class TestMalformedContactInformation:
    def test_date_range_mistaken_for_phone_number_is_rejected_and_warned(self):
        """Rule: Date range mistaken for phone number (e.g. '2019 - 2022') must be rejected."""
        info = SemanticPersonalInfo(
            full_name=RawNormalizedValue.from_raw("Test Candidate"),
            phone=RawNormalizedValue.from_raw("2019 - 2022"),  # Mistaken date range
            provenance=_prov("BLOCK_001"),
        )
        normalize_personal_info_entity(info)

        # Phone normalized_value should be None
        assert info.phone.normalized_value is None
        assert info.phone.confidence == 0.0

        cv = CanonicalSemanticCV(personal_info=info)
        warnings = validate_career_consistency(cv)
        assert any(w.code == "DATE_RANGE_AS_PHONE" for w in warnings)

    def test_malformed_email_rejected_and_warned(self):
        info = SemanticPersonalInfo(
            full_name=RawNormalizedValue.from_raw("Test Candidate"),
            email=RawNormalizedValue.from_raw("not-an-email-at-all"),
            provenance=_prov("BLOCK_001"),
        )
        normalize_personal_info_entity(info)

        assert info.email.normalized_value is None
        assert info.email.confidence == 0.0

        cv = CanonicalSemanticCV(personal_info=info)
        warnings = validate_career_consistency(cv)
        assert any(w.code == "MALFORMED_EMAIL" for w in warnings)

    def test_malformed_url_rejected_and_warned(self):
        info = SemanticPersonalInfo(
            full_name=RawNormalizedValue.from_raw("Test Candidate"),
            linkedin_url=RawNormalizedValue.from_raw("invalid url with spaces inside"),
            provenance=_prov("BLOCK_001"),
        )
        normalize_personal_info_entity(info)

        assert info.linkedin_url.normalized_value is None
        assert info.linkedin_url.confidence == 0.0

        cv = CanonicalSemanticCV(personal_info=info)
        warnings = validate_career_consistency(cv)
        assert any(w.code == "MALFORMED_URL" for w in warnings)


# ============================================================================
# 7. Unsupported Inferred Skill Rejection (Architectural Invariant)
# ============================================================================

class TestUnsupportedInferredSkillRejection:
    def test_fastapi_does_not_infer_python_as_additional_candidate_claim(self):
        """Rule: FastAPI must NOT automatically create Python as an additional candidate claim.

        Relationships between technologies may exist as metadata, but must not become
        candidate evidence unless supported by source evidence.
        """
        raw_cv = CanonicalSemanticCV(
            source_document_id="DOC_INFERENCE_CHECK",
            skills=[
                SemanticSkill(raw_value="FastAPI", provenance=_prov("BLOCK_002")),
            ],
        )

        res = normalize_canonical_cv(raw_cv)
        cv = res.cv

        # Candidate skills list must contain ONLY the explicitly extracted FastAPI claim
        skill_raw_names = [s.raw_value for s in cv.skills]
        skill_norm_names = [s.normalized_value for s in cv.skills]

        assert "FastAPI" in skill_raw_names
        assert "FastAPI" in skill_norm_names
        # Python must NOT exist as a candidate claim!
        assert "Python" not in skill_raw_names
        assert "Python" not in skill_norm_names
        assert len(cv.skills) == 1

        # Check metadata: relationships may exist in metadata ONLY
        fastapi_skill = cv.skills[0]
        assert "Python" in fastapi_skill.metadata.get("related_technologies", [])


# ============================================================================
# 8. Company & Academic Institution Normalization Tests
# ============================================================================

class TestCompanyAndInstitutionNormalization:
    def test_company_legal_suffix_stripping(self):
        assert normalize_company_name("TechCorp Inc.")[0] == "TechCorp"
        assert normalize_company_name("Google LLC")[0] == "Google"
        assert normalize_company_name("Siemens AG")[0] == "Siemens"
        assert normalize_company_name("Acme GmbH & Co. KG")[0] == "Acme"
        assert normalize_company_name("RUYA Advisory GmbH")[0] == "RUYA Advisory"

    def test_academic_institution_canonicalization(self):
        assert normalize_institution("TU Berlin")[0] == "Technical University of Berlin"
        assert normalize_institution("TUB")[0] == "Technical University of Berlin"
        assert normalize_institution("MIT")[0] == "Massachusetts Institute of Technology"
        assert normalize_institution("ETH Zurich")[0] == "ETH Zurich"
        assert normalize_institution("UCLA")[0] == "University of California, Los Angeles"


# ============================================================================
# 9. Multi-Signal Confidence Model & Invariant Verification Tests
# ============================================================================

class TestConfidenceModelAndInvariants:
    def test_confidence_signals_breakdown_and_never_verified(self):
        cv = CanonicalSemanticCV(
            source_document_id="DOC_001",
            personal_info=SemanticPersonalInfo(
                full_name=RawNormalizedValue(raw_value="Youssof El Karhani", normalized_value="Youssof El Karhani"),
                email=RawNormalizedValue(raw_value="youssof@example.com", normalized_value="youssof@example.com"),
                provenance=_prov("BLOCK_001"),
            ),
            skills=[
                SemanticSkill(raw_value="MangoDB", normalized_value="MongoDB", provenance=_prov("BLOCK_002")),
            ],
            experiences=[
                SemanticExperience(
                    role_title=RawNormalizedValue(raw_value="Senior Dev", normalized_value="Senior Developer"),
                    company_name=RawNormalizedValue(raw_value="TechCorp Inc.", normalized_value="TechCorp"),
                    start_date=RawNormalizedValue(raw_value="01/2022", normalized_value="2022-01"),
                    end_date=RawNormalizedValue(raw_value="Present", normalized_value="Present"),
                    is_current=True,
                    provenance=_prov("BLOCK_003"),
                )
            ]
        )

        res: NormalizedSemanticCVResult = normalize_canonical_cv(cv)
        qs: DocumentQualityScore = res.quality_score

        # Verify 5 distinct signals
        assert 0.0 <= qs.extraction_quality <= 1.0
        assert 0.0 <= qs.layout_confidence <= 1.0
        assert 0.0 <= qs.semantic_confidence <= 1.0
        assert 0.0 <= qs.source_consistency <= 1.0
        assert 0.0 <= qs.validation_outcome_score <= 1.0
        assert qs.overall_score >= 0.80

        # CRUCIAL INVARIANT: Never present confidence as verification
        assert qs.is_verified is False
        assert res.cv.metadata["confidence_breakdown"]["is_verified"] is False
