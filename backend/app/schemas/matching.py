"""Job Matching and Compatibility Assessment Schemas."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.job import JobRead


class JobAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_match_id: uuid.UUID
    skills_score: int
    experience_score: int
    seniority_score: int
    location_score: int
    language_score: int
    confidence: float
    evaluation_mode: str = "ai"
    strengths: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    matching_evidence_ids: List[str] = Field(default_factory=list)


class JobMatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    overall_score: int
    recommendation: str
    status: str
    matched_at: datetime
    job: Optional[JobRead] = None
    assessment: Optional[JobAssessmentRead] = None


class PaginatedMatchesResponse(BaseModel):
    items: List[JobMatchRead]
    total_items: int
    total_pages: int
    current_page: int
    limit: int
