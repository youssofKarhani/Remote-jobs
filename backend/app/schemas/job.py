"""Job and Discovery Feed Pydantic schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    sanitized_title: Optional[str] = None
    company_name: str
    location: str
    remote: bool
    url: str
    description: str
    tags: List[str] = Field(default_factory=list)
    job_types: List[str] = Field(default_factory=list)
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: Optional[str] = "EUR"
    published_at: datetime
    created_at: Optional[datetime] = None
    source_name: Optional[str] = "Arbeitnow"


class PaginationMeta(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    limit: int


class PaginatedJobsResponse(BaseModel):
    items: List[JobRead]
    pagination: PaginationMeta


class JobSyncRequest(BaseModel):
    source: str = "arbeitnow"
    force_refresh: bool = False


class JobSyncResponse(BaseModel):
    status: str
    source: str
    fetched_count: int
    new_jobs_inserted: int
    duplicates_skipped: int
