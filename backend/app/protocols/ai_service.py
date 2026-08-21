"""AI Gateway Protocol and Structured Extraction Schemas.

Enforces that LLMs select verified evidence by stable ID and return strictly typed Pydantic structures.
"""

from typing import Any, Dict, List, Optional, Protocol
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Target Extraction Schemas
# ---------------------------------------------------------------------------

class ExtractedEvidenceBullet(BaseModel):
    """Discrete factual achievement or responsibility bullet point."""
    text: str = Field(description="Factual achievement or responsibility statement.")
    category: str = Field(
        default="experience",
        description="Category: experience, achievement, metric, or leadership.",
    )
    variants: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional pre-approved variants (e.g. FULL, SHORT, DATA).",
    )


class ExtractedExperience(BaseModel):
    """Structured work experience record extracted from CV."""
    company_name: str = Field(description="Name of the employer / company.")
    role_title: str = Field(description="Job title or role held.")
    location: Optional[str] = Field(default=None, description="City, country or remote status.")
    start_date: str = Field(description="Start date (e.g. '2023-01' or 'Jan 2023').")
    end_date: Optional[str] = Field(default=None, description="End date or None if current.")
    is_current: bool = Field(default=False, description="True if candidate currently holds this role.")
    description: Optional[str] = Field(default=None, description="General role overview.")
    bullets: List[ExtractedEvidenceBullet] = Field(
        default_factory=list,
        description="List of atomic achievement / responsibility bullets.",
    )


class ExtractedSkill(BaseModel):
    """Structured candidate skill extracted from CV."""
    name: str = Field(description="Standardized name of the skill or technology.")
    category: str = Field(
        default="backend",
        description="Category: programming, backend, data_engineering, ai_ml, devops, tools, soft_skill.",
    )
    proficiency: Optional[str] = Field(
        default=None,
        description="Proficiency level: beginner, intermediate, advanced, expert.",
    )
    years_of_experience: Optional[float] = Field(
        default=None,
        description="Estimated years of experience.",
    )


class ExtractedProject(BaseModel):
    """Structured portfolio or side project extracted from CV."""
    title: str = Field(description="Title of the project.")
    category: Optional[str] = Field(default=None, description="Domain or project type.")
    description: str = Field(description="Overview and accomplishments.")
    technologies: List[str] = Field(default_factory=list, description="List of technologies used.")
    url: Optional[str] = Field(default=None, description="Live project URL.")
    github_url: Optional[str] = Field(default=None, description="Source code repository URL.")


class ExtractedCertification(BaseModel):
    """Structured certification or credential extracted from CV."""
    name: str = Field(description="Certification title.")
    issuing_organization: str = Field(description="Organization or platform that issued the certificate.")
    issue_date: Optional[str] = Field(default=None, description="Date issued (e.g. '2024-05').")
    expiration_date: Optional[str] = Field(default=None, description="Expiration date if applicable.")
    credential_id: Optional[str] = Field(default=None, description="License or credential ID.")
    credential_url: Optional[str] = Field(default=None, description="Verification URL.")


class ExtractedEducation(BaseModel):
    """Structured academic degree or education record extracted from CV."""
    institution: str = Field(description="Name of the university or institution.")
    degree: str = Field(description="Degree name (e.g. 'Bachelor of Science').")
    field_of_study: str = Field(description="Major or area of study.")
    start_date: Optional[str] = Field(default=None, description="Start year or date.")
    end_date: Optional[str] = Field(default=None, description="Graduation year or date.")
    grade: Optional[str] = Field(default=None, description="GPA or grade achieved.")
    activities: Optional[str] = Field(default=None, description="Extracurriculars or notable honors.")


