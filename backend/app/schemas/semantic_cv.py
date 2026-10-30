"""Canonical Semantic CV Schemas with Strict Provenance.

Defines the target typed data contract for semantic extraction:
- Personal Information
- Experience (with nested achievement bullets)
- Education
- Certifications
- Projects
- Skills
- Languages
- Awards
- Publications
- Volunteering
- Unknown / Unclassified Sections

Enforces separation of raw vs normalized values and strict provenance metadata
(source_document_id, source_pages, source_block_ids, raw_text, extraction_confidence).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# 1. Provenance & Raw/Normalized Core Types
# ============================================================================

class ProvenanceMetadata(BaseModel):
    """Immutable audit trail tying an extracted semantic fact to physical source blocks."""
    model_config = ConfigDict(extra="ignore")

    source_document_id: Optional[str] = Field(
        default=None,
        description="Identifier or hash of the source document/file"
    )
    source_pages: List[int] = Field(
        default_factory=list,
        description="1-based page numbers where this content appears"
    )
    source_block_ids: List[str] = Field(
        default_factory=list,
        description="Stable block IDs from layout reconstruction (e.g. ['BLOCK_005', 'BLOCK_006'])"
    )
    raw_text: str = Field(
        default="",
        description="Exact raw text snippet from the source blocks supporting this entity"
    )
    raw_value: Optional[str] = Field(
        default=None,
        description="Specific raw value extracted before any interpretation"
    )
    extraction_method: str = Field(
        default="semantic_llm",
        description="Extraction method: 'semantic_llm', 'layout_heuristic', or 'native_text'"
    )
    extraction_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence score between 0.0 and 1.0"
    )

    @property
    def has_valid_blocks(self) -> bool:
        """Return True if at least one non-empty source block ID is referenced."""
        return bool(self.source_block_ids and any(bid.strip() for bid in self.source_block_ids))


class RawNormalizedValue(BaseModel):
    """Pairs verbatim extracted text with a separate post-normalization slot."""
    model_config = ConfigDict(extra="ignore")

    raw_value: str = Field(
        description="Exact verbatim value extracted from the source CV (e.g. 'MangoDB')"
    )
    normalized_value: Optional[str] = Field(
        default=None,
        description="Canonical or normalized form (strictly null until deterministic normalization phase)"
    )

    @classmethod
    def from_raw(cls, raw: str) -> "RawNormalizedValue":
        """Factory creating an unnormalized value pairing."""
        return cls(raw_value=raw, normalized_value=None)


class SemanticBaseEntity(BaseModel):
    """Base class for all semantic CV entities requiring provenance."""
    model_config = ConfigDict(extra="ignore")

    provenance: ProvenanceMetadata = Field(
        description="Traceable audit trail tying this entity to source blocks"
    )


# ============================================================================
# 2. Personal Information
# ============================================================================

class SemanticPersonalInfo(SemanticBaseEntity):
    """Personal contact information and executive summary."""

    full_name: RawNormalizedValue = Field(description="Candidate's full name")
    email: Optional[RawNormalizedValue] = Field(default=None, description="Contact email address")
    phone: Optional[RawNormalizedValue] = Field(default=None, description="Raw phone number (e.g. '+961-76-071579')")
    location: Optional[RawNormalizedValue] = Field(default=None, description="Location / Address")
    headline: Optional[RawNormalizedValue] = Field(default=None, description="Professional headline or title")
    summary: Optional[RawNormalizedValue] = Field(default=None, description="Executive or career summary")
    linkedin_url: Optional[RawNormalizedValue] = Field(default=None, description="LinkedIn profile URL")
    github_url: Optional[RawNormalizedValue] = Field(default=None, description="GitHub profile URL")
    portfolio_url: Optional[RawNormalizedValue] = Field(default=None, description="Personal website or portfolio URL")


# ============================================================================
# 3. Work Experience & Nested Bullets
# ============================================================================

class SemanticExperienceBullet(SemanticBaseEntity):
    """Atomic factual achievement or responsibility bullet point."""

    raw_text: str = Field(description="Verbatim text of the achievement or bullet")
    normalized_text: Optional[str] = Field(default=None, description="Normalized or cleaned text (null initially)")
    category: str = Field(
        default="experience",
        description="Category: 'experience', 'achievement', 'metric', or 'leadership'"
    )


class SemanticExperience(SemanticBaseEntity):
    """Structured work experience record."""

    company_name: RawNormalizedValue = Field(description="Name of employer / organization")
    role_title: RawNormalizedValue = Field(description="Job title or role held")
    location: Optional[RawNormalizedValue] = Field(default=None, description="City, country or remote status")
    start_date: RawNormalizedValue = Field(description="Start date raw text (e.g. '01/2025' or 'Jan 2025')")
    end_date: Optional[RawNormalizedValue] = Field(default=None, description="End date raw text or null if current")
    is_current: bool = Field(default=False, description="True if candidate currently holds this role")
    description: Optional[str] = Field(default=None, description="General role overview paragraph if present")
    bullets: List[SemanticExperienceBullet] = Field(
        default_factory=list,
        description="Discrete achievement or responsibility bullets"
    )


# ============================================================================
# 4. Education & Academic Background
# ============================================================================

class SemanticEducation(SemanticBaseEntity):
    """Academic degree or educational program."""

    institution: RawNormalizedValue = Field(description="Name of university, college, or school")
    degree: RawNormalizedValue = Field(description="Degree name (e.g. 'Bachelor of Science')")
    field_of_study: Optional[RawNormalizedValue] = Field(default=None, description="Major, discipline, or field of study")
    start_date: Optional[RawNormalizedValue] = Field(default=None, description="Start year or date")
    end_date: Optional[RawNormalizedValue] = Field(default=None, description="Graduation year or date")
    grade: Optional[RawNormalizedValue] = Field(default=None, description="GPA, honors, or grade")
    activities: Optional[str] = Field(default=None, description="Extracurricular activities or societies")
    bullets: List[str] = Field(default_factory=list, description="Associated academic achievements or bullet items")


# ============================================================================
# 5. Certifications & Credentials
# ============================================================================

class SemanticCertification(SemanticBaseEntity):
    """Professional certification or license."""

    name: RawNormalizedValue = Field(description="Certification or license title")
    issuing_organization: RawNormalizedValue = Field(description="Issuing platform or institution")
    issue_date: Optional[RawNormalizedValue] = Field(default=None, description="Issue date raw text")
    expiration_date: Optional[RawNormalizedValue] = Field(default=None, description="Expiration date if applicable")
    credential_id: Optional[str] = Field(default=None, description="License or credential identification code")
    credential_url: Optional[str] = Field(default=None, description="Online credential verification link")


# ============================================================================
# 6. Projects & Portfolio
# ============================================================================

class SemanticProject(SemanticBaseEntity):
    """Technical portfolio project or initiative."""

    title: RawNormalizedValue = Field(description="Project title or system name")
    description: str = Field(description="Project overview and accomplishments")
    category: Optional[str] = Field(default=None, description="Project domain or type")
    technologies: List[RawNormalizedValue] = Field(
        default_factory=list,
        description="List of technologies, frameworks, or tools used"
    )
    url: Optional[str] = Field(default=None, description="Live deployment URL")
    github_url: Optional[str] = Field(default=None, description="Source code repository URL")
    bullets: List[str] = Field(default_factory=list, description="Specific project achievement bullets")


# ============================================================================
# 7. Skills & Technical Capabilities
# ============================================================================

class SemanticSkill(SemanticBaseEntity):
    """Technical or soft skill claim."""

    raw_value: str = Field(description="Exact verbatim skill string from the CV (e.g. 'MangoDB', 'PyTorch')")
    normalized_value: Optional[str] = Field(
        default=None,
        description="Canonical normalized skill name (null initially; filled in normalization phase)"
    )
    category: Optional[str] = Field(
        default=None,
        description="Categorization (e.g. 'backend', 'data_engineering', 'ai_ml', 'devops')"
    )
    proficiency: Optional[str] = Field(
        default=None,
        description="Proficiency indicator if explicitly stated (e.g. 'Advanced', 'Working knowledge')"
    )
    years_of_experience: Optional[float] = Field(
        default=None,
        description="Years of experience if explicitly declared in CV text"
    )


# ============================================================================
# 8. Languages Spoken
# ============================================================================

class SemanticLanguage(SemanticBaseEntity):
    """Natural language capability."""

    language: RawNormalizedValue = Field(description="Language name (e.g. 'English', 'Arabic')")
    proficiency: Optional[RawNormalizedValue] = Field(
        default=None,
        description="Proficiency level declaration (e.g. '(C1) - IELTS', 'Native', 'Fluent')"
    )


# ============================================================================
# 9. Awards, Publications & Volunteering
# ============================================================================

class SemanticAward(SemanticBaseEntity):
    """Honors, prizes, or competitive awards."""

    title: RawNormalizedValue = Field(description="Award or honor title")
    issuer: Optional[RawNormalizedValue] = Field(default=None, description="Granting institution or body")
    date: Optional[RawNormalizedValue] = Field(default=None, description="Date awarded")
    description: Optional[str] = Field(default=None, description="Award description or significance")


class SemanticPublication(SemanticBaseEntity):
    """Research paper, article, or book publication."""

    title: RawNormalizedValue = Field(description="Publication title")
    publisher: Optional[RawNormalizedValue] = Field(default=None, description="Journal, conference, or publisher")
    date: Optional[RawNormalizedValue] = Field(default=None, description="Date published")
    url: Optional[str] = Field(default=None, description="Link or DOI")
    description: Optional[str] = Field(default=None, description="Summary or abstract")


class SemanticVolunteering(SemanticBaseEntity):
    """Volunteer work, community leadership, or pro-bono service."""

    organization: RawNormalizedValue = Field(description="Name of non-profit or community organization")
    role: RawNormalizedValue = Field(description="Volunteer role or title held")
    start_date: Optional[RawNormalizedValue] = Field(default=None, description="Start date")
    end_date: Optional[RawNormalizedValue] = Field(default=None, description="End date")
    description: Optional[str] = Field(default=None, description="Description of volunteer responsibilities")
    bullets: List[str] = Field(default_factory=list, description="Specific volunteer achievement bullets")


# ============================================================================
# 10. Unknown / Unclassified Sections
# ============================================================================

class UnknownSectionItem(SemanticBaseEntity):
    """Discrete item inside an unknown or unrecognized CV section."""

    raw_text: str = Field(description="Verbatim text of the item")


class UnknownSection(SemanticBaseEntity):
    """Preserved section with unfamiliar heading that must not be discarded."""

    section_type: str = Field(default="unknown", description="Section classification identifier ('unknown')")
    heading: str = Field(description="Raw heading text of the unknown section (e.g. 'Open Source Contributions')")
    items: List[UnknownSectionItem] = Field(
        default_factory=list,
        description="List of items or lines preserved under this heading"
    )
    raw_text: Optional[str] = Field(
        default=None,
        description="Complete raw text of the unknown section"
    )


# ============================================================================
# 11. Canonical Semantic CV Root Document
# ============================================================================

class CanonicalSemanticCV(BaseModel):
    """Root canonical semantic document containing all structured sections and audit provenance."""
    model_config = ConfigDict(extra="ignore")

    source_document_id: Optional[str] = Field(default=None, description="Source document identifier")
    personal_info: Optional[SemanticPersonalInfo] = Field(default=None, description="Personal and contact info")
    experiences: List[SemanticExperience] = Field(default_factory=list, description="Work experiences")
    education: List[SemanticEducation] = Field(default_factory=list, description="Education records")
    certifications: List[SemanticCertification] = Field(default_factory=list, description="Certifications")
    projects: List[SemanticProject] = Field(default_factory=list, description="Projects")
    skills: List[SemanticSkill] = Field(default_factory=list, description="Technical and professional skills")
    languages: List[SemanticLanguage] = Field(default_factory=list, description="Languages spoken")
    awards: List[SemanticAward] = Field(default_factory=list, description="Honors and awards")
    publications: List[SemanticPublication] = Field(default_factory=list, description="Publications")
    volunteering: List[SemanticVolunteering] = Field(default_factory=list, description="Volunteering experience")
    unknown_sections: List[UnknownSection] = Field(
        default_factory=list,
        description="Preserved unclassified sections (never discarded)"
    )
    raw_cv_text: Optional[str] = Field(default=None, description="Complete unedited raw CV text")
    extraction_mode: str = Field(default="canonical_semantic_schema", description="Schema format version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution and extraction metadata")

    def to_evidence_bank_draft(self) -> Dict[str, Any]:
        """Map canonical semantic entities to Evidence Bank compatible draft dictionary.

        Crucial Architectural Invariants:
        1. All extracted claims are strictly marked with is_verified = False.
        2. Raw values are preserved.
        3. Never automatically approves claims for application generation.
        """
        from app.protocols.ai_service import (
            ExtractedCertification,
            ExtractedEducation,
            ExtractedEvidenceBankDraft,
            ExtractedEvidenceBullet,
            ExtractedExperience,
            ExtractedProject,
            ExtractedSkill,
        )

        draft = ExtractedEvidenceBankDraft(
            headline=self.personal_info.headline.raw_value if (self.personal_info and self.personal_info.headline) else None,
            summary=self.personal_info.summary.raw_value if (self.personal_info and self.personal_info.summary) else None,
            phone=self.personal_info.phone.raw_value if (self.personal_info and self.personal_info.phone) else None,
            location=self.personal_info.location.raw_value if (self.personal_info and self.personal_info.location) else None,
            linkedin_url=self.personal_info.linkedin_url.raw_value if (self.personal_info and self.personal_info.linkedin_url) else None,
            github_url=self.personal_info.github_url.raw_value if (self.personal_info and self.personal_info.github_url) else None,
            portfolio_url=self.personal_info.portfolio_url.raw_value if (self.personal_info and self.personal_info.portfolio_url) else None,
            experiences=[
                ExtractedExperience(
                    company_name=exp.company_name.raw_value,
                    role_title=exp.role_title.raw_value,
                    location=exp.location.raw_value if exp.location else None,
                    start_date=exp.start_date.raw_value,
                    end_date=exp.end_date.raw_value if exp.end_date else None,
                    is_current=exp.is_current,
                    description=exp.description,
                    bullets=[
                        ExtractedEvidenceBullet(
                            text=b.raw_text,
                            category=b.category,
                        )
                        for b in exp.bullets
                    ],
                )
                for exp in self.experiences
            ],
            skills=[
                ExtractedSkill(
                    name=s.raw_value,
                    category=s.category or "tools",
                    proficiency=s.proficiency,
                    years_of_experience=s.years_of_experience,
                )
                for s in self.skills
            ],
            projects=[
                ExtractedProject(
                    title=p.title.raw_value,
                    description=p.description,
                    category=p.category,
                    technologies=[t.raw_value for t in p.technologies],
                    url=p.url,
                    github_url=p.github_url,
                )
                for p in self.projects
            ],
            certifications=[
                ExtractedCertification(
                    name=c.name.raw_value,
                    issuing_organization=c.issuing_organization.raw_value,
                    issue_date=c.issue_date.raw_value if c.issue_date else None,
                    expiration_date=c.expiration_date.raw_value if c.expiration_date else None,
                    credential_id=c.credential_id,
                    credential_url=c.credential_url,
                )
                for c in self.certifications
            ],
            education=[
                ExtractedEducation(
                    institution=e.institution.raw_value,
                    degree=e.degree.raw_value,
                    field_of_study=e.field_of_study.raw_value if e.field_of_study else "General",
                    start_date=e.start_date.raw_value if e.start_date else None,
                    end_date=e.end_date.raw_value if e.end_date else None,
                    grade=e.grade.raw_value if e.grade else None,
                    activities=e.activities,
                )
                for e in self.education
            ],
            languages=[
                f"{lang.language.raw_value}: {lang.proficiency.raw_value}"
                if lang.proficiency else lang.language.raw_value
                for lang in self.languages
            ],
            unclassified_sections={
                sec.heading: [item.raw_text for item in sec.items]
                for sec in self.unknown_sections
            },
            raw_cv_text=self.raw_cv_text,
            extraction_mode="canonical_semantic_schema",
        )
        return draft
