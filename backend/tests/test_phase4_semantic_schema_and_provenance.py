"""Test Suite for Phase 4 — Canonical Semantic CV Schema and Strict Provenance.

Verifies:
1. Valid semantic objects (Personal Info, Experience, Education, Certifications, Projects,
   Skills, Languages, Awards, Publications, Volunteering, UnknownSection).
2. Missing or invalid provenance detection (empty block IDs, hallucinated block IDs, empty pages).
3. Unknown section preservation (never discarded, preserved under section_type='unknown').
4. Null and optional fields handling.
5. Raw vs normalized separation (raw values preserved, normalized values initially null).
6. Nested objects and Evidence Bank compatibility (is_verified strictly False).
"""

import pytest
from pydantic import ValidationError

from app.schemas.semantic_cv import (
    CanonicalSemanticCV,
    ProvenanceMetadata,
    RawNormalizedValue,
    SemanticAward,
    SemanticBaseEntity,
    SemanticCertification,
    SemanticEducation,
    SemanticExperience,
    SemanticExperienceBullet,
    SemanticLanguage,
    SemanticPersonalInfo,
    SemanticProject,
    SemanticPublication,
    SemanticSkill,
    SemanticVolunteering,
    UnknownSection,
    UnknownSectionItem,
)
from app.services.provenance_validator import (
    CanonicalCVValidationReport,
    EntityValidationResult,
    ProvenanceErrorCode,
    ProvenanceValidationError,
    validate_canonical_cv,
    validate_entity_provenance,
)


def _sample_prov(block_ids: list[str] = None, pages: list[int] = None, raw_text: str = "Sample raw text") -> ProvenanceMetadata:
    """Helper to generate a valid test ProvenanceMetadata."""
    return ProvenanceMetadata(
        source_document_id="DOC_001",
        source_pages=pages if pages is not None else [1],
        source_block_ids=block_ids if block_ids is not None else ["BLOCK_001"],
        raw_text=raw_text,
        raw_value=raw_text,
        extraction_method="semantic_llm",
        extraction_confidence=0.98,
    )


# ============================================================================
# 1. Valid Semantic Objects
# ============================================================================

