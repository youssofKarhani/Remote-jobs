"""CV Ingestion and Status Pydantic schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CVUploadResponse(BaseModel):
    task_id: str
    status: str
    filename: str
    message: str
    summary: Optional[Dict[str, Any]] = None


class CVStatusResponse(BaseModel):
    task_id: str
    status: str
    progress_percent: int
    message: str
    summary: Optional[Dict[str, Any]] = None


class CVRawTextRequest(BaseModel):
    text: str = Field(min_length=10, description="Raw plaintext resume content")
    replace_existing: Optional[bool] = Field(default=None, description="Whether to replace all existing candidate evidence")



# ---------------------------------------------------------------------------
# Anonymous preview (extract-only, nothing persisted)
# ---------------------------------------------------------------------------

class CVPreviewExperience(BaseModel):
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    bullets: List[str] = Field(default_factory=list)


class CVPreviewEducation(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CVPreviewCertification(BaseModel):
    name: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None


class CVPreviewProject(BaseModel):
    title: str
    description: Optional[str] = None


class CVPreviewCounts(BaseModel):
    experiences: int = 0
    bullets: int = 0
    skills: int = 0
    projects: int = 0
    education: int = 0
    certifications: int = 0
    languages: int = 0


class CVPreview(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    experiences: List[CVPreviewExperience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[CVPreviewProject] = Field(default_factory=list)
    education: List[CVPreviewEducation] = Field(default_factory=list)
    certifications: List[CVPreviewCertification] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class CVPreviewResponse(BaseModel):
    """Result of an anonymous extraction. Nothing is stored; sign in to save."""
    filename: str
    persisted: bool = False
    preview: CVPreview
    counts: CVPreviewCounts
    parser_mode: Optional[str] = None
    degraded: Optional[bool] = None
