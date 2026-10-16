"""Cover Letter Pydantic Schemas."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CoverLetterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    strategy: str
    content: str
    referenced_evidence_ids: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class GenerateCoverLetterRequest(BaseModel):
    strategy: str = Field(default="Technical Depth", description="One of the 10 positioning strategies")


class UpdateCoverLetterRequest(BaseModel):
    content: str = Field(min_length=10, description="Updated cover letter content")


class PositioningStrategyInfo(BaseModel):
    id: str
    name: str
    tagline: str
    description: str