class TestValidSemanticObjects:
    """Verify all canonical semantic entities instantiate and serialize cleanly."""

    def test_personal_info_valid(self):
        """SemanticPersonalInfo with full name, contact details, and provenance."""
        personal = SemanticPersonalInfo(
            full_name=RawNormalizedValue(raw_value="Youssof El Karhani"),
            email=RawNormalizedValue(raw_value="youssof.k0@gmail.com"),
            phone=RawNormalizedValue(raw_value="+961-76-071579"),
            location=RawNormalizedValue(raw_value="Kirchhain, Germany"),
            headline=RawNormalizedValue(raw_value="AI & Data Automation Engineer"),
            summary=RawNormalizedValue(raw_value="Seasoned engineer building autonomous systems."),
            linkedin_url=RawNormalizedValue(raw_value="https://www.linkedin.com/in/youssof-el-karhani"),
            github_url=RawNormalizedValue(raw_value="https://github.com/youssof"),
            provenance=_sample_prov(block_ids=["BLOCK_001"], pages=[1], raw_text="Youssof El Karhani"),
        )
        assert personal.full_name.raw_value == "Youssof El Karhani"
        assert personal.full_name.normalized_value is None
        assert personal.provenance.source_block_ids == ["BLOCK_001"]

        res = validate_entity_provenance(personal, valid_block_ids={"BLOCK_001"})
        assert res.is_valid is True

    def test_all_11_entity_types_instantiation(self):
        """Verify each of the 11 required domain entities can be created with valid provenance."""
        # 1. Skill
        skill = SemanticSkill(
            raw_value="MangoDB",
            category="database",
            provenance=_sample_prov(block_ids=["BLOCK_005"], raw_text="MangoDB"),
        )
        assert skill.raw_value == "MangoDB"
        assert skill.normalized_value is None

        # 2. Language
        lang = SemanticLanguage(
            language=RawNormalizedValue.from_raw("English"),
            proficiency=RawNormalizedValue.from_raw("(C1) - IELTS"),
            provenance=_sample_prov(block_ids=["BLOCK_006"], raw_text="English: (C1) - IELTS"),
        )
        assert lang.language.raw_value == "English"
        assert lang.proficiency.raw_value == "(C1) - IELTS"

        # 3. Experience & Nested Bullets
        bullet = SemanticExperienceBullet(
            raw_text="Architected distributed middleware in Python.",
            provenance=_sample_prov(block_ids=["BLOCK_007"], raw_text="Architected distributed middleware"),
        )
        exp = SemanticExperience(
            company_name=RawNormalizedValue.from_raw("RUYA Advisory"),
            role_title=RawNormalizedValue.from_raw("AI & Automation Lead"),
            start_date=RawNormalizedValue.from_raw("01/2025"),
            is_current=True,
            bullets=[bullet],
            provenance=_sample_prov(block_ids=["BLOCK_008"], raw_text="RUYA Advisory AI & Automation Lead"),
        )
        assert exp.company_name.raw_value == "RUYA Advisory"
        assert len(exp.bullets) == 1

        # 4. Education
        edu = SemanticEducation(
            institution=RawNormalizedValue.from_raw("Lebanese American University"),
            degree=RawNormalizedValue.from_raw("B.S. in Computer Science"),
            start_date=RawNormalizedValue.from_raw("2019"),
            end_date=RawNormalizedValue.from_raw("2023"),
            provenance=_sample_prov(block_ids=["BLOCK_009"], raw_text="Lebanese American University B.S."),
        )
        assert edu.institution.raw_value == "Lebanese American University"

        # 5. Certification
        cert = SemanticCertification(
            name=RawNormalizedValue.from_raw("AWS Solutions Architect"),
            issuing_organization=RawNormalizedValue.from_raw("Amazon Web Services"),
            issue_date=RawNormalizedValue.from_raw("2024-05"),
            provenance=_sample_prov(block_ids=["BLOCK_010"], raw_text="AWS Solutions Architect"),
        )
        assert cert.name.raw_value == "AWS Solutions Architect"

        # 6. Project
        proj = SemanticProject(
            title=RawNormalizedValue.from_raw("Sentimental Chatbot Engine"),
            description="Autonomous sentiment-aware agent orchestrator.",
            technologies=[RawNormalizedValue.from_raw("Python"), RawNormalizedValue.from_raw("FastAPI")],
            provenance=_sample_prov(block_ids=["BLOCK_011"], raw_text="Sentimental Chatbot Engine"),
        )
        assert proj.title.raw_value == "Sentimental Chatbot Engine"

        # 7. Award
        award = SemanticAward(
            title=RawNormalizedValue.from_raw("First Place AI Hackathon 2024"),
            issuer=RawNormalizedValue.from_raw("Beirut Tech Summit"),
            provenance=_sample_prov(block_ids=["BLOCK_012"], raw_text="First Place AI Hackathon"),
        )
        assert award.title.raw_value == "First Place AI Hackathon 2024"

        # 8. Publication
        pub = SemanticPublication(
            title=RawNormalizedValue.from_raw("Event-Driven Autonomous Microservices"),
            publisher=RawNormalizedValue.from_raw("IEEE Conference on Cloud Computing"),
            provenance=_sample_prov(block_ids=["BLOCK_013"], raw_text="Event-Driven Autonomous Microservices"),
        )
        assert pub.title.raw_value == "Event-Driven Autonomous Microservices"

        # 9. Volunteering
        vol = SemanticVolunteering(
            organization=RawNormalizedValue.from_raw("Code For Good Lebanon"),
            role=RawNormalizedValue.from_raw("Lead Python Mentor"),
            provenance=_sample_prov(block_ids=["BLOCK_014"], raw_text="Code For Good Lebanon Lead Mentor"),
        )
        assert vol.organization.raw_value == "Code For Good Lebanon"

        # 10. Unknown Section
        unk_item = UnknownSectionItem(
            raw_text="Contributed PR #412 to FastAPI core.",
            provenance=_sample_prov(block_ids=["BLOCK_015"], raw_text="Contributed PR #412"),
        )
        unk = UnknownSection(
            heading="Open Source Contributions",
            items=[unk_item],
            provenance=_sample_prov(block_ids=["BLOCK_015"], raw_text="Open Source Contributions"),
        )
        assert unk.section_type == "unknown"
        assert unk.heading == "Open Source Contributions"
        assert len(unk.items) == 1