class ExtractedEvidenceBankDraft(BaseModel):
    """Comprehensive draft of parsed candidate profile and evidence bank."""
    headline: Optional[str] = Field(default=None, description="Professional headline.")
    summary: Optional[str] = Field(default=None, description="Executive or personal summary.")
    phone: Optional[str] = Field(default=None, description="Phone number.")
    location: Optional[str] = Field(default=None, description="Current location.")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL.")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL.")
    portfolio_url: Optional[str] = Field(default=None, description="Personal website/portfolio.")
    experiences: List[ExtractedExperience] = Field(default_factory=list)
    skills: List[ExtractedSkill] = Field(default_factory=list)
    projects: List[ExtractedProject] = Field(default_factory=list)
    certifications: List[ExtractedCertification] = Field(default_factory=list)
    education: List[ExtractedEducation] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Matching & Evaluation Schemas
# ---------------------------------------------------------------------------

class PreScreenResult(BaseModel):
    """Fast, high-recall filter result to determine if a job warrants deep assessment."""
    relevant: bool = Field(description="Whether the job aligns with candidate profile domain.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score.")
    reason_codes: List[str] = Field(default_factory=list, description="Machine-readable reason tags.")
    reasoning: str = Field(description="Explanation of relevancy.")


class JobAssessmentResult(BaseModel):
    """Deep multi-dimensional compatibility assessment result."""
    overall_score: int = Field(ge=0, le=100, description="Composite compatibility score.")
    skills_score: int = Field(ge=0, le=100)
    experience_score: int = Field(ge=0, le=100)
    seniority_score: int = Field(ge=0, le=100)
    location_score: int = Field(ge=0, le=100)
    language_score: int = Field(ge=0, le=100)
    matching_evidence_ids: List[str] = Field(
        default_factory=list,
        description="Stable IDs of verified candidate evidence that match the job.",
    )
    missing_requirements: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    recommendation: str = Field(description="'apply', 'consider', or 'skip'.")
    confidence: float = Field(ge=0.0, le=1.0)
    sanitized_job_title: str


class CVSelectionResult(BaseModel):
    """Strict selection of verified stable IDs by LLM without modifying text."""
    experience_bullet_ids: List[str] = Field(
        default_factory=list,
        description="Selected stable IDs for experience bullets (e.g. ['EXP_001', 'EXP_003']).",
    )
    project_ids: List[str] = Field(
        default_factory=list,
        description="Selected stable IDs for projects (e.g. ['PROJ_001']).",
    )
    skill_ids: List[str] = Field(
        default_factory=list,
        description="Selected stable IDs for skills (e.g. ['SKILL_001', 'SKILL_002']).",
    )
    certification_ids: List[str] = Field(
        default_factory=list,
        description="Selected stable IDs for certifications.",
    )


class CoverLetterResult(BaseModel):
    """Evidence-grounded cover letter generation result."""
    letter_text: str
    strategy_used: str
    referenced_evidence_ids: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# AIService Protocol Interface
# ---------------------------------------------------------------------------

class AIService(Protocol):
    """Protocol defining LLM gateway capabilities."""

    async def extract_cv_to_evidence_bank(self, cv_text: str) -> ExtractedEvidenceBankDraft:
        """Parse raw CV text into structured Evidence Bank entities."""
        ...

    async def prescreen_job(
        self,
        candidate_summary: str,
        job_title: str,
        job_tags: List[str],
    ) -> PreScreenResult:
        """Fast high-recall filter for job relevancy."""
        ...

    async def assess_job(
        self,
        candidate_profile_text: str,
        job_details: Dict[str, Any],
    ) -> JobAssessmentResult:
        """Deep multi-dimensional compatibility assessment."""
        ...

    async def select_cv_evidence(
        self,
        job_details: Dict[str, Any],
        allowed_evidence_ids: Dict[str, List[str]],
        max_bullets_per_role: int = 4,
    ) -> CVSelectionResult:
        """Select relevant verified stable IDs without modifying bullet texts."""
        ...

    async def generate_cover_letter(
        self,
        candidate_profile_text: str,
        job_details: Dict[str, Any],
        selected_evidence_items: List[Dict[str, Any]],
        strategy: str = "direct_impact",
    ) -> CoverLetterResult:
        """Generate evidence-grounded prose for cover letter."""
        ...
