"""Application Tracking System (ATS) Schemas."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.job import JobRead


class ApplicationEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    event_type: str
    description: Optional[str] = None
    created_at: datetime


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    status: str
    tailored_cv_id: Optional[uuid.UUID] = None
    cover_letter_id: Optional[uuid.UUID] = None
    applied_at: Optional[datetime] = None
    salary_offered: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job: Optional[JobRead] = None
    events: List[ApplicationEventRead] = Field(default_factory=list)


class CreateApplicationRequest(BaseModel):
    job_id: uuid.UUID
    status: str = Field(default="Saved", description="'Saved', 'Applying', 'Applied', 'Interview', 'Offer', 'Rejected'")
    notes: Optional[str] = None
    tailored_cv_id: Optional[uuid.UUID] = None
    cover_letter_id: Optional[uuid.UUID] = None
    salary_offered: Optional[Decimal] = None


class UpdateApplicationStatusRequest(BaseModel):
    status: str = Field(description="New ATS stage ('Saved', 'Applying', 'Applied', 'Interview', 'Offer', 'Rejected')")


class UpdateApplicationRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    tailored_cv_id: Optional[uuid.UUID] = None
    cover_letter_id: Optional[uuid.UUID] = None
    salary_offered: Optional[Decimal] = None