# ============================================================================
# 2. Strict Provenance Validation & Rejection
# ============================================================================

class TestStrictProvenanceValidation:
    """Verify the core rule: An entity without valid provenance MUST NOT be accepted."""

    def test_empty_source_block_ids_is_rejected(self):
        """Entity with empty source_block_ids must fail provenance verification."""
        skill = SemanticSkill(
            raw_value="Python",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=[],  # EMPTY
                raw_text="Python",
            ),
        )
        res = validate_entity_provenance(skill)
        assert res.is_valid is False
        assert ProvenanceErrorCode.EMPTY_SOURCE_BLOCK_IDS in res.error_codes

    def test_hallucinated_source_block_reference_is_rejected(self):
        """Entity referencing a non-existent block ID must be rejected as hallucination."""
        skill = SemanticSkill(
            raw_value="Kubernetes",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=["BLOCK_999"],  # Hallucinated block not in layout
                raw_text="Kubernetes",
            ),
        )
        # Valid blocks from actual layout document
        valid_layout_blocks = {"BLOCK_001", "BLOCK_002", "BLOCK_003"}
        res = validate_entity_provenance(skill, valid_block_ids=valid_layout_blocks)
        assert res.is_valid is False
        assert ProvenanceErrorCode.INVALID_SOURCE_BLOCK_REFERENCE in res.error_codes
        assert "BLOCK_999" in res.errors[0]

    def test_empty_source_pages_is_rejected(self):
        """Entity with empty source_pages must fail provenance verification."""
        skill = SemanticSkill(
            raw_value="Docker",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[],  # EMPTY
                source_block_ids=["BLOCK_001"],
                raw_text="Docker",
            ),
        )
        res = validate_entity_provenance(skill)
        assert res.is_valid is False
        assert ProvenanceErrorCode.EMPTY_SOURCE_PAGES in res.error_codes

    def test_empty_raw_text_and_raw_value_is_rejected(self):
        """Entity without supporting raw text must fail provenance verification."""
        skill = SemanticSkill(
            raw_value="",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=["BLOCK_001"],
                raw_text="",  # EMPTY
                raw_value="",
            ),
        )
        res = validate_entity_provenance(skill)
        assert res.is_valid is False
        assert ProvenanceErrorCode.EMPTY_RAW_TEXT in res.error_codes

    def test_canonical_cv_filters_unprovenanced_claims(self):
        """In non-strict mode, unprovenanced claims are partitioned into rejected_claims."""
        valid_skill = SemanticSkill(
            raw_value="FastAPI",
            provenance=_sample_prov(block_ids=["BLOCK_001"], raw_text="FastAPI"),
        )
        invalid_skill = SemanticSkill(
            raw_value="HallucinatedSkill",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=[],  # MISSING
                raw_text="HallucinatedSkill",
            ),
        )

        cv = CanonicalSemanticCV(skills=[valid_skill, invalid_skill])
        report: CanonicalCVValidationReport = validate_canonical_cv(cv, valid_block_ids={"BLOCK_001"}, strict=False)

        assert report.is_valid is False
        assert report.accepted_entities_count == 1
        assert report.rejected_entities_count == 1

        # Only the valid skill exists in accepted_cv
        assert len(report.accepted_cv.skills) == 1
        assert report.accepted_cv.skills[0].raw_value == "FastAPI"

        # The rejected skill is tracked in rejected_claims
        assert len(report.rejected_claims) == 1
        assert "HallucinatedSkill" in report.rejected_claims[0]["summary"]

    def test_canonical_cv_strict_mode_raises_error(self):
        """In strict mode, an unprovenanced claim raises ProvenanceValidationError."""
        invalid_skill = SemanticSkill(
            raw_value="GhostSkill",
            provenance=ProvenanceMetadata(
                source_document_id="DOC_001",
                source_pages=[1],
                source_block_ids=[],
                raw_text="GhostSkill",
            ),
        )
        cv = CanonicalSemanticCV(skills=[invalid_skill])
        with pytest.raises(ProvenanceValidationError) as exc_info:
            validate_canonical_cv(cv, strict=True)
        assert "Provenance validation failed" in str(exc_info.value)


