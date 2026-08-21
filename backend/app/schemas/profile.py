"""Candidate Profile and Evidence Bank Pydantic schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    experience_record_id: Optional[uuid.UUID] = None
    stable_id: str
    raw_text: str
    category: str
    variants: Optional[Dict[str, str]] = None
    is_verified: bool
    display_order: int


class ExperienceRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_name: str
    role_title: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    is_current: bool
    description: Optional[str] = None
    display_order: int
    bullets: List[EvidenceItemRead] = Field(default_factory=list)


class SkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stable_id: str
    name: str
    category: str
    proficiency: Optional[str] = None
    years_of_experience: Optional[float] = None
    is_verified: bool
    display_order: int


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stable_id: str
    title: str
    category: Optional[str] = None
    description: str
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    github_url: Optional[str] = None
    is_verified: bool
    display_order: int


class CertificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stable_id: str
    name: str
    issuing_organization: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    is_verified: bool
    display_order: int


class EducationRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stable_id: str
    institution: str
    degree: str
    field_of_study: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    activities: Optional[str] = None
    is_verified: bool
    display_order: int


class EvidenceBankRead(BaseModel):
    experiences: List[ExperienceRecordRead] = Field(default_factory=list)
    skills: List[SkillRead] = Field(default_factory=list)
    projects: List[ProjectRead] = Field(default_factory=list)
    certifications: List[CertificationRead] = Field(default_factory=list)
    education: List[EducationRecordRead] = Field(default_factory=list)


class CandidateProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: Optional[str] = None
    email: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    raw_cv_text: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    evidence_bank: Optional[EvidenceBankRead] = None


class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class EvidenceVerificationRequest(BaseModel):
    item_id: str = Field(description="Stable ID or UUID string of the evidence item")
    item_type: str = Field(default="experience_bullet", description="experience_bullet, skill, project, certification, or education")
    is_verified: bool = True


class EvidenceVerificationResponse(BaseModel):
    item_id: str
    item_type: str
    is_verified: bool
    status: str = "updated"


class EvidenceItemUpdate(BaseModel):
    raw_text: Optional[str] = None
    category: Optional[str] = None
    variants: Optional[Dict[str, str]] = None
    is_verified: Optional[bool] = None