# ============================================================================
# 3. Unknown Sections Preservation
# ============================================================================

class TestUnknownSectionsPreservation:
    """Verify unknown CV sections are never discarded and retain full provenance."""

    def test_unknown_section_is_preserved_with_items(self):
        """Unknown section 'Open Source Contributions' must be preserved with items and provenance."""
        item1 = UnknownSectionItem(
            raw_text="Maintained async task worker with 500k downloads.",
            provenance=_sample_prov(block_ids=["BLOCK_020"], raw_text="Maintained async task worker"),
        )
        item2 = UnknownSectionItem(
            raw_text="Authored RFC for distributed telemetry.",
            provenance=_sample_prov(block_ids=["BLOCK_021"], raw_text="Authored RFC"),
        )
        unknown_sec = UnknownSection(
            heading="Open Source Contributions",
            items=[item1, item2],
            raw_text="Open Source Contributions\nMaintained async task worker\nAuthored RFC",
            provenance=_sample_prov(block_ids=["BLOCK_020", "BLOCK_021"], raw_text="Open Source Contributions"),
        )

        cv = CanonicalSemanticCV(unknown_sections=[unknown_sec])
        report = validate_canonical_cv(cv, valid_block_ids={"BLOCK_020", "BLOCK_021"})
        assert report.is_valid is True
        assert len(report.accepted_cv.unknown_sections) == 1

        saved_sec = report.accepted_cv.unknown_sections[0]
        assert saved_sec.section_type == "unknown"
        assert saved_sec.heading == "Open Source Contributions"
        assert len(saved_sec.items) == 2


# ============================================================================
# 4. Null & Optional Fields
# ============================================================================

class TestNullAndOptionalFields:
    """Verify partial, missing, and null fields deserialize cleanly."""

    def test_null_fields_in_experience_and_education(self):
        """Current job with end_date=None and education with field_of_study=None."""
        exp = SemanticExperience(
            company_name=RawNormalizedValue.from_raw("Startup X"),
            role_title=RawNormalizedValue.from_raw("Founding Engineer"),
            start_date=RawNormalizedValue.from_raw("2024-01"),
            end_date=None,  # Currently employed
            is_current=True,
            location=None,  # No location declared
            description=None,
            bullets=[],
            provenance=_sample_prov(block_ids=["BLOCK_030"]),
        )
        assert exp.end_date is None
        assert exp.is_current is True
        assert exp.location is None

        edu = SemanticEducation(
            institution=RawNormalizedValue.from_raw("Self-Taught Academy"),
            degree=RawNormalizedValue.from_raw("Certificate"),
            field_of_study=None,
            start_date=None,
            end_date=None,
            grade=None,
            activities=None,
            provenance=_sample_prov(block_ids=["BLOCK_031"]),
        )
        assert edu.field_of_study is None
        assert edu.grade is None


# ============================================================================
# 5. Raw vs Normalized Value Separation
# ============================================================================

class TestRawVsNormalizedSeparation:
    """Verify raw extracted values remain verbatim and normalized values stay null initially."""

    def test_raw_mangodb_spelling_claim_preserved(self):
        """'MangoDB' candidate claim must stay strictly in raw_value with normalized_value=None."""
        skill = SemanticSkill(
            raw_value="MangoDB",
            normalized_value=None,  # Normalization comes in a later phase!
            provenance=_sample_prov(block_ids=["BLOCK_040"], raw_text="MangoDB"),
        )
        assert skill.raw_value == "MangoDB"
        assert skill.normalized_value is None

    def test_raw_phone_number_preservation(self):
        """International phone format must stay in raw_value without immediate formatting."""
        personal = SemanticPersonalInfo(
            full_name=RawNormalizedValue.from_raw("Youssof"),
            phone=RawNormalizedValue(raw_value="+961-76-071579", normalized_value=None),
            provenance=_sample_prov(block_ids=["BLOCK_041"]),
        )
        assert personal.phone.raw_value == "+961-76-071579"
        assert personal.phone.normalized_value is None


# ============================================================================
# 6. Nested Objects & Evidence Bank Compatibility
# ============================================================================

class TestNestedObjectsAndEvidenceBankCompatibility:
    """Verify mapping to Evidence Bank drafts preserves all claims with is_verified=False."""

    def test_evidence_bank_draft_mapping_invariants(self):
        """CanonicalSemanticCV maps to ExtractedEvidenceBankDraft with is_verified=False strictly."""
        cv = CanonicalSemanticCV(
            source_document_id="Youssof_CV_001",
            personal_info=SemanticPersonalInfo(
                full_name=RawNormalizedValue.from_raw("Youssof El Karhani"),
                headline=RawNormalizedValue.from_raw("AI Engineer"),
                phone=RawNormalizedValue.from_raw("+961-76-071579"),
                provenance=_sample_prov(block_ids=["BLOCK_001"]),
            ),
            experiences=[
                SemanticExperience(
                    company_name=RawNormalizedValue.from_raw("RUYA Advisory"),
                    role_title=RawNormalizedValue.from_raw("AI Lead"),
                    start_date=RawNormalizedValue.from_raw("01/2025"),
                    is_current=True,
                    bullets=[
                        SemanticExperienceBullet(
                            raw_text="Architected event-driven automation middleware.",
                            provenance=_sample_prov(block_ids=["BLOCK_002"]),
                        )
                    ],
                    provenance=_sample_prov(block_ids=["BLOCK_002"]),
                )
            ],
            skills=[
                SemanticSkill(
                    raw_value="Python",
                    category="backend",
                    provenance=_sample_prov(block_ids=["BLOCK_003"]),
                ),
                SemanticSkill(
                    raw_value="FastAPI",
                    category="backend",
                    provenance=_sample_prov(block_ids=["BLOCK_003"]),
                ),
            ],
            unknown_sections=[
                UnknownSection(
                    heading="Patents",
                    items=[
                        UnknownSectionItem(
                            raw_text="US Patent 12345: Autonomous Pipeline Optimization",
                            provenance=_sample_prov(block_ids=["BLOCK_004"]),
                        )
                    ],
                    provenance=_sample_prov(block_ids=["BLOCK_004"]),
                )
            ],
        )

        draft = cv.to_evidence_bank_draft()

        # Invariant 1: Correct entity mapping
        assert draft.headline == "AI Engineer"
        assert draft.phone == "+961-76-071579"
        assert len(draft.experiences) == 1
        assert draft.experiences[0].company_name == "RUYA Advisory"
        assert len(draft.experiences[0].bullets) == 1
        assert "Architected" in draft.experiences[0].bullets[0].text

        assert len(draft.skills) == 2
        assert draft.skills[0].name == "Python"
        assert draft.skills[1].name == "FastAPI"

        # Invariant 2: Unknown section preserved in draft
        assert "Patents" in draft.unclassified_sections
        assert len(draft.unclassified_sections["Patents"]) == 1

        # Invariant 3: Verification status is not auto-approved
        # ExtractedEvidenceBankDraft contains unverified draft claims
        assert draft.extraction_mode == "canonical_semantic_schema"
